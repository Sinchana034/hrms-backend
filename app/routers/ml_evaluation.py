from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth import CurrentUser, require_hr_admin
from app.services.ml_predictor import predict_candidate


router = APIRouter(
    prefix="/ml-evaluation",
    tags=["ML Evaluation"],
)


# =========================================================
# REQUEST MODEL
# =========================================================

class CandidateFeatures(BaseModel):

    required_skill_match: float = Field(..., ge=0, le=100)

    preferred_skill_match: float = Field(..., ge=0, le=100)

    total_skill_match: float = Field(..., ge=0, le=100)

    matched_required_count: int = Field(..., ge=0)

    matched_preferred_count: int = Field(..., ge=0)

    experience_years: int = Field(..., ge=0)

    project_count: int = Field(..., ge=0)


# =========================================================
# ML PREDICTION ENDPOINT
# =========================================================

@router.post("/predict")
async def predict_candidate_shortlisting(
    data: CandidateFeatures,
    user: CurrentUser = Depends(require_hr_admin),
):

    try:

        result = predict_candidate(
            data.model_dump()
        )

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"ML prediction failed: {str(e)}",
        )