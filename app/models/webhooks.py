from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SuppressionEntryOut(BaseModel):
    email: str
    reason: str
    added_at: datetime
    cleared_at: Optional[datetime] = None
