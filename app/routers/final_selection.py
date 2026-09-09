from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth import CurrentUser, require_hr_admin

from app.services.final_selection_service import (
    calculate_final_selection,
    get_final_selection,
    get_selected_candidates,
    get_rejected_candidates,
)

router = APIRouter(
    prefix="/final-selection",
    tags=["final-selection"],
)


# =========================================================
# REQUEST MODEL
# =========================================================

class FinalSelectionScores(BaseModel):

    ai_interview_score: float = Field(
        ...,
        ge=0,
        le=100,
    )

    hr_interview_score: float = Field(
        ...,
        ge=0,
        le=100,
    )


# =========================================================
# CALCULATE FINAL SELECTION
# =========================================================

@router.post("/{application_id}/calculate")
async def calculate_candidate_final_selection(
    application_id: str,
    scores: FinalSelectionScores,
    user: CurrentUser = Depends(
        require_hr_admin
    ),
):

    try:

        result = calculate_final_selection(
            application_id=application_id,

            ai_interview_score=(
                scores.ai_interview_score
            ),

            hr_interview_score=(
                scores.hr_interview_score
            ),
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
                "Failed to calculate final selection: "
                f"{str(e)}"
            ),
        )

# =========================================================
# GET SELECTED CANDIDATES
# =========================================================

@router.get("/selected-candidates")
async def get_all_selected_candidates(
    user: CurrentUser = Depends(
        require_hr_admin
    ),
):

    try:

        return get_selected_candidates()

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to load selected candidates: "
                f"{str(e)}"
            ),
        )


# =========================================================
# GET REJECTED CANDIDATES
# =========================================================

@router.get("/rejected-candidates")
async def get_all_rejected_candidates(
    user: CurrentUser = Depends(
        require_hr_admin
    ),
):

    try:

        return get_rejected_candidates()

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to load rejected candidates: "
                f"{str(e)}"
            ),
        )
# =========================================================
# GET FINAL SELECTION
# =========================================================

@router.get("/{application_id}")
async def get_candidate_final_selection(
    application_id: str,
    user: CurrentUser = Depends(
        require_hr_admin
    ),
):

    try:

        return get_final_selection(
            application_id
        )

    except RuntimeError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to load final selection: "
                f"{str(e)}"
            ),
        )