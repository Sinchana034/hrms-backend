from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

CURRENT_CONSENT_VERSION = "v1.0-2026-08"  # bump when consent text changes (Section 16)


class ApplicationCreate(BaseModel):
    """Public website application-intake payload (Section 6.1)."""

    candidate_name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=30)

    department: str
    position: str

    resume_url: Optional[str] = None  # storage path returned by POST /applications/resume-upload
    education: list = Field(default_factory=list)
    skills: list = Field(default_factory=list)
    experience: list = Field(default_factory=list)
    projects: list = Field(default_factory=list)

    portfolio: Optional[str] = None
    github: Optional[str] = None
    linkedin: Optional[str] = None

    consent_given: bool = Field(..., description="Mandatory consent checkbox on the form")
    captcha_token: str


class ApplicationOut(BaseModel):
    application_id: UUID
    candidate_id: UUID
    candidate_name: str
    email: str
    phone: Optional[str]
    department: str
    position: str
    source: str
    application_date: datetime
    resume_url: Optional[str]
    current_status: str
    email_bounced: bool
    has_potential_duplicates: bool = False
    consent_version: str
    consented_at: datetime
    withdrawn_at: Optional[datetime]
    created_at: datetime


class ApplicationListFilters(BaseModel):
    status: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    source: Optional[str] = None
    email_bounced: Optional[bool] = None


class WithdrawRequest(BaseModel):
    reason: Optional[str] = None


class ResumeUploadOut(BaseModel):
    resume_path: str  # storage path — pass this back as resume_url on submit


class ResumeSignedUrlOut(BaseModel):
    url: str
    expires_in_seconds: int
