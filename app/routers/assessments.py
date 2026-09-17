from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth import CurrentUser, require_hr_admin

from app.services.assessment_service import (
    create_assessment,
    get_assessment_by_token,
    submit_assessment,
    get_assessment_result,
    record_violation,
    save_assessment_answer,
    handle_tab_close,
)

router = APIRouter(
    prefix="/assessments",
    tags=["assessments"],
)


# =========================================================
# HR — CREATE ASSESSMENT
# =========================================================

@router.post("/{application_id}/create")
async def create_candidate_assessment(
    application_id: str,
    user: CurrentUser = Depends(require_hr_admin),
):

    try:

        result = create_assessment(
            application_id
        )

        return {
            "message": "Assessment created successfully",

            "assessment_id": (
                result["assessment"][
                    "assessment_id"
                ]
            ),

            "candidate_name": (
                result["candidate_name"]
            ),

            "candidate_email": (
                result["candidate_email"]
            ),

            "assessment_url": (
                result["assessment_url"]
            ),

            "expires_at": (
                result["expires_at"]
            ),
        }

    except RuntimeError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to create assessment: "
                f"{str(e)}"
            ),
        )

# =========================================================
# HR — GET ASSESSMENT RESULT
# =========================================================

@router.get("/{application_id}/result")
async def get_candidate_assessment_result(
    application_id: str,
    user: CurrentUser = Depends(require_hr_admin),
):

    try:

        result = get_assessment_result(
            application_id
        )

        return result

    except RuntimeError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to load assessment result: "
                f"{str(e)}"
            ),
        )
    

# =========================================================
# CANDIDATE — GET ASSESSMENT
# =========================================================

@router.get("/access/{token}")
async def get_candidate_assessment(
    token: str,
):

    try:

        result = get_assessment_by_token(
            token
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
                "Failed to load assessment: "
                f"{str(e)}"
            ),
        )
    
# =========================================================
# CANDIDATE — SUBMIT ASSESSMENT
# =========================================================

class AssessmentSubmission(BaseModel):
    answers: list[str | None]
    terminated_reason: str | None = None

class AssessmentAnswer(BaseModel):
    question_index: int
    selected_option: str | None = None


@router.post("/access/{token}/submit")
async def submit_candidate_assessment(
    token: str,
    submission: AssessmentSubmission,
):

    try:

        result = submit_assessment(
            token=token,
            answers=submission.answers,
            terminated_reason=submission.terminated_reason,
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
                "Failed to submit assessment: "
                f"{str(e)}"
            ),
        )


# =========================================================
# CANDIDATE — SAVE ASSESSMENT ANSWER
# =========================================================

@router.post("/access/{token}/answer")
async def save_candidate_assessment_answer(
    token: str,
    answer: AssessmentAnswer,
):

    try:

        result = save_assessment_answer(
            token=token,
            question_index=answer.question_index,
            selected_option=answer.selected_option,
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
                "Failed to save assessment answer: "
                f"{str(e)}"
            ),
        )

# =========================================================
# CANDIDATE — HANDLE TAB CLOSE
# =========================================================

@router.post("/access/{token}/tab-close")
async def candidate_tab_close(
    token: str,
):

    try:

        result = handle_tab_close(
            token=token,
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
                "Failed to handle tab close: "
                f"{str(e)}"
            ),
        )
# =========================================================
# CANDIDATE — RECORD PROCTORING VIOLATION
# =========================================================

class ViolationReport(BaseModel):
    violation_type: str


@router.post("/access/{token}/violation")
async def report_assessment_violation(
    token: str,
    report: ViolationReport,
):

    try:

        result = record_violation(
            token=token,
            violation_type=report.violation_type,
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
                "Failed to record violation: "
                f"{str(e)}"
            ),
        )