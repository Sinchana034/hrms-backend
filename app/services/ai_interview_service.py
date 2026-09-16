from app.database import get_service_client


# =========================================================
# AI INTERVIEW QUESTION BANK
# =========================================================

INTERVIEW_QUESTION_BANK = {
    "python": [
        "Explain the difference between a list, tuple, set, and dictionary in Python.",
        "What is the difference between shallow copy and deep copy in Python?",
        "Explain exception handling in Python with an example.",
        "What are decorators in Python?",
        "What is the difference between a Python list and a generator?",
    ],

    "django": [
        "Explain Django's MVT architecture.",
        "What are Django models and how are they connected to the database?",
        "What is Django ORM?",
        "Explain the difference between authentication and authorization in Django.",
        "How would you optimize a slow Django application?",
    ],

    "fastapi": [
        "What is FastAPI and why would you choose it over Flask?",
        "What is dependency injection in FastAPI?",
        "How do you create a POST endpoint in FastAPI?",
        "How does Pydantic validation work in FastAPI?",
        "How would you secure a FastAPI application?",
    ],

    "sql": [
        "What is the difference between WHERE and HAVING?",
        "Explain INNER JOIN, LEFT JOIN, RIGHT JOIN, and FULL JOIN.",
        "What is database normalization?",
        "What is an index and how does it improve query performance?",
        "What is the difference between DELETE, TRUNCATE, and DROP?",
    ],

    "git": [
        "What is the difference between git merge and git rebase?",
        "Explain the purpose of a Git branch.",
        "What is the difference between git pull and git fetch?",
        "How would you resolve a merge conflict?",
        "What is the purpose of git stash?",
    ],

    "javascript": [
        "What is the difference between var, let, and const?",
        "Explain closures in JavaScript.",
        "What is the difference between == and ===?",
        "What are promises and async/await?",
        "Explain the JavaScript event loop.",
    ],

    "react": [
        "What is the difference between state and props in React?",
        "Explain the useState hook.",
        "Explain the useEffect hook.",
        "Why are keys required when rendering lists in React?",
        "What is the difference between controlled and uncontrolled components?",
    ],

    "angular": [
        "What is Angular and how is it different from React?",
        "What is a component in Angular?",
        "What is dependency injection in Angular?",
        "Explain Angular services.",
        "What is the difference between ngOnInit and a constructor?",
    ],
}


# =========================================================
# NORMALIZE SKILL
# =========================================================

def normalize_skill(skill):
    return str(skill).strip().lower()


# =========================================================
# GENERATE INTERVIEW QUESTIONS
# =========================================================

def generate_interview_questions(skills):
    """
    Generate interview questions based on candidate skills.

    If no recognized skills are available, use general
    Software Engineering interview questions.
    """

    questions = []

    # -----------------------------------------------------
    # GENERAL FALLBACK QUESTIONS
    # -----------------------------------------------------

    GENERAL_INTERVIEW_QUESTIONS = [
        "Explain the difference between an array and a linked list.",
        "What are the four main principles of Object-Oriented Programming?",
        "What is the difference between a stack and a queue?",
        "What is the difference between a primary key and a foreign key?",
        "Explain the difference between authentication and authorization.",
        "What is an API and why is it used in software applications?",
        "What is the difference between GET and POST HTTP methods?",
        "What does HTTP status code 404 mean?",
        "What is the purpose of version control systems such as Git?",
        "What is the difference between git merge and git rebase?",
        "What is an exception and how should application errors be handled?",
        "What is the purpose of database indexing?",
        "Explain the difference between SQL and NoSQL databases.",
        "What is REST architecture?",
        "What is the purpose of input validation in a web application?",
        "What is time complexity and why is it important?",
        "Explain the difference between frontend and backend development.",
        "What is a REST API endpoint?",
        "What is debugging and how do you approach finding a bug?",
        "Explain the basic request-response cycle in a web application.",
    ]

    # -----------------------------------------------------
    # USE SKILL-BASED QUESTIONS WHEN AVAILABLE
    # -----------------------------------------------------

    for skill in skills or []:

        normalized_skill = normalize_skill(skill)

        skill_questions = INTERVIEW_QUESTION_BANK.get(
            normalized_skill,
            []
        )

        for question in skill_questions:

            questions.append({
                "skill": normalized_skill,
                "question": question,
            })

    # -----------------------------------------------------
    # FALLBACK WHEN NO RECOGNIZED SKILLS EXIST
    # -----------------------------------------------------

    if not questions:

        for question in GENERAL_INTERVIEW_QUESTIONS:

            questions.append({
                "skill": "general",
                "question": question,
            })

    return questions
# =========================================================
# CREATE AI INTERVIEW
# =========================================================

def create_ai_interview(application_id: str):

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
    # Check latest assessment
    # -----------------------------------------------------

    assessment_result = (
        client
        .table("assessments")
        .select(
            "assessment_id,"
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
            "Candidate has not completed an assessment"
        )

    assessment = assessment_result.data[0]

    # -----------------------------------------------------
    # Candidate must pass assessment
    # -----------------------------------------------------

    if assessment["status"] != "Completed":
        raise RuntimeError(
            "Candidate assessment is not completed"
        )

    if assessment["result"] != "Passed":
        raise RuntimeError(
            "Candidate has not passed the assessment"
        )

    # -----------------------------------------------------
    # Check whether interview already exists
    # -----------------------------------------------------

    existing_result = (
        client
        .table("ai_interviews")
        .select("*")
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

    if existing_result.data:
        return {
            "message": "AI Interview already exists",
            "interview": existing_result.data[0],
            "candidate_name": application["candidate_name"],
            "candidate_email": application["email"],
        }

    # -----------------------------------------------------
    # Generate questions
    # -----------------------------------------------------

    skills = application.get("skills") or []

    questions = generate_interview_questions(skills)

    if not questions:
        raise RuntimeError(
            "No interview questions available for candidate skills"
        )

    # -----------------------------------------------------
    # Create interview
    # -----------------------------------------------------

    interview_result = (
        client
        .table("ai_interviews")
        .insert({
            "application_id": application_id,
            "position": application["position"],
            "questions": questions,
            "total_questions": len(questions),
            "status": "Created",
        })
        .execute()
    )

    if not interview_result.data:
        raise RuntimeError(
            "Failed to create AI interview"
        )

    interview = interview_result.data[0]

    return {
        "message": "AI Interview created successfully",
        "interview": interview,
        "candidate_name": application["candidate_name"],
        "candidate_email": application["email"],
        "position": application["position"],
    }