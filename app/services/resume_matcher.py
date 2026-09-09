import re
from typing import Any

from app.database import get_service_client
from app.services.resume_parser import parse_resume
from app.services.storage import download_resume
from app.services.ml_predictor import predict_candidate

SKILL_ALIASES = {
    "js": "javascript",
    "javascript": "javascript",

    "reactjs": "react",
    "react.js": "react",

    "nodejs": "node",
    "node.js": "node",

    "py": "python",

    "postgres": "postgresql",
    "postgres sql": "postgresql",

    "ml": "machine learning",
    "machine-learning": "machine learning",
}


def normalize_skill(skill: str) -> str:

    skill = skill.strip().lower()

    skill = re.sub(
        r"\s+",
        " ",
        skill,
    )

    return SKILL_ALIASES.get(
        skill,
        skill,
    )


def normalize_skills(
    skills: list[Any],
) -> set[str]:

    normalized = set()

    for skill in skills:

        if isinstance(skill, str):

            normalized.add(
                normalize_skill(skill)
            )

    return normalized

def calculate_matching_score(
    candidate_skills: list[Any],
    required_skills: list[Any],
    preferred_skills: list[Any],
) -> dict:

    candidate = normalize_skills(candidate_skills)
    required = normalize_skills(required_skills)
    preferred = normalize_skills(preferred_skills)

    matched_required = candidate.intersection(required)
    matched_preferred = candidate.intersection(preferred)

    missing_required = required - candidate

    # Required skills = 70%
    if required:
        required_score = (
            len(matched_required) / len(required)
        ) * 70
    else:
        required_score = 0

    # Preferred skills = 30%
    if preferred:
        preferred_score = (
            len(matched_preferred) / len(preferred)
        ) * 30
    else:
        preferred_score = 0

    score = required_score + preferred_score

    return {
        "matching_score": round(score, 2),

        "matching_skills": sorted(
            matched_required.union(matched_preferred)
        ),

        "matched_required_skills": sorted(
            matched_required
        ),

        "matched_preferred_skills": sorted(
            matched_preferred
        ),

        "missing_skills": sorted(
            missing_required
        ),
    }

def evaluate_application(
    application_id: str,
) -> dict:

    client = get_service_client()

    # ---------------------------------------------------------
    # 1. Get application
    # ---------------------------------------------------------

    application_result = (
        client
        .table("applications")
        .select("*")
        .eq(
            "application_id",
            application_id,
        )
        .single()
        .execute()
    )

    if not application_result.data:

        raise RuntimeError(
            "Application not found"
        )

    application = (
        application_result.data
    )

    # ---------------------------------------------------------
    # 2. Parse resume if skills are still empty
    # ---------------------------------------------------------

    candidate_skills = (
        application.get("skills")
        or []
    )

    resume_path = (
        application.get("resume_url")
    )

    if not candidate_skills and resume_path:

        try:

            resume_bytes = download_resume(
                resume_path
            )

            parsed = parse_resume(
                resume_bytes,
                resume_path,
            )

            candidate_skills = (
                parsed["skills"]
            )

            # Save everything we extracted.
            update_data = {
                "education": parsed[
                    "education"
                ],

                "skills": parsed[
                    "skills"
                ],

                "experience": parsed[
                    "experience"
                ],

                "projects": parsed[
                    "projects"
                ],
            }

            update_result = (
                client
                .table("applications")
                .update(update_data)
                .eq(
                    "application_id",
                    application_id,
                )
                .execute()
            )

            if update_result.data:
                application = (
                    update_result.data[0]
                )

        except Exception as exc:

            raise RuntimeError(
                "Failed to parse candidate resume: "
                f"{exc}"
            ) from exc

    # ---------------------------------------------------------
    # 3. Get job requirements
    # ---------------------------------------------------------

    requirements_result = (
    client
    .table("job_requirements")
    .select("*")
    .ilike(
        "department",
        application["department"],
    )
    .ilike(
        "position",
        application["position"],
    )
    .maybe_single()
    .execute()
    )  
    if not requirements_result or not requirements_result.data:

        raise RuntimeError(
            "No job requirements found for "
            f"{application['department']} / "
            f"{application['position']}"
        )

    requirements = (
        requirements_result.data
    )

    # ---------------------------------------------------------
    # 4. Make sure we use the latest skills
    # ---------------------------------------------------------

    candidate_skills = (
        application.get("skills")
        or []
    )

    # ---------------------------------------------------------
    # 5. Calculate score
    # ---------------------------------------------------------

    evaluation = calculate_matching_score(
        candidate_skills=candidate_skills,

        required_skills=(
            requirements.get(
                "required_skills"
            )
            or []
        ),

        preferred_skills=(
            requirements.get(
                "preferred_skills"
            )
            or []
        ),
    )

    # ---------------------------------------------------------
    # ML FEATURE CALCULATION
    # ---------------------------------------------------------

    required_skills = (
        requirements.get("required_skills")
        or []
    )

    preferred_skills = (
        requirements.get("preferred_skills")
        or []
    )

    matched_required_count = len(
        evaluation["matched_required_skills"]
    )

    matched_preferred_count = len(
        evaluation["matched_preferred_skills"]
    )

    if required_skills:

        required_skill_match = (
            matched_required_count
            / len(required_skills)
        ) * 100

    else:

        required_skill_match = 0


    if preferred_skills:

        preferred_skill_match = (
            matched_preferred_count
            / len(preferred_skills)
        ) * 100

    else:

        preferred_skill_match = 0


    total_skill_match = (
        required_skill_match * 0.7
        +
        preferred_skill_match * 0.3
    )

    # ---------------------------------------------------------
    # ML PREDICTION
    # ---------------------------------------------------------

    experience_years = len(
        application.get("experience") or []
    )

    project_count = len(
        application.get("projects") or []
    )

    ml_features = {
        "required_skill_match": required_skill_match,
        "preferred_skill_match": preferred_skill_match,
        "total_skill_match": total_skill_match,
        "matched_required_count": matched_required_count,
        "matched_preferred_count": matched_preferred_count,
        "experience_years": experience_years,
        "project_count": project_count,
    }

    ml_prediction = predict_candidate(
        ml_features
    )

    

    # ---------------------------------------------------------
    # 6. Save evaluation
    # ---------------------------------------------------------

    evaluation_row = {

        "application_id":
            application_id,

        "requirement_id":
            requirements[
                "requirement_id"
            ],

        "matching_score":
            evaluation[
                "matching_score"
            ],

        "matching_skills":
            evaluation[
                "matching_skills"
            ],

        "missing_skills":
            evaluation[
                "missing_skills"
            ],

        "matched_required_skills":
            evaluation[
                "matched_required_skills"
            ],

        "matched_preferred_skills":
            evaluation[
                "matched_preferred_skills"
            ],

        "ml_prediction": 
            ml_prediction[
                "prediction"
            ],

        "ml_probability": 
            ml_prediction[
                "probability"
            ],   
    }

    result = (
        client
        .table("ml_evaluations")
        .upsert(
            evaluation_row,
            on_conflict="application_id",
        )
        .execute()
    )


    if not result.data:

        raise RuntimeError(
            "Failed to save ML evaluation"
        )

    return result.data[0]