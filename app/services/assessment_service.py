import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from app.config import get_settings
from app.database import get_service_client
from app.services.assessment_questions import select_questions
from app.services.assessment_email import send_assessment_email


# =========================================================
# ASSESSMENT SETTINGS
# =========================================================

# Candidate has 72 hours to OPEN the invitation link.
# This is NOT the actual exam duration.
ASSESSMENT_DURATION_HOURS = 72

# Once the candidate starts the assessment,
# they have 25 minutes to complete it.
ASSESSMENT_DURATION_MINUTES = 25

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
        raise RuntimeError(
            "Application not found"
        )

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
    # Assessment invitation expiry
    # -----------------------------------------------------

    now = datetime.now(timezone.utc)

    expires_at = (
        now
        + timedelta(hours=ASSESSMENT_DURATION_HOURS)
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

    frontend_url = get_settings().frontend_url

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

    The actual exam timer is based on the server-side
    started_at timestamp and therefore does NOT reset
    when the candidate refreshes or reopens the page.
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
    # Check invitation expiry
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
    # Start assessment / calculate exam deadline
    # -----------------------------------------------------

    if assessment["status"] == "Invited":

        # First access starts the 25-minute exam clock.
        started_at = now

        exam_deadline = (
            started_at
            + timedelta(minutes=ASSESSMENT_DURATION_MINUTES)
        )

        client.table("assessments").update({
            "status": "Started",
            "started_at": started_at.isoformat(),
        }).eq(
            "assessment_id",
            assessment["assessment_id"]
        ).execute()

    else:

        # Assessment was already started.
        # NEVER reset the timer.
        if not assessment.get("started_at"):
            raise RuntimeError(
                "Assessment start time is missing"
            )

        started_at = datetime.fromisoformat(
            assessment["started_at"].replace("Z", "+00:00")
        )

        exam_deadline = (
            started_at
            + timedelta(minutes=ASSESSMENT_DURATION_MINUTES)
        )

    # -----------------------------------------------------
    # Check 25-minute exam deadline
    # -----------------------------------------------------

    if exam_deadline <= now:
        raise RuntimeError(
            "Assessment time has expired"
        )

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

    # -----------------------------------------------------
    # Load saved answers
    # -----------------------------------------------------

    responses_result = (
        client
        .table("assessment_responses")
        .select("question_index,selected_option")
        .eq(
            "assessment_id",
            assessment["assessment_id"]
        )
        .execute()
    )

    saved_answers = [
        None
        for _ in range(assessment["total_questions"])
    ]

    for response in responses_result.data or []:

        question_index = response.get("question_index")

        if (
            question_index is not None
            and 0 <= question_index < len(saved_answers)
        ):
            saved_answers[question_index] = (
                response.get("selected_option")
            )

    # -----------------------------------------------------
    # Return assessment
    # -----------------------------------------------------

    return {
    "assessment_id": assessment["assessment_id"],
    "position": assessment["position"],
    "questions": safe_questions,
    "total_questions": assessment["total_questions"],
    "pass_threshold": assessment["pass_threshold"],
    "expires_at": assessment["expires_at"],
    "started_at": started_at.isoformat(),
    "exam_deadline": exam_deadline.isoformat(),
    "duration_minutes": ASSESSMENT_DURATION_MINUTES,
    "saved_answers": saved_answers,
    "status": "Started",
}


# =========================================================
# SUBMIT ASSESSMENT
# =========================================================

def submit_assessment(
    token: str,
    answers: list[str | None],
    terminated_reason: str | None = None,
):
    """
    Evaluate and submit the candidate assessment.

    terminated_reason is set when the assessment is
    automatically terminated because of a proctoring
    violation or because the exam timer expired.
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
    # Check invitation expiry
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
    # Check assessment was started
    # -----------------------------------------------------

    if not assessment.get("started_at"):
        raise RuntimeError(
            "Assessment has not been started"
        )

    assessment_started_at = datetime.fromisoformat(
        assessment["started_at"].replace("Z", "+00:00")
    )

    # -----------------------------------------------------
    # Calculate 25-minute deadline
    # -----------------------------------------------------

    exam_deadline = (
        assessment_started_at
        + timedelta(minutes=ASSESSMENT_DURATION_MINUTES)
    )

    # -----------------------------------------------------
    # Check 25-minute deadline
    # -----------------------------------------------------

    if exam_deadline <= now:

        # Time expired.
        # The assessment will be submitted with
        # whatever answers were available.
        terminated_reason = (
            terminated_reason
            or "time_expired"
        )

    # -----------------------------------------------------
    # Questions
    # -----------------------------------------------------

    questions = assessment["questions"]

    # -----------------------------------------------------
    # Validate answer count
    # -----------------------------------------------------

    if len(answers) != len(questions):

        if terminated_reason is not None:

            # Automatic submission.
            # Pad unanswered questions with None.
            answers = (
                answers
                + [None] * len(questions)
            )[:len(questions)]

        else:

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

        # -------------------------------------------------
        # Save response
        # -------------------------------------------------

        client.table("assessment_responses").upsert(
            {
                "assessment_id": assessment["assessment_id"],
                "question_index": index,
                "selected_option": selected_option,
                "is_correct": is_correct,
                "locked_at": now.isoformat(),
            },
            on_conflict="assessment_id,question_index",
        ).execute()

    # -----------------------------------------------------
    # Calculate percentage
    # -----------------------------------------------------

    total_questions = len(questions)

    score = (
        correct_answers
        / total_questions
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
            "terminated_reason": terminated_reason,
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
        "terminated_reason": terminated_reason,
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
            "completed_at,"
            "terminated_reason"
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

    assessment = result.data[0]

    # -----------------------------------------------------
    # Get violations
    # -----------------------------------------------------

    violations_result = (
        client
        .table("assessment_violations")
        .select(
            "violation_type,occurred_at"
        )
        .eq(
            "assessment_id",
            assessment["assessment_id"]
        )
        .order(
            "occurred_at"
        )
        .execute()
    )

    assessment["violations"] = (
        violations_result.data or []
    )

    return assessment


# =========================================================
# RECORD PROCTORING VIOLATION
# =========================================================

def record_violation(
    token: str,
    violation_type: str,
):
    """
    Logs a single proctoring violation against
    the assessment matching the candidate token.

    Returns the running violation count.
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
        .select(
            "assessment_id,expires_at"
        )
        .eq(
            "token_hash",
            token_hash
        )
        .single()
        .execute()
    )

    access_token = token_result.data

    if not access_token:
        raise RuntimeError(
            "Invalid assessment link"
        )

    # -----------------------------------------------------
    # Record violation
    # -----------------------------------------------------

    client.table(
        "assessment_violations"
    ).insert({
        "assessment_id": access_token["assessment_id"],
        "violation_type": violation_type,
    }).execute()

    # -----------------------------------------------------
    # Count violations
    # -----------------------------------------------------

    count_result = (
        client
        .table("assessment_violations")
        .select(
            "violation_id",
            count="exact"
        )
        .eq(
            "assessment_id",
            access_token["assessment_id"]
        )
        .execute()
    )

    return {
        "violation_type": violation_type,
        "total_violations": (
            count_result.count or 0
        ),
    }

# =========================================================
# SAVE ASSESSMENT ANSWER
# =========================================================

def save_assessment_answer(
    token: str,
    question_index: int,
    selected_option: str | None,
):
    """
    Save a candidate's answer while the assessment is in progress.

    This does NOT submit or score the assessment.
    It only saves the current answer so progress can be
    restored if the candidate leaves and reopens the link.
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
        .eq(
            "token_hash",
            token_hash
        )
        .single()
        .execute()
    )

    access_token = token_result.data

    if not access_token:
        raise RuntimeError(
            "Invalid assessment link"
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
            "Assessment has already been completed"
        )

    # -----------------------------------------------------
    # Check assessment started
    # -----------------------------------------------------

    if not assessment.get("started_at"):
        raise RuntimeError(
            "Assessment has not been started"
        )

    # -----------------------------------------------------
    # Check 25-minute deadline
    # -----------------------------------------------------

    started_at = datetime.fromisoformat(
        assessment["started_at"].replace("Z", "+00:00")
    )

    now = datetime.now(timezone.utc)

    exam_deadline = (
        started_at
        + timedelta(minutes=ASSESSMENT_DURATION_MINUTES)
    )

    if exam_deadline <= now:
        raise RuntimeError(
            "Assessment time has expired"
        )

    # -----------------------------------------------------
    # Validate question index
    # -----------------------------------------------------

    questions = assessment["questions"]

    if (
        question_index < 0
        or question_index >= len(questions)
    ):
        raise RuntimeError(
            "Invalid question index"
        )

    # -----------------------------------------------------
    # Validate selected option
    # -----------------------------------------------------

    question = questions[question_index]

    options = question.get("options", [])

    if (
        selected_option is not None
        and selected_option not in options
    ):
        raise RuntimeError(
            "Invalid answer option"
        )

    # -----------------------------------------------------
    # Save answer
    # -----------------------------------------------------

    response_result = (
        client
        .table("assessment_responses")
        .upsert(
            {
                "assessment_id": assessment["assessment_id"],
                "question_index": question_index,
                "selected_option": selected_option,
                "is_correct": None,
                "locked_at": None,
            },
            on_conflict="assessment_id,question_index",
        )
        .execute()
    )

    if not response_result.data:
        raise RuntimeError(
            "Failed to save assessment answer"
        )

    return {
        "message": "Answer saved",
        "question_index": question_index,
    }

# =========================================================
# HANDLE CANDIDATE TAB CLOSE
# =========================================================

def handle_tab_close(token: str):
    """
    Record a candidate closing/leaving the assessment page.

    First close:
        - Record violation
        - Keep assessment resumable

    Second close:
        - Record violation
        - Automatically submit using saved answers
        - Assessment becomes Completed
        - Access link becomes unavailable
    """

    client = get_service_client()

    # -----------------------------------------------------
    # Find assessment from token
    # -----------------------------------------------------

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

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
        raise RuntimeError("Invalid assessment link")

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
        raise RuntimeError("Assessment not found")

    # -----------------------------------------------------
    # Already completed
    # -----------------------------------------------------

    if assessment["status"] == "Completed":
        return {
            "message": "Assessment already completed",
            "terminated": True,
            "close_count": 2,
        }

    # -----------------------------------------------------
    # Record close violation
    # -----------------------------------------------------

    client.table("assessment_violations").insert({
        "assessment_id": assessment["assessment_id"],
        "violation_type": "tab_close",
    }).execute()

    # -----------------------------------------------------
    # Count tab closes ONLY
    # -----------------------------------------------------

    count_result = (
        client
        .table("assessment_violations")
        .select(
            "violation_id",
            count="exact"
        )
        .eq(
            "assessment_id",
            assessment["assessment_id"]
        )
        .eq(
            "violation_type",
            "tab_close"
        )
        .execute()
    )

    close_count = count_result.count or 0

    # -----------------------------------------------------
    # FIRST CLOSE
    # -----------------------------------------------------

    if close_count < 2:

        return {
            "message": (
                "Tab close recorded. "
                "Assessment remains resumable."
            ),
            "terminated": False,
            "close_count": close_count,
        }

    # -----------------------------------------------------
    # SECOND CLOSE → TERMINATE
    # -----------------------------------------------------

    # Get all answers already saved by the candidate.
    responses_result = (
        client
        .table("assessment_responses")
        .select(
            "question_index,selected_option"
        )
        .eq(
            "assessment_id",
            assessment["assessment_id"]
        )
        .execute()
    )

    answers = [
        None
        for _ in range(assessment["total_questions"])
    ]

    for response in responses_result.data or []:

        index = response.get("question_index")

        if (
            index is not None
            and 0 <= index < len(answers)
        ):
            answers[index] = response.get(
                "selected_option"
            )

    # -----------------------------------------------------
    # Submit assessment
    # -----------------------------------------------------

    result = submit_assessment(
        token=token,
        answers=answers,
        terminated_reason="tab_close_limit",
    )

    return {
        "message": (
            "Assessment terminated after "
            "two tab closes."
        ),
        "terminated": True,
        "close_count": close_count,
        "result": result,
    }