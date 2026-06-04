from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    id: int
    request_id: int
    actor_id: Optional[int]
    action: str
    old_status: Optional[str]
    new_status: Optional[str]
    note: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
