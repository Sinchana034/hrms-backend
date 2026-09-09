from fastapi import APIRouter, Depends, HTTPException

from app.auth import CurrentUser, require_hr_admin
from app.database import get_service_client

from app.models.interviews import (
    InterviewCreate,
    InterviewUpdate,
)


router = APIRouter(
    prefix="/interviews",
    tags=["interviews"],
)


# =========================================================
# LIST INTERVIEWS
# =========================================================

@router.get("")
async def list_interviews(
    user: CurrentUser = Depends(require_hr_admin),
):
    client = get_service_client()

    result = (
        client
        .table("interviews")
        .select("*")
        .order("scheduled_at", desc=False)
        .execute()
    )

    return result.data or []


# =========================================================
# GET INTERVIEW
# =========================================================

@router.get("/{interview_id}")
async def get_interview(
    interview_id: str,
    user: CurrentUser = Depends(require_hr_admin),
):
    client = get_service_client()

    result = (
        client
        .table("interviews")
        .select("*")
        .eq("interview_id", interview_id)
        .single()
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=404,
            detail="Interview not found",
        )

    return result.data


# =========================================================
# GET INTERVIEWS FOR APPLICATION
# =========================================================

@router.get("/application/{application_id}")
async def get_application_interviews(
    application_id: str,
    user: CurrentUser = Depends(require_hr_admin),
):
    client = get_service_client()

    result = (
        client
        .table("interviews")
        .select("*")
        .eq("application_id", application_id)
        .order("scheduled_at", desc=False)
        .execute()
    )

    return result.data or []


# =========================================================
# CREATE INTERVIEW
# =========================================================

@router.post("")
async def create_interview(
    interview: InterviewCreate,
    user: CurrentUser = Depends(require_hr_admin),
):
    client = get_service_client()

    # -----------------------------------------------------
    # Verify application exists
    # -----------------------------------------------------

    application_result = (
        client
        .table("applications")
        .select(
            "application_id,"
            "candidate_name,"
            "email,"
            "position,"
            "current_status"
        )
        .eq(
            "application_id",
            str(interview.application_id),
        )
        .single()
        .execute()
    )

    application = application_result.data

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    # -----------------------------------------------------
    # Create interview
    # -----------------------------------------------------

    result = (
        client
        .table("interviews")
        .insert({
            "application_id": str(interview.application_id),
            "interview_type": interview.interview_type,
            "interviewer_name": interview.interviewer_name,
            "interviewer_email": interview.interviewer_email,
            "scheduled_at": (
                interview.scheduled_at.isoformat()
                if interview.scheduled_at
                else None
            ),
            "duration_minutes": interview.duration_minutes,
            "meeting_link": interview.meeting_link,
            "status": "Scheduled",
            "notes": interview.notes,
        })
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to create interview",
        )

    return {
        "message": "Interview created successfully",
        "interview": result.data[0],
        "candidate_name": application["candidate_name"],
        "candidate_email": application["email"],
        "position": application["position"],
    }


# =========================================================
# UPDATE INTERVIEW
# =========================================================

@router.put("/{interview_id}")
async def update_interview(
    interview_id: str,
    interview: InterviewUpdate,
    user: CurrentUser = Depends(require_hr_admin),
):
    client = get_service_client()

    update_data = interview.model_dump(
        exclude_unset=True
    )

    if "scheduled_at" in update_data:
        if update_data["scheduled_at"]:
            update_data["scheduled_at"] = (
                update_data["scheduled_at"].isoformat()
            )

    update_data["updated_at"] = "now()"

    # Don't send literal SQL expression through
    # Supabase client.
    update_data.pop("updated_at", None)

    result = (
        client
        .table("interviews")
        .update(update_data)
        .eq("interview_id", interview_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=404,
            detail="Interview not found",
        )

    return {
        "message": "Interview updated successfully",
        "interview": result.data[0],
    }


# =========================================================
# DELETE / CANCEL INTERVIEW
# =========================================================

@router.delete("/{interview_id}")
async def cancel_interview(
    interview_id: str,
    user: CurrentUser = Depends(require_hr_admin),
):
    client = get_service_client()

    result = (
        client
        .table("interviews")
        .update({
            "status": "Cancelled",
        })
        .eq("interview_id", interview_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=404,
            detail="Interview not found",
        )

    return {
        "message": "Interview cancelled successfully",
        "interview": result.data[0],
    }