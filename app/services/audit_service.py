from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import AuditLog

ACTION_SUBMITTED = "submitted"
ACTION_ROUTED = "routed"
ACTION_DECISION = "decision"
ACTION_STATUS_CHANGE = "status_change"


def log_action(
    db: Session,
    request_id: int,
    actor_id: Optional[int],
    action: str,
    old_status: Optional[str] = None,
    new_status: Optional[str] = None,
    note: Optional[str] = None,
) -> AuditLog:
    entry = AuditLog(
        request_id=request_id,
        actor_id=actor_id,
        action=action,
        old_status=old_status,
        new_status=new_status,
        note=note,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
