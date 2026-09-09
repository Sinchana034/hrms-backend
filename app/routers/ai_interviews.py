from fastapi import APIRouter, Depends, HTTPException

from app.auth import CurrentUser, require_hr_admin
from app.services.ai_interview_service import create_ai_interview


router = APIRouter(
    prefix="/ai-interviews",
    tags=["ai-interviews"],
)


# =========================================================
# HR — CREATE AI INTERVIEW
# =========================================================

@router.post("/{application_id}/create")
async def create_candidate_ai_interview(
    application_id: str,
    user: CurrentUser = Depends(require_hr_admin),
):

    try:

        result = create_ai_interview(
            application_id
        )

        return result

    except RuntimeError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to create AI interview: "
                f"{str(e)}"
            ),
        )