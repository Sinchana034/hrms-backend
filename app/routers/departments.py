from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth import CurrentUser, require_hr_admin
from app.database import get_service_client


router = APIRouter(
    prefix="/departments",
    tags=["departments"],
)


class DepartmentCreate(BaseModel):
    name: str
    description: str | None = None


class DepartmentUpdate(BaseModel):
    name: str
    description: str | None = None


# ---------------------------------------------------------------------------
# List all departments
# PUBLIC — used by the candidate application form
# ---------------------------------------------------------------------------
@router.get("")
async def list_departments():
    client = get_service_client()

    result = (
        client.table("departments")
        .select("*")
        .order("name")
        .execute()
    )

    return result.data


# ---------------------------------------------------------------------------
# Get one department
# HR ADMIN ONLY
# ---------------------------------------------------------------------------
@router.get("/{department_id}")
async def get_department(
    department_id: str,
    user: CurrentUser = Depends(require_hr_admin),
):
    client = get_service_client()

    result = (
        client.table("departments")
        .select("*")
        .eq("department_id", department_id)
        .single()
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=404,
            detail="Department not found",
        )

    return result.data


# ---------------------------------------------------------------------------
# Create department
# HR ADMIN ONLY
# ---------------------------------------------------------------------------
@router.post("")
async def create_department(
    payload: DepartmentCreate,
    user: CurrentUser = Depends(require_hr_admin),
):
    client = get_service_client()

    existing = (
        client.table("departments")
        .select("department_id")
        .eq("name", payload.name)
        .execute()
    )

    if existing.data:
        raise HTTPException(
            status_code=409,
            detail="Department already exists",
        )

    result = (
        client.table("departments")
        .insert(
            {
                "name": payload.name,
                "description": payload.description,
            }
        )
        .execute()
    )

    return result.data[0]


# ---------------------------------------------------------------------------
# Update department
# HR ADMIN ONLY
# ---------------------------------------------------------------------------
@router.put("/{department_id}")
async def update_department(
    department_id: str,
    payload: DepartmentUpdate,
    user: CurrentUser = Depends(require_hr_admin),
):
    client = get_service_client()

    existing = (
        client.table("departments")
        .select("*")
        .eq("department_id", department_id)
        .execute()
    )

    if not existing.data:
        raise HTTPException(
            status_code=404,
            detail="Department not found",
        )

    duplicate = (
        client.table("departments")
        .select("department_id")
        .eq("name", payload.name)
        .neq("department_id", department_id)
        .execute()
    )

    if duplicate.data:
        raise HTTPException(
            status_code=409,
            detail="Another department already uses this name",
        )

    result = (
        client.table("departments")
        .update(
            {
                "name": payload.name,
                "description": payload.description,
            }
        )
        .eq("department_id", department_id)
        .execute()
    )

    return result.data[0]


# ---------------------------------------------------------------------------
# Delete department
# HR ADMIN ONLY
# ---------------------------------------------------------------------------
@router.delete("/{department_id}")
async def delete_department(
    department_id: str,
    user: CurrentUser = Depends(require_hr_admin),
):
    client = get_service_client()

    existing = (
        client.table("departments")
        .select("department_id")
        .eq("department_id", department_id)
        .execute()
    )

    if not existing.data:
        raise HTTPException(
            status_code=404,
            detail="Department not found",
        )

    client.table("departments").delete().eq(
        "department_id",
        department_id,
    ).execute()

    return {
        "status": "deleted",
        "department_id": department_id,
    }