from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, model_validator


class DuplicateApplicationSummary(BaseModel):
    application_id: UUID
    candidate_name: str
    email: str
    phone: Optional[str]
    current_status: str


class DuplicateCandidateOut(BaseModel):
    duplicate_id: UUID
    application: DuplicateApplicationSummary
    matched_application: DuplicateApplicationSummary
    match_type: str
    match_score: Optional[float]
    status: str
    resolution: Optional[str]
    created_at: datetime


class ResolveDuplicateRequest(BaseModel):
    resolution: str  # 'merge' | 'keep_separate' | 'mark_duplicate'
    # Required for 'merge' and 'mark_duplicate': which of the pair is kept
    # as the canonical record. Must be one of the two application_ids on
    # the duplicate_candidates row being resolved.
    canonical_application_id: Optional[UUID] = None

    @model_validator(mode="after")
    def check_canonical_required(self):
        if self.resolution in ("merge", "mark_duplicate") and not self.canonical_application_id:
            raise ValueError(
                f"canonical_application_id is required when resolution='{self.resolution}'"
            )
        if self.resolution not in ("merge", "keep_separate", "mark_duplicate"):
            raise ValueError("resolution must be one of: merge, keep_separate, mark_duplicate")
        return self
