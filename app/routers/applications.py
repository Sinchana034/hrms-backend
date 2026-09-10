from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile

from app.auth import CurrentUser, require_hr_admin
from app.config import get_settings
from app.database import get_service_client

from app.models.applications import (
    CURRENT_CONSENT_VERSION,
    ApplicationCreate,
    ApplicationOut,
    ResumeSignedUrlOut,
    ResumeUploadOut,
    WithdrawRequest,
)

from app.services.application_intake import create_application
from app.services.resume_matcher import evaluate_application
from app.services.audit import write_audit_log
from app.services.captcha import verify_captcha
from app.services.rate_limit import check_email_rate_limit, limiter
from app.services.storage import (
    ResumeUploadError,
    get_resume_signed_url,
    upload_resume,
)


router = APIRouter(prefix="/applications", tags=["applications"])


# ============================================================
# PUBLIC - RESUME UPLOAD
# ============================================================

@router.post(
    "/resume-upload",
    response_model=ResumeUploadOut,
    status_code=201,
)
@limiter.limit("10/minute")
async def upload_resume_file(
    request: Request,
    file: UploadFile = File(...),
    captcha_token: str = Form(...),
):

    if not captcha_token:
        raise HTTPException(
            status_code=400,
            detail="CAPTCHA verification required.",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Resume file is empty.",
        )

    try:
        storage_path = upload_resume(
            content,
            file.content_type,
        )

    except ResumeUploadError as e:
        raise HTTPException(
            status_code=422,
            detail=str(e),
        )

    # ✅ ADD THIS
    return {
    "resume_path": storage_path
    }
# ============================================================
# PUBLIC - SUBMIT APPLICATION
# ============================================================

@router.post(
    "",
    response_model=ApplicationOut,
    status_code=201,
)
@limiter.limit("5/minute")
async def submit_application(
    request: Request,
    payload: ApplicationCreate,
):
    """
    Public candidate application endpoint.

    Protected by:
    - CAPTCHA
    - IP rate limiting
    - Email rate limiting
    - Consent validation
    """

    # --------------------------------------------------------
    # Consent
    # --------------------------------------------------------

    if not payload.consent_given:
        raise HTTPException(
            status_code=422,
            detail="Consent checkbox must be accepted.",
        )

    # --------------------------------------------------------
    # Client IP
    # --------------------------------------------------------

    client_ip = (
        request.client.host
        if request.client
        else None
    )

    # --------------------------------------------------------
    # CAPTCHA
    # --------------------------------------------------------

    captcha_ok = await verify_captcha(
        payload.captcha_token,
        remote_ip=client_ip,
    )

    if not captcha_ok:
        raise HTTPException(
            status_code=400,
            detail="CAPTCHA verification failed.",
        )

    # --------------------------------------------------------
    # Email rate limiting
    # --------------------------------------------------------

    if not check_email_rate_limit(payload.email):
        raise HTTPException(
            status_code=429,
            detail=(
                "Too many applications submitted from this "
                "email address. Try again later."
            ),
        )

    # --------------------------------------------------------
    # Prepare Supabase row
    # --------------------------------------------------------

    row = {
        "candidate_name": payload.candidate_name.strip(),
        "email": payload.email.strip().lower(),
        "phone": payload.phone,
        "department": payload.department.strip(),
        "position": payload.position.strip(),

        "source": "WEBSITE",

        # Resume storage path
        "resume_url": payload.resume_url,

        # Candidate information used by matcher
        "education": payload.education or [],
        "skills": payload.skills or [],
        "experience": payload.experience or [],
        "projects": payload.projects or [],

        # Links
        "portfolio": payload.portfolio,
        "github": payload.github,
        "linkedin": payload.linkedin,

        # Initial status
        "current_status": "Application Received",

        # Consent
        "consent_version": CURRENT_CONSENT_VERSION,
    }

    # --------------------------------------------------------
    # Insert application
    # --------------------------------------------------------

    try:
        created = create_application(row)

    except RuntimeError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create application: {str(e)}",
        )

    return created


# ============================================================
# HR - LIST APPLICATIONS
# ============================================================

@router.get(
    "",
    response_model=list[ApplicationOut],
)
async def list_applications(
    status: str | None = None,
    department: str | None = None,
    position: str | None = None,
    source: str | None = None,
    email_bounced: bool | None = None,
    limit: int = 50,
    offset: int = 0,
    user: CurrentUser = Depends(require_hr_admin),
):
    """
    HR-only application listing.
    """

    # Protect pagination values
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="limit must be between 1 and 100.",
        )

    if offset < 0:
        raise HTTPException(
            status_code=400,
            detail="offset cannot be negative.",
        )

    client = get_service_client()

    query = (
        client
        .table("applications")
        .select("*")
    )

    if status:
        query = query.eq(
            "current_status",
            status,
        )

    if department:
        query = query.eq(
            "department",
            department,
        )

    if position:
        query = query.eq(
            "position",
            position,
        )

    if source:
        query = query.eq(
            "source",
            source,
        )

    if email_bounced is not None:
        query = query.eq(
            "email_bounced",
            email_bounced,
        )

    query = (
        query
        .order(
            "application_date",
            desc=True,
        )
        .range(
            offset,
            offset + limit - 1,
        )
    )

    result = query.execute()

    return result.data or []


# ============================================================
# HR - GET SINGLE APPLICATION
# ============================================================

@router.get(
    "/{application_id}",
    response_model=ApplicationOut,
)
async def get_application(
    application_id: str,
    user: CurrentUser = Depends(require_hr_admin),
):
    client = get_service_client()

    result = (
        client
        .table("applications")
        .select("*")
        .eq(
            "application_id",
            application_id,
        )
        .single()
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=404,
            detail="Application not found.",
        )

    return result.data


# ============================================================
# HR - EVALUATE APPLICATION
# ============================================================
# ---------------------------------------------------------------------------
# HR: evaluate application against job requirements
# ---------------------------------------------------------------------------
@router.post("/{application_id}/evaluate")
async def evaluate_application_match(
    application_id: str,
    user: CurrentUser = Depends(require_hr_admin),
):
    """
    Evaluate an application against the requirements for its position.

    Returns:
    - evaluation_id
    - application_id
    - requirement_id
    - matching_score
    - matching_skills
    - missing_skills
    - matched_required_skills
    - matched_preferred_skills
    """
    try:
        evaluation = evaluate_application(application_id)

        if not evaluation:
            raise HTTPException(
                status_code=404,
                detail="Unable to evaluate application",
            )

        return evaluation

    except HTTPException:
        raise

    except RuntimeError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except Exception as e:
        import traceback

        print("\n========== EVALUATION ERROR ==========")
        traceback.print_exc()
        print("======================================\n")

        raise HTTPException(
            status_code=500,
            detail=str(e),
    )

# ============================================================
# HR - GET RESUME SIGNED URL
# ============================================================

@router.get(
    "/{application_id}/resume-url",
    response_model=ResumeSignedUrlOut,
)
async def get_application_resume_url(
    application_id: str,
    user: CurrentUser = Depends(require_hr_admin),
):
    client = get_service_client()

    existing = (
        client
        .table("applications")
        .select(
            "resume_url,candidate_id"
        )
        .eq(
            "application_id",
            application_id,
        )
        .single()
        .execute()
    )

    if not existing.data:
        raise HTTPException(
            status_code=404,
            detail="Application not found.",
        )

    resume_url = existing.data.get(
        "resume_url"
    )

    if not resume_url:
        raise HTTPException(
            status_code=404,
            detail="No resume on file for this application.",
        )

    settings = get_settings()

    try:
        url = get_resume_signed_url(
            resume_url
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate resume URL: {str(e)}",
        )

    # Audit resume access
    write_audit_log(
        action="resume_viewed",
        role="hr",
        hr_user=user.user_id,
        candidate_id=existing.data.get(
            "candidate_id"
        ),
        metadata={
            "application_id": application_id
        },
    )

    return {
        "url": url,
        "expires_in_seconds": (
            settings.resume_signed_url_ttl_seconds
        ),
    }


# ============================================================
# HR - WITHDRAW APPLICATION
# ============================================================

@router.post(
    "/{application_id}/withdraw",
    response_model=ApplicationOut,
)
async def withdraw_application(
    application_id: str,
    payload: WithdrawRequest,
    user: CurrentUser = Depends(require_hr_admin),
):
    client = get_service_client()

    existing = (
        client
        .table("applications")
        .select("*")
        .eq(
            "application_id",
            application_id,
        )
        .single()
        .execute()
    )

    if not existing.data:
        raise HTTPException(
            status_code=404,
            detail="Application not found.",
        )

    previous_status = existing.data[
        "current_status"
    ]

    result = (
        client
        .table("applications")
        .update(
            {
                "current_status": "Withdrawn",
                "withdrawn_at": (
                    datetime
                    .now(timezone.utc)
                    .isoformat()
                ),
            }
        )
        .eq(
            "application_id",
            application_id,
        )
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to withdraw application.",
        )

    # Audit withdrawal
    write_audit_log(
        action="application_withdrawn",
        role="hr",
        hr_user=user.user_id,
        candidate_id=existing.data.get(
            "candidate_id"
        ),
        previous_status=previous_status,
        new_status="Withdrawn",
        metadata=(
            {"reason": payload.reason}
            if payload.reason
            else None
        ),
    )

    return result.data[0]