import os
import joblib
import pandas as pd

from app.database import get_service_client
from app.services.candidate_notification import send_candidate_notification


# ---------------------------------------------------------
# ML MODEL CONFIGURATION
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "ml",
    "models",
    "candidate_shortlisting_model.pkl"
)

FEATURE_PATH = os.path.join(
    BASE_DIR,
    "ml",
    "models",
    "features.pkl"
)

def load_ml_model():
    """
    Load the trained candidate shortlisting model
    and its feature names.
    """

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"ML model not found at: {MODEL_PATH}"
        )

    if not os.path.exists(FEATURE_PATH):
        raise FileNotFoundError(
            f"Feature file not found at: {FEATURE_PATH}"
        )

    model = joblib.load(MODEL_PATH)

    features = joblib.load(FEATURE_PATH)

    return model, features

def predict_shortlisting(
    required_skill_match: float,
    preferred_skill_match: float,
    total_skill_match: float,
    matched_required_count: int,
    matched_preferred_count: int,
    experience_years: float,
    project_count: int,
):
    """
    Predict whether a candidate should be shortlisted
    using the trained ML model.
    """

    model, features = load_ml_model()

    input_data = pd.DataFrame(
        [[
            required_skill_match,
            preferred_skill_match,
            total_skill_match,
            matched_required_count,
            matched_preferred_count,
            experience_years,
            project_count,
        ]],
        columns=features
    )

    prediction = model.predict(input_data)[0]

    probability = model.predict_proba(
        input_data
    )[0]

    return {
        "prediction": int(prediction),
        "prediction_label": (
            "shortlisted"
            if prediction == 1
            else "non_shortlisted"
        ),
        "shortlist_probability": round(
            float(probability[1]) * 100,
            2
        ),
        "features_used": {
            "required_skill_match":
                required_skill_match,

            "preferred_skill_match":
                preferred_skill_match,

            "total_skill_match":
                total_skill_match,

            "matched_required_count":
                matched_required_count,

            "matched_preferred_count":
                matched_preferred_count,

            "experience_years":
                experience_years,

            "project_count":
                project_count,
        }
    }

def get_shortlisting_data():
    """
    Get applications together with:
    - ML evaluation
    - job requirement
    - existing HR decision
    - shortlisting eligibility
    """

    client = get_service_client()

    applications = (
        client.table("applications")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    if not applications.data:
        return []

    evaluations = (
        client.table("ml_evaluations")
        .select("*")
        .execute()
    )

    decisions = (
        client.table("shortlisting_decisions")
        .select("*")
        .execute()
    )

    requirements = (
        client.table("job_requirements")
        .select("*")
        .execute()
    )

    evaluation_map = {
        item["application_id"]: item
        for item in (evaluations.data or [])
    }

    decision_map = {
        item["application_id"]: item
        for item in (decisions.data or [])
    }

    requirement_map = {
        item["requirement_id"]: item
        for item in (requirements.data or [])
    }

    result = []

    for application in applications.data:

        application_id = application["application_id"]

        evaluation = evaluation_map.get(application_id)
        decision = decision_map.get(application_id)

        requirement = None
        eligible = False
        eligibility_reason = "Not evaluated"

        if evaluation:

            requirement_id = evaluation.get("requirement_id")

            requirement = requirement_map.get(requirement_id)

            if requirement:

                matching_score = float(
                    evaluation.get("matching_score") or 0
                )

                minimum_score = float(
                    requirement.get("minimum_score") or 60
                )

                missing_required_skills = (
                    evaluation.get("missing_skills") or []
                )

                all_required_skills_matched = (
                    len(missing_required_skills) == 0
                )

                score_passed = (
                    matching_score >= minimum_score
                )

                eligible = (
                    score_passed
                    and all_required_skills_matched
                )

                if eligible:
                    eligibility_reason = (
                        "Candidate meets the required score "
                        "and all required skills."
                    )

                elif not score_passed:
                    eligibility_reason = (
                        f"Score {matching_score}% is below "
                        f"the required {minimum_score}%."
                    )

                elif not all_required_skills_matched:
                    eligibility_reason = (
                        "Candidate is missing one or more "
                        "required skills."
                    )

        result.append({
            "application": application,
            "evaluation": evaluation,
            "requirement": requirement,
            "decision": decision,
            "eligible": eligible,
            "eligibility_reason": eligibility_reason,
        })

    return result


def get_shortlisted():
    """
    Get applications that HR has marked as shortlisted.
    """

    client = get_service_client()

    decisions = (
        client.table("shortlisting_decisions")
        .select("*")
        .eq("decision", "shortlisted")
        .order("decided_at", desc=True)
        .execute()
    )

    if not decisions.data:
        return []

    application_ids = [
        item["application_id"]
        for item in decisions.data
    ]

    applications = (
        client.table("applications")
        .select("*")
        .in_("application_id", application_ids)
        .execute()
    )

    application_map = {
        item["application_id"]: item
        for item in (applications.data or [])
    }

    result = []

    for decision in decisions.data:

        application = application_map.get(
            decision["application_id"]
        )

        if application:
            result.append({
                "application": application,
                "decision": decision,
            })

    return result


def get_non_shortlisted():
    """
    Get applications that HR has marked as non-shortlisted.
    """

    client = get_service_client()

    decisions = (
        client.table("shortlisting_decisions")
        .select("*")
        .eq("decision", "non_shortlisted")
        .order("decided_at", desc=True)
        .execute()
    )

    if not decisions.data:
        return []

    application_ids = [
        item["application_id"]
        for item in decisions.data
    ]

    applications = (
        client.table("applications")
        .select("*")
        .in_("application_id", application_ids)
        .execute()
    )

    application_map = {
        item["application_id"]: item
        for item in (applications.data or [])
    }

    result = []

    for decision in decisions.data:

        application = application_map.get(
            decision["application_id"]
        )

        if application:
            result.append({
                "application": application,
                "decision": decision,
            })

    return result


def save_decision(
    application_id: str,
    decision: str,
    reason: str | None,
    decided_by: str,
):
    """
    Save or update the HR's shortlisting decision.

    HR can override ML eligibility.

    After the decision is saved:
    - applications.current_status is synchronized
    - candidate receives a status notification email

    Re-saving the same decision does not send the same email again.
    """

    if decision not in (
        "shortlisted",
        "non_shortlisted",
    ):
        raise ValueError(
            "Decision must be 'shortlisted' or 'non_shortlisted'"
        )

    client = get_service_client()

    # ---------------------------------------------------------
    # 1. Check application exists
    # ---------------------------------------------------------

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
        .execute()
    )

    if not application_result.data:
        raise ValueError(
            "Application not found"
        )

    application = application_result.data[0]

    # ---------------------------------------------------------
    # 2. Check existing HR decision
    # ---------------------------------------------------------

    existing = (
        client
        .table("shortlisting_decisions")
        .select(
            "decision_id,"
            "decision"
        )
        .eq(
            "application_id",
            application_id
        )
        .execute()
    )

    previous_decision = None

    if existing.data:
        previous_decision = (
            existing.data[0].get("decision")
        )

    # ---------------------------------------------------------
    # 3. Save / update HR decision
    # ---------------------------------------------------------

    payload = {
        "application_id": application_id,
        "decision": decision,
        "reason": reason,
        "decided_by": decided_by,
    }

    if existing.data:

        result = (
            client
            .table("shortlisting_decisions")
            .update(payload)
            .eq(
                "application_id",
                application_id
            )
            .execute()
        )

    else:

        result = (
            client
            .table("shortlisting_decisions")
            .insert(payload)
            .execute()
        )

    if not result.data:
        raise RuntimeError(
            "Failed to save shortlisting decision"
        )

    # ---------------------------------------------------------
    # 4. Synchronize application status
    # ---------------------------------------------------------

    if decision == "shortlisted":
        new_status = "Shortlisted"
    else:
        new_status = "Non-Shortlisted"

    application_update = (
        client
        .table("applications")
        .update({
            "current_status": new_status
        })
        .eq(
            "application_id",
            application_id
        )
        .execute()
    )

    if not application_update.data:
        raise RuntimeError(
            "Shortlisting decision saved, "
            "but application status could not be updated"
        )

    # ---------------------------------------------------------
    # 5. Notify candidate
    #
    # Do not send another email when HR saves exactly the
    # same decision again.
    # ---------------------------------------------------------

    notification_sent = False
    notification_error = None

    if previous_decision != decision:

        if decision == "shortlisted":

            subject = (
                f"Application Shortlisted - "
                f"{application['position']}"
            )

            body = (
                "Congratulations!\n\n"
                "Your application has been shortlisted.\n\n"
                "You have successfully progressed to the next "
                "stage of our recruitment process.\n\n"
                "You will receive further instructions regarding "
                "the assessment."
            )

        else:

            subject = (
                f"Application Update - "
                f"{application['position']}"
            )

            body = (
                "Thank you for your interest in this position "
                "and for taking the time to apply.\n\n"
                "After reviewing your application, we will not "
                "be progressing your application to the next "
                "stage of the recruitment process.\n\n"
                "We appreciate your interest and wish you the "
                "best in your future opportunities."
            )

        try:

            send_candidate_notification(
                candidate_name=(
                    application["candidate_name"]
                ),
                candidate_email=(
                    application["email"]
                ),
                position=(
                    application["position"]
                ),
                subject=subject,
                body=body,
            )

            notification_sent = True

        except Exception as exc:

            # The HR decision is already safely stored.
            # An email failure must not undo/fail the
            # shortlisting operation.
            notification_error = str(exc)

            print(
                "Candidate notification email failed:",
                notification_error
            )

    # ---------------------------------------------------------
    # 6. Return decision
    # ---------------------------------------------------------

    return {
        **result.data[0],
        "notification_sent": notification_sent,
        "notification_error": notification_error,
    }