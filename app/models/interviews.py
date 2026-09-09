from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class InterviewCreate(BaseModel):
    application_id: UUID

    interview_type: str = "Technical"

    interviewer_name: Optional[str] = None
    interviewer_email: Optional[str] = None

    scheduled_at: Optional[datetime] = None

    duration_minutes: int = Field(
        default=60,
        ge=15,
        le=480,
    )

    meeting_link: Optional[str] = None

    notes: Optional[str] = None


class InterviewUpdate(BaseModel):
    interview_type: Optional[str] = None

    interviewer_name: Optional[str] = None
    interviewer_email: Optional[str] = None

    scheduled_at: Optional[datetime] = None

    duration_minutes: Optional[int] = Field(
        default=None,
        ge=15,
        le=480,
    )

    meeting_link: Optional[str] = None

    status: Optional[str] = None

    notes: Optional[str] = None


class InterviewOut(BaseModel):
    interview_id: UUID
    application_id: UUID

    interview_type: str

    interviewer_name: Optional[str]
    interviewer_email: Optional[str]

    scheduled_at: Optional[datetime]

    duration_minutes: int

    meeting_link: Optional[str]

    status: str

    notes: Optional[str]

    created_at: datetime
    updated_at: datetime