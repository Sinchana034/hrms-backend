from typing import Optional

from app.database import get_service_client


def write_audit_log(
    *,
    action: str,
    role: str,                       # 'hr' | 'interviewer' | 'system'
    hr_user: Optional[str] = None,    # users.user_id, None for system-initiated actions
    candidate_id: Optional[str] = None,
    previous_status: Optional[str] = None,
    new_status: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> None:
    """
    Append-only audit trail (Section 12.16 / 19: failures are surfaced, never
    silent — but a failure to *write an audit log* itself should not break
    the primary action, so this swallows and logs to stdout as a fallback).
    """
    client = get_service_client()
    row = {
        "hr_user": hr_user,
        "role": role,
        "action": action,
        "candidate_id": candidate_id,
        "previous_status": previous_status,
        "new_status": new_status,
        "metadata": metadata or {},
    }
    try:
        client.table("audit_logs").insert(row).execute()
    except Exception as exc:  # noqa: BLE001 - audit logging must not crash the request
        print(f"[audit_logs] WRITE FAILED: {row} error={exc}")
