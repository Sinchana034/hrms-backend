from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.auth import CurrentUser, require_hr_admin
from app.database import get_service_client
from app.models.duplicates import DuplicateCandidateOut, ResolveDuplicateRequest
from app.services.audit import write_audit_log
from app.services.duplicate_detection import run_duplicate_check

router = APIRouter(tags=["duplicates"])


# ---------------------------------------------------------------------------
# HR: manually (re-)run duplicate detection for one application
# (Section 13: POST /applications/{id}/duplicate-check)
# ---------------------------------------------------------------------------
@router.post("/applications/{application_id}/duplicate-check")
async def trigger_duplicate_check(
    application_id: str, user: CurrentUser = Depends(require_hr_admin)
):
    client = get_service_client()
    existing = client.table("applications").select("*").eq("application_id", application_id).single().execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Application not found")

    created = run_duplicate_check(existing.data)
    return {"new_matches_found": len(created)}


# ---------------------------------------------------------------------------
# HR: list pending duplicate flags for review (Section 6.3, Section 25
# "Applications (All / Website / Email / Withdrawn)" dashboard area)
# ---------------------------------------------------------------------------
@router.get("/duplicates", response_model=list[DuplicateCandidateOut])
async def list_duplicates(
    status: str = "pending", user: CurrentUser = Depends(require_hr_admin)
):
    client = get_service_client()
    query = client.table("duplicate_candidates").select("*")
    if status:
        query = query.eq("status", status)
    rows = query.order("created_at", desc=True).execute().data

    if not rows:
        return []

    app_ids = {r["application_id"] for r in rows} | {r["matched_application_id"] for r in rows}
    apps = (
        client.table("applications")
        .select("application_id,candidate_name,email,phone,current_status")
        .in_("application_id", list(app_ids))
        .execute()
        .data
    )
    apps_by_id = {a["application_id"]: a for a in apps}

    out = []
    for r in rows:
        app = apps_by_id.get(r["application_id"])
        matched = apps_by_id.get(r["matched_application_id"])
        if not app or not matched:
            continue  # defensive: shouldn't happen, FK cascade keeps these in sync
        out.append(
            {
                "duplicate_id": r["duplicate_id"],
                "application": app,
                "matched_application": matched,
                "match_type": r["match_type"],
                "match_score": r["match_score"],
                "status": r["status"],
                "resolution": r["resolution"],
                "created_at": r["created_at"],
            }
        )
    return out


# ---------------------------------------------------------------------------
# HR: resolve a duplicate flag — Merge / Keep Separate / Mark as Duplicate.
# No automatic deletion, ever (Section 6.3).
# ---------------------------------------------------------------------------
@router.post("/duplicates/{duplicate_id}/resolve")
async def resolve_duplicate(
    duplicate_id: str,
    payload: ResolveDuplicateRequest,
    user: CurrentUser = Depends(require_hr_admin),
):
    client = get_service_client()
    existing = (
        client.table("duplicate_candidates").select("*").eq("duplicate_id", duplicate_id).single().execute()
    )
    if not existing.data:
        raise HTTPException(status_code=404, detail="Duplicate flag not found")

    row = existing.data
    pair = {row["application_id"], row["matched_application_id"]}

    if payload.canonical_application_id and str(payload.canonical_application_id) not in pair:
        raise HTTPException(
            status_code=422,
            detail="canonical_application_id must be one of the two applications in this pair",
        )

    if payload.resolution in ("merge", "mark_duplicate"):
        canonical_id = str(payload.canonical_application_id)
        duplicate_app_id = next(iter(pair - {canonical_id}))

        # NOTE: 'merge' currently has the same effect as 'mark_duplicate' —
        # it flags the non-canonical record and points duplicate_of at the
        # canonical one. There's no child data (assessments/interviews) to
        # actually reconcile yet since those land in Phase 4+; once they
        # exist, 'merge' should additionally re-point any child records
        # from the duplicate onto the canonical application before this
        # write. Tracked as a follow-up, not silently skipped.
        client.table("applications").update({"duplicate_of": canonical_id}).eq(
            "application_id", duplicate_app_id
        ).execute()

    client.table("duplicate_candidates").update(
        {
            "status": "resolved",
            "resolution": payload.resolution,
            "resolved_by": user.user_id,
            "resolved_at": datetime.now(timezone.utc).isoformat(),
        }
    ).eq("duplicate_id", duplicate_id).execute()

    write_audit_log(
        action="duplicate_resolved",
        role="hr",
        hr_user=user.user_id,
        metadata={
            "duplicate_id": duplicate_id,
            "resolution": payload.resolution,
            "canonical_application_id": str(payload.canonical_application_id)
            if payload.canonical_application_id
            else None,
        },
    )

    return {"status": "resolved", "resolution": payload.resolution}
