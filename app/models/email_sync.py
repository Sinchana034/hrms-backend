from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EmailAuthUrlOut(BaseModel):
    authorization_url: str


class EmailAccountStatusOut(BaseModel):
    connected: bool
    provider: Optional[str] = None
    account_email: Optional[str] = None
    is_active: Optional[bool] = None
    last_synced_at: Optional[datetime] = None


class EmailSyncResultOut(BaseModel):
    messages_seen: int
    applications_created: int
    skipped: int
    errors: int
