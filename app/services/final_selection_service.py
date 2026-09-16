from app.database import get_service_client
from app.services.candidate_notification import send_candidate_notification


# =========================================================
# FINAL SELECTION
# =========================================================

def calculate_final_selection(
    application_id: str,
    ai_interview_score: float,
    hr_interview_score: float,
):
    """
    Calculate final candidate selection using:

    Resume Score        -> 25%
    Assessment Score    -> 25%
    AI Interview Score  -> 25%
    HR Interview Score  -> 25%

    For the current submission, AI Interview and HR Interview
    scores are manually entered by HR.
    """

    client = get_service_client()

    # -----------------------------------------------------
    # Validate manually entered scores
    # -----------------------------------------------------

    if not 0 <= ai_interview_score <= 100:
        raise RuntimeError(
            "AI Interview score must be between 0 and 100"
        )

    if not 0 <= hr_interview_score <= 100:
        raise RuntimeError(
            "HR Interview score must be between 0 and 100"
        )

    # -----------------------------------------------------
    # Check application
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
            application_id
        )
        .single()
        .execute()
    )

    application = application_result.data

    if not application:
        raise RuntimeError(
            "Application not found"
        )

    # -----------------------------------------------------
    # Get Resume / ML Score
    # -----------------------------------------------------

    evaluation_result = (
    client
    .table("ml_evaluations")
    .select(
        "matching_score"
    )
    .eq(
        "application_id",
        application_id
    )
    .limit(1)
    .execute()
)

    evaluation = (
        evaluation_result.data[0]
        if evaluation_result.data
        else None
    )

    if evaluation:
        resume_score = float(
            evaluation.get("matching_score") or 0
        )
    else:
        # Candidate has no resume / ML evaluation.
        # Treat the resume component as 0 and
        # allow the remaining recruitment stages
        # to determine the final score.
        resume_score = 0.0
    # -----------------------------------------------------
    # Get Assessment Score
    # -----------------------------------------------------

    assessment_result = (
        client
        .table("assessments")
        .select(
            "score,"
            "result,"
            "status"
        )
        .eq(
            "application_id",
            application_id
        )
        .order(
            "created_at",
            desc=True
        )
        .limit(1)
        .execute()
    )

    if not assessment_result.data:
        raise RuntimeError(
            "Assessment not found"
        )

    assessment = assessment_result.data[0]

    if assessment["status"] != "Completed":
        raise RuntimeError(
            "Assessment has not been completed"
        )

    assessment_score = float(
        assessment.get("score") or 0
    )

    # -----------------------------------------------------
    # Final Score
    # -----------------------------------------------------

    final_score = (
        resume_score * 0.25
        + assessment_score * 0.25
        + ai_interview_score * 0.25
        + hr_interview_score * 0.25
    )

    final_score = round(
        final_score,
        2
    )

    # -----------------------------------------------------
    # Final ML Prediction
    #
    # Current submission model:
    # score >= 70 -> Selected
    # score < 70  -> Rejected
    #
    # We will replace this with a trained ML classifier
    # after the complete workflow is working.
    # -----------------------------------------------------

    if final_score >= 70:
        prediction = "Selected"
    else:
        prediction = "Rejected"

    # -----------------------------------------------------
    # Save final selection
    # -----------------------------------------------------

    selection_data = {
        "application_id": application_id,

        "resume_score": round(
            resume_score,
            2
        ),

        "assessment_score": round(
            assessment_score,
            2
        ),

        "ai_interview_score": round(
            ai_interview_score,
            2
        ),

        "hr_interview_score": round(
            hr_interview_score,
            2
        ),

        "final_score": final_score,

        "prediction": prediction,
    }

    result = (
        client
        .table("final_selections")
        .upsert(
            selection_data,
            on_conflict="application_id"
        )
        .execute()
    )

    if not result.data:
        raise RuntimeError(
            "Failed to save final selection"
        )

    # -----------------------------------------------------
    # Notify candidate of final decision
    #
    # This was previously missing entirely — the final
    # selection was saved to the DB but no email was ever
    # sent, unlike the shortlisting stage which already does
    # this. A send failure must not undo the saved decision.
    # -----------------------------------------------------

    if prediction == "Selected":

        subject = (
            f"Congratulations - {application['position']}"
        )

        body = (
            "Congratulations!\n\n"
            "We are pleased to inform you that you have been "
            "selected for this position.\n\n"
            "Our HR team will be in touch shortly with your "
            "offer letter and next steps."
        )

    else:

        subject = (
            f"Application Update - {application['position']}"
        )

        body = (
            "Thank you for completing our full recruitment "
            "process.\n\n"
            "After careful consideration, we will not be moving "
            "forward with your application at this time.\n\n"
            "We appreciate the time and effort you invested and "
            "wish you the best in your future opportunities."
        )

    notification_sent = False
    notification_error = None

    try:
        send_candidate_notification(
            candidate_name=application["candidate_name"],
            candidate_email=application["email"],
            position=application["position"],
            subject=subject,
            body=body,
        )
        notification_sent = True

    except Exception as exc:
        notification_error = str(exc)
        print("Final decision notification email failed:", notification_error)

    return {
        "message": "Final selection calculated successfully",

        "candidate_name":
            application["candidate_name"],

        "candidate_email":
            application["email"],

        "position":
            application["position"],

        "scores": {
            "resume_score":
                round(resume_score, 2),

            "assessment_score":
                round(assessment_score, 2),

            "ai_interview_score":
                round(ai_interview_score, 2),

            "hr_interview_score":
                round(hr_interview_score, 2),
        },

        "final_score":
            final_score,

        "prediction":
            prediction,

        "selection":
            result.data[0],

        "notification_sent":
            notification_sent,

        "notification_error":
            notification_error,
    }


# =========================================================
# GET FINAL SELECTION
# =========================================================

# =========================================================
# GET FINAL CANDIDATES BY PREDICTION
# =========================================================

def get_final_candidates(prediction: str):
    """
    Get candidates based on final selection prediction.

    prediction:
        Selected
        Rejected
    """

    client = get_service_client()

    # -----------------------------------------------------
    # Get final selections
    # -----------------------------------------------------

    result = (
        client
        .table("final_selections")
        .select(
            "application_id,"
            "resume_score,"
            "assessment_score,"
            "ai_interview_score,"
            "hr_interview_score,"
            "final_score,"
            "prediction"
        )
        .eq(
            "prediction",
            prediction
        )
        .order(
            "final_score",
            desc=True
        )
        .execute()
    )

    selections = result.data

    if not selections:
        return []

    candidates = []

    # -----------------------------------------------------
    # Get application details
    # -----------------------------------------------------

    for selection in selections:

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
                selection["application_id"]
            )
            .single()
            .execute()
        )

        application = application_result.data

        if application:

            candidates.append(
                {
                    "application_id":
                        application["application_id"],

                    "candidate_name":
                        application["candidate_name"],

                    "email":
                        application["email"],

                    "position":
                        application["position"],

                    "current_status":
                        application["current_status"],

                    "resume_score":
                        selection["resume_score"],

                    "assessment_score":
                        selection["assessment_score"],

                    "ai_interview_score":
                        selection["ai_interview_score"],

                    "hr_interview_score":
                        selection["hr_interview_score"],

                    "final_score":
                        selection["final_score"],

                    "prediction":
                        selection["prediction"],
                }
            )

    return candidates
# =========================================================
# GET SELECTED CANDIDATES
# =========================================================

def get_selected_candidates():
    """
    Get all candidates whose final selection
    prediction is Selected.
    """

    client = get_service_client()

    # -----------------------------------------------------
    # Get selected final selections
    # -----------------------------------------------------

    result = (
        client
        .table("final_selections")
        .select(
            "application_id,"
            "resume_score,"
            "assessment_score,"
            "ai_interview_score,"
            "hr_interview_score,"
            "final_score,"
            "prediction"
        )
        .eq(
            "prediction",
            "Selected"
        )
        .order(
            "final_score",
            desc=True
        )
        .execute()
    )

    selections = result.data

    if not selections:
        return []

    selected_candidates = []

    # -----------------------------------------------------
    # Get application details
    # -----------------------------------------------------

    for selection in selections:

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
                selection["application_id"]
            )
            .single()
            .execute()
        )

        application = application_result.data

        if application:

            selected_candidates.append(
                {
                    "application_id":
                        application["application_id"],

                    "candidate_name":
                        application["candidate_name"],

                    "email":
                        application["email"],

                    "position":
                        application["position"],

                    "final_score":
                        selection["final_score"],

                    "prediction":
                        selection["prediction"],

                    "resume_score":
                        selection["resume_score"],

                    "assessment_score":
                        selection["assessment_score"],

                    "ai_interview_score":
                        selection["ai_interview_score"],

                    "hr_interview_score":
                        selection["hr_interview_score"],
                }
            )

    return selected_candidates


# =========================================================
# GET REJECTED CANDIDATES
# =========================================================

def get_rejected_candidates():
    """
    Get all candidates whose final selection
    prediction is Rejected.
    """

    client = get_service_client()

    # -----------------------------------------------------
    # Get rejected final selections
    # -----------------------------------------------------

    result = (
        client
        .table("final_selections")
        .select(
            "application_id,"
            "resume_score,"
            "assessment_score,"
            "ai_interview_score,"
            "hr_interview_score,"
            "final_score,"
            "prediction"
        )
        .eq(
            "prediction",
            "Rejected"
        )
        .order(
            "final_score",
            desc=True
        )
        .execute()
    )

    selections = result.data

    if not selections:
        return []

    rejected_candidates = []

    # -----------------------------------------------------
    # Get application details
    # -----------------------------------------------------

    for selection in selections:

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
                selection["application_id"]
            )
            .single()
            .execute()
        )

        application = application_result.data

        if application:

            rejected_candidates.append(
                {
                    "application_id":
                        application["application_id"],

                    "candidate_name":
                        application["candidate_name"],

                    "email":
                        application["email"],

                    "position":
                        application["position"],

                    "final_score":
                        selection["final_score"],

                    "prediction":
                        selection["prediction"],

                    "resume_score":
                        selection["resume_score"],

                    "assessment_score":
                        selection["assessment_score"],

                    "ai_interview_score":
                        selection["ai_interview_score"],

                    "hr_interview_score":
                        selection["hr_interview_score"],
                }
            )

    return rejected_candidates

# =========================================================
# GET FINAL SELECTION
# =========================================================

def get_final_selection(application_id: str):
    """
    Get the final selection result for a candidate.
    """

    client = get_service_client()

    result = (
        client
        .table("final_selections")
        .select("*")
        .eq(
            "application_id",
            application_id
        )
        .single()
        .execute()
    )

    if not result.data:
        raise RuntimeError(
            "Final selection not found"
        )

    return result.data[0]