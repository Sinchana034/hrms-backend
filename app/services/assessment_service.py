import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from app.database import get_service_client
from app.services.assessment_questions import select_questions
from app.services.assessment_email import send_assessment_email


ASSESSMENT_DURATION_HOURS = 72
PASS_THRESHOLD = 70


# =========================================================
# GENERATE ACCESS TOKEN
# =========================================================

def generate_access_token():
    """
    Generate a cryptographically secure random token.
    """

    raw_token = secrets.token_urlsafe(48)

    token_hash = hashlib.sha256(
        raw_token.encode("utf-8")
    ).hexdigest()

    return raw_token, token_hash


# =========================================================
# CREATE ASSESSMENT
# =========================================================

def create_assessment(application_id):
    """
    Create an assessment for a shortlisted candidate.
    """

    client = get_service_client()

    # -----------------------------------------------------
    # Get application
    # -----------------------------------------------------

    application_result = (
        client
        .table("applications")
        .select(
            "application_id,"
            "candidate_name,"
            "email,"
            "position,"
            "skills,"
            "current_status"
        )
        .eq("application_id", application_id)
        .single()
        .execute()
    )

    application = application_result.data

    if not application:
        raise RuntimeError("Application not found")

    # -----------------------------------------------------
    # Candidate must be shortlisted
    # -----------------------------------------------------

    shortlisting_result = (
        client
        .table("shortlisting_decisions")
        .select("decision")
        .eq("application_id", application_id)
        .limit(1)
        .execute()
    )

    shortlisting_decision = (
        shortlisting_result.data[0]["decision"]
        if shortlisting_result.data
        else None
    )

    if shortlisting_decision != "shortlisted":
        raise RuntimeError(
            "Candidate must be shortlisted before assessment"
        )

    # -----------------------------------------------------
    # Get candidate skills
    # -----------------------------------------------------

    skills = application.get("skills") or []

    # -----------------------------------------------------
    # Select questions
    # -----------------------------------------------------

    questions = select_questions(skills)

    if not questions:
        raise RuntimeError(
            "No assessment questions available for candidate skills"
        )

    # -----------------------------------------------------
    # Assessment expiry
    # -----------------------------------------------------

    now = datetime.now(timezone.utc)

    expires_at = now + timedelta(
        hours=ASSESSMENT_DURATION_HOURS
    )

    # -----------------------------------------------------
    # Create assessment
    # -----------------------------------------------------

    assessment_result = (
        client
        .table("assessments")
        .insert({
            "application_id": application_id,
            "position": application["position"],
            "questions": questions,
            "total_questions": len(questions),
            "pass_threshold": PASS_THRESHOLD,
            "status": "Invited",
            "expires_at": expires_at.isoformat(),
        })
        .execute()
    )

    if not assessment_result.data:
        raise RuntimeError(
            "Failed to create assessment"
        )

    assessment = assessment_result.data[0]

    # -----------------------------------------------------
    # Generate access token
    # -----------------------------------------------------

    raw_token, token_hash = generate_access_token()

    token_result = (
        client
        .table("assessment_access_tokens")
        .insert({
            "assessment_id": assessment["assessment_id"],
            "token_hash": token_hash,
            "expires_at": expires_at.isoformat(),
        })
        .execute()
    )

    if not token_result.data:
        raise RuntimeError(
            "Failed to create assessment access token"
        )

    # -----------------------------------------------------
    # Candidate assessment URL
    # -----------------------------------------------------

    frontend_url =  "http://localhost:5173"

    assessment_url = (
        f"{frontend_url}/assessment/{raw_token}"
    )

    # -----------------------------------------------------
    # Send assessment email
    # -----------------------------------------------------

    send_assessment_email(
        candidate_name=application["candidate_name"],
        candidate_email=application["email"],
        position=application["position"],
        assessment_url=assessment_url,
        expires_at=expires_at,
    )

    # -----------------------------------------------------
    # Return
    # -----------------------------------------------------

    return {
        "assessment": assessment,
        "access_token": raw_token,
        "assessment_url": assessment_url,
        "expires_at": expires_at,
        "candidate_name": application["candidate_name"],
        "candidate_email": application["email"],
        "position": application["position"],
    }


# =========================================================
# GET ASSESSMENT BY TOKEN
# =========================================================

def get_assessment_by_token(token: str):
    """
    Get an assessment using the candidate's access token.

    Correct answers are never returned.
    """

    client = get_service_client()

    # -----------------------------------------------------
    # Hash token
    # -----------------------------------------------------

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    # -----------------------------------------------------
    # Find access token
    # -----------------------------------------------------

    token_result = (
        client
        .table("assessment_access_tokens")
        .select("*")
        .eq("token_hash", token_hash)
        .single()
        .execute()
    )

    access_token = token_result.data

    if not access_token:
        raise RuntimeError(
            "Invalid assessment link"
        )

    # -----------------------------------------------------
    # Check expiry
    # -----------------------------------------------------

    expires_at = datetime.fromisoformat(
        access_token["expires_at"].replace("Z", "+00:00")
    )

    now = datetime.now(timezone.utc)

    if expires_at <= now:
        raise RuntimeError(
            "This assessment link has expired"
        )

    # -----------------------------------------------------
    # Get assessment
    # -----------------------------------------------------

    assessment_result = (
        client
        .table("assessments")
        .select("*")
        .eq(
            "assessment_id",
            access_token["assessment_id"]
        )
        .single()
        .execute()
    )

    assessment = assessment_result.data

    if not assessment:
        raise RuntimeError(
            "Assessment not found"
        )

    # -----------------------------------------------------
    # Check completed
    # -----------------------------------------------------

    if assessment["status"] == "Completed":
        raise RuntimeError(
            "This assessment has already been completed"
        )

    # -----------------------------------------------------
    # Change Invited → Started
    # -----------------------------------------------------

    if assessment["status"] == "Invited":

        client.table("assessments").update({
            "status": "Started",
            "started_at": now.isoformat(),
        }).eq(
            "assessment_id",
            assessment["assessment_id"]
        ).execute()

    # -----------------------------------------------------
    # Return safe questions
    # -----------------------------------------------------

    safe_questions = []

    for question in assessment["questions"]:

        safe_questions.append({
            "skill": question.get("skill"),
            "question": question.get("question"),
            "options": question.get("options", []),
        })

    return {
        "assessment_id": assessment["assessment_id"],
        "position": assessment["position"],
        "questions": safe_questions,
        "total_questions": assessment["total_questions"],
        "pass_threshold": assessment["pass_threshold"],
        "expires_at": assessment["expires_at"],
        "status": "Started",
    }


# =========================================================
# SUBMIT ASSESSMENT
# =========================================================

def submit_assessment(
    token: str,
    answers: list[str | None],
):
    """
    Evaluate and submit the candidate assessment.
    """

    client = get_service_client()

    # -----------------------------------------------------
    # Hash token
    # -----------------------------------------------------

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    # -----------------------------------------------------
    # Get access token
    # -----------------------------------------------------

    token_result = (
        client
        .table("assessment_access_tokens")
        .select("*")
        .eq("token_hash", token_hash)
        .single()
        .execute()
    )

    access_token = token_result.data

    if not access_token:
        raise RuntimeError(
            "Invalid assessment link"
        )

    # -----------------------------------------------------
    # Check expiry
    # -----------------------------------------------------

    expires_at = datetime.fromisoformat(
        access_token["expires_at"].replace("Z", "+00:00")
    )

    now = datetime.now(timezone.utc)

    if expires_at <= now:
        raise RuntimeError(
            "This assessment link has expired"
        )

    # -----------------------------------------------------
    # Get assessment
    # -----------------------------------------------------

    assessment_result = (
        client
        .table("assessments")
        .select("*")
        .eq(
            "assessment_id",
            access_token["assessment_id"]
        )
        .single()
        .execute()
    )

    assessment = assessment_result.data

    if not assessment:
        raise RuntimeError(
            "Assessment not found"
        )

    # -----------------------------------------------------
    # Check already submitted
    # -----------------------------------------------------

    if assessment["status"] == "Completed":
        raise RuntimeError(
            "Assessment has already been submitted"
        )

    # -----------------------------------------------------
    # Questions
    # -----------------------------------------------------

    questions = assessment["questions"]

    if len(answers) != len(questions):
        raise RuntimeError(
            "Number of answers does not match number of questions"
        )

    # -----------------------------------------------------
    # Calculate score
    # -----------------------------------------------------

    correct_answers = 0

    for index, question in enumerate(questions):

        selected_option = answers[index]

        correct_option = question.get("answer")

        is_correct = (
            selected_option is not None
            and selected_option == correct_option
        )

        if is_correct:
            correct_answers += 1

        # Save response
        client.table("assessment_responses").upsert({
            "assessment_id": assessment["assessment_id"],
            "question_index": index,
            "selected_option": selected_option,
            "is_correct": is_correct,
            "locked_at": now.isoformat(),
        }).execute()

    # -----------------------------------------------------
    # Calculate percentage
    # -----------------------------------------------------

    total_questions = len(questions)

    score = (
        correct_answers / total_questions
    ) * 100

    # -----------------------------------------------------
    # Determine result
    # -----------------------------------------------------

    pass_threshold = float(
        assessment["pass_threshold"]
    )

    if score >= pass_threshold:
        result = "Passed"
    else:
        result = "Failed"

    # -----------------------------------------------------
    # Determine application status
    # -----------------------------------------------------

    # if result == "Passed":
    #     new_application_status = "Assessment Passed"
    # else:
    #     new_application_status = "Assessment Failed"

    # # -----------------------------------------------------
    # # Update application
    # # -----------------------------------------------------

    # application_update = (
    #     client
    #     .table("applications")
    #     .update({
    #         "current_status": new_application_status
    #     })
    #     .eq(
    #         "application_id",
    #         assessment["application_id"]
    #     )
    #     .execute()
    # )

    # if not application_update.data:
    #     raise RuntimeError(
    #         "Assessment result calculated, "
    #         "but application status could not be updated"
    #     )

    # -----------------------------------------------------
    # Update assessment
    # -----------------------------------------------------

    assessment_update = (
        client
        .table("assessments")
        .update({
            "score": score,
            "result": result,
            "status": "Completed",
            "completed_at": now.isoformat(),
        })
        .eq(
            "assessment_id",
            assessment["assessment_id"]
        )
        .execute()
    )

    if not assessment_update.data:
        raise RuntimeError(
            "Assessment result calculated, "
            "but assessment could not be updated"
        )

    # -----------------------------------------------------
    # Mark token as used
    # -----------------------------------------------------

    client.table("assessment_access_tokens").update({
        "used_at": now.isoformat(),
    }).eq(
        "access_token_id",
        access_token["access_token_id"]
    ).execute()

    # -----------------------------------------------------
    # Return result
    # -----------------------------------------------------

    return {
        "message": "Assessment submitted successfully",
        "score": round(score, 2),
        "result": result,
        "correct_answers": correct_answers,
        "total_questions": total_questions,
        "pass_threshold": pass_threshold,
    }


# =========================================================
# GET ASSESSMENT RESULT
# =========================================================

def get_assessment_result(application_id: str):
    """
    Get the latest assessment result for an application.
    HR/Admin only.
    """

    client = get_service_client()

    result = (
        client
        .table("assessments")
        .select(
            "assessment_id,"
            "application_id,"
            "position,"
            "total_questions,"
            "pass_threshold,"
            "score,"
            "result,"
            "status,"
            "expires_at,"
            "completed_at"
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

    if not result.data:
        raise RuntimeError(
            "No assessment found for this application"
        )

    return result.data[0]