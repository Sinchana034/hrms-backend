from app.database import get_service_client


def get_job_requirements(department: str, position: str) -> dict:
    client = get_service_client()

    result = (
        client.table("job_requirements")
        .select("requirement_id, department, position, required_skills, preferred_skills")
        .eq("department", department)
        .eq("position", position)
        .single()
        .execute()
    )

    if not result.data:
        raise ValueError(
            f"No job requirements found for {department} / {position}"
        )

    return result.data