from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth import CurrentUser, require_hr_admin
from app.database import get_service_client


router = APIRouter(
    prefix="/job-requirements",
    tags=["job-requirements"],
)


class JobRequirementCreate(BaseModel):
    department_id: str
    position: str
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)


class JobRequirementUpdate(BaseModel):
    department_id: str
    position: str
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# List all job requirements
# PUBLIC — used by the candidate application form
# ---------------------------------------------------------------------------
@router.get("")
async def list_job_requirements():
    client = get_service_client()

    result = (
        client.table("job_requirements")
        .select("*")
        .order("department")
        .order("position")
        .execute()
    )

    return result.data


# ---------------------------------------------------------------------------
# Get one job requirement
# HR ADMIN ONLY
# ---------------------------------------------------------------------------
@router.get("/{requirement_id}")
async def get_job_requirement(
    requirement_id: str,
    user: CurrentUser = Depends(require_hr_admin),
):
    client = get_service_client()

    result = (
        client.table("job_requirements")
        .select("*")
        .eq("requirement_id", requirement_id)
        .single()
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=404,
            detail="Job requirement not found",
        )

    return result.data


# ---------------------------------------------------------------------------
# Create job requirement
# HR ADMIN ONLY
# ---------------------------------------------------------------------------
@router.post("")
async def create_job_requirement(
    payload: JobRequirementCreate,
    user: CurrentUser = Depends(require_hr_admin),
):
    client = get_service_client()

    department = (
        client.table("departments")
        .select("department_id, name")
        .eq("department_id", payload.department_id)
        .single()
        .execute()
    )

    if not department.data:
        raise HTTPException(
            status_code=404,
            detail="Department not found",
        )

    existing = (
        client.table("job_requirements")
        .select("requirement_id")
        .eq("department_id", payload.department_id)
        .eq("position", payload.position)
        .execute()
    )

    if existing.data:
        raise HTTPException(
            status_code=409,
            detail="Job requirement already exists for this department and position",
        )

    result = (
        client.table("job_requirements")
        .insert(
            {
                "department_id": payload.department_id,
                "department": department.data["name"],
                "position": payload.position,
                "required_skills": payload.required_skills,
                "preferred_skills": payload.preferred_skills,
            }
        )
        .execute()
    )

    return result.data[0]


# ---------------------------------------------------------------------------
# Update job requirement
# HR ADMIN ONLY
# ---------------------------------------------------------------------------
@router.put("/{requirement_id}")
async def update_job_requirement(
    requirement_id: str,
    payload: JobRequirementUpdate,
    user: CurrentUser = Depends(require_hr_admin),
):
    client = get_service_client()

    existing = (
        client.table("job_requirements")
        .select("*")
        .eq("requirement_id", requirement_id)
        .execute()
    )

    if not existing.data:
        raise HTTPException(
            status_code=404,
            detail="Job requirement not found",
        )

    department = (
        client.table("departments")
        .select("department_id, name")
        .eq("department_id", payload.department_id)
        .single()
        .execute()
    )

    if not department.data:
        raise HTTPException(
            status_code=404,
            detail="Department not found",
        )

    result = (
        client.table("job_requirements")
        .update(
            {
                "department_id": payload.department_id,
                "department": department.data["name"],
                "position": payload.position,
                "required_skills": payload.required_skills,
                "preferred_skills": payload.preferred_skills,
            }
        )
        .eq("requirement_id", requirement_id)
        .execute()
    )

    return result.data[0]


# ---------------------------------------------------------------------------
# Delete job requirement
# HR ADMIN ONLY
# ---------------------------------------------------------------------------
@router.delete("/{requirement_id}")
async def delete_job_requirement(
    requirement_id: str,
    user: CurrentUser = Depends(require_hr_admin),
):
    client = get_service_client()

    existing = (
        client.table("job_requirements")
        .select("requirement_id")
        .eq("requirement_id", requirement_id)
        .execute()
    )

    if not existing.data:
        raise HTTPException(
            status_code=404,
            detail="Job requirement not found",
        )

    client.table("job_requirements").delete().eq(
        "requirement_id",
        requirement_id,
    ).execute()

    return {
        "status": "deleted",
        "requirement_id": requirement_id,
    }