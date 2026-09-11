from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth import CurrentUser, require_hr_admin
from app.services.shortlisting import (
    get_shortlisting_data,
    get_shortlisted,
    get_non_shortlisted,
    save_decision,
)

from app.services.ml_predictor import predict_candidate
from app.services.ml_evaluation import evaluate_application



router = APIRouter(
    prefix="/shortlisting",
    tags=["shortlisting"],
)


class ShortlistingDecision(BaseModel):
    decision: str
    reason: str | None = None


class CandidateMLFeatures(BaseModel):
    required_skill_match: float
    preferred_skill_match: float
    total_skill_match: float
    matched_required_count: int
    matched_preferred_count: int
    experience_years: float
    project_count: int



@router.get("")
async def list_shortlisting(
    user: CurrentUser = Depends(require_hr_admin),
):
    return get_shortlisting_data()


@router.get("/shortlisted")
async def list_shortlisted(
    user: CurrentUser = Depends(require_hr_admin),
):
    return get_shortlisted()


@router.get("/non-shortlisted")
async def list_non_shortlisted(
    user: CurrentUser = Depends(require_hr_admin),
):
    return get_non_shortlisted()

@router.post("/predict")
async def predict_candidate_shortlisting(
    payload: CandidateMLFeatures,
    user: CurrentUser = Depends(require_hr_admin),
):
    """
    Predict whether a candidate should be shortlisted
    using the trained ML model.
    """

    try:

        result = predict_candidate(
            {
                "required_skill_match":
                    payload.required_skill_match,

                "preferred_skill_match":
                    payload.preferred_skill_match,

                "total_skill_match":
                    payload.total_skill_match,

                "matched_required_count":
                    payload.matched_required_count,

                "matched_preferred_count":
                    payload.matched_preferred_count,

                "experience_years":
                    payload.experience_years,

                "project_count":
                    payload.project_count,
            }
        )

        return result

    except FileNotFoundError as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"ML prediction failed: {str(e)}",
        )

@router.post("/{application_id}/evaluate")
async def evaluate_candidate(
    application_id: str,
    user: CurrentUser = Depends(require_hr_admin),
):
    try:

        result = evaluate_application(
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
            detail=f"Candidate evaluation failed: {str(e)}",
        )
     
@router.post("/{application_id}/decision")
async def make_shortlisting_decision(
    application_id: str,
    payload: ShortlistingDecision,
    user: CurrentUser = Depends(require_hr_admin),
):
    try:

        result = save_decision(
            application_id=application_id,
            decision=payload.decision,
            reason=payload.reason,
            decided_by=user.user_id,
        )

        if not result:
            raise HTTPException(
                status_code=500,
                detail="Failed to save shortlisting decision",
            )

        return result

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except HTTPException:
        raise

    except Exception as e:

        print(
            "SHORTLISTING ERROR:",
            str(e)
        )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )