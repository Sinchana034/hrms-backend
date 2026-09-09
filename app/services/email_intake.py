import logging

from app.database import get_service_client
from app.services.application_intake import EMAIL_INTAKE_CONSENT_VERSION, create_application
from app.services.email_parser import (
    extract_department,
    extract_gmail_attachments,
    extract_gmail_body_text,
    extract_position,
    parse_sender,
    pick_resume_attachment,
)
from app.services.gmail_client import get_attachment_bytes, get_message
from app.services.storage import ResumeUploadError, upload_resume

logger = logging.getLogger(__name__)


def _already_ingested(message_id: str) -> bool:
    client = get_service_client()
    result = (
        client.table("applications")
        .select("application_id")
        .eq("email_metadata->>message_id", message_id)
        .execute()
    )
    return bool(result.data)


def ingest_gmail_message(creds, message_id: str) -> dict | None:
    """
    Fetches, parses, and stores one Gmail message as an application
    (Section 6.2). Returns the created application row, or None if the
    message was skipped (already ingested, no candidate email, etc.) —
    skips are not errors, they're logged and counted by the caller.
    """
    if _already_ingested(message_id):
        return None

    message = get_message(creds, message_id)
    payload = message.get("payload", {})
    headers = {h["name"].lower(): h["value"] for h in payload.get("headers", [])}

    from_header = headers.get("from", "")
    candidate_name, candidate_email = parse_sender(from_header)
    if not candidate_email:
        logger.warning("Skipping Gmail message %s: no parseable sender email", message_id)
        return None

    subject = headers.get("subject", "")
    body = extract_gmail_body_text(payload)

    resume_path = None
    attachments = extract_gmail_attachments(payload)
    resume_attachment = pick_resume_attachment(attachments)
    if resume_attachment:
        try:
            file_bytes = get_attachment_bytes(creds, message_id, resume_attachment["attachment_id"])
            resume_path = upload_resume(file_bytes, resume_attachment["mime_type"])
        except ResumeUploadError as e:
            logger.warning("Resume attachment on message %s rejected: %s", message_id, e)
        except Exception:  # noqa: BLE001
            logger.warning("Failed to fetch/store resume attachment on message %s", message_id, exc_info=True)

    row = {
        "candidate_name": candidate_name or candidate_email.split("@")[0],
        "email": candidate_email,
        "phone": None,
        # Section 6.2 extraction is best-effort — HR fills gaps from the
        # Applications view rather than the message being rejected outright.
        "department": extract_department(body) or "Unspecified",
        "position": extract_position(subject, body) or "Unspecified",
        "source": "EMAIL",
        "resume_url": resume_path,
        "education": [],
        "skills": [],
        "experience": [],
        "projects": [],
        "portfolio": None,
        "github": None,
        "linkedin": None,
        "current_status": "Application Received",
        "consent_version": EMAIL_INTAKE_CONSENT_VERSION,
        "email_metadata": {
            "message_id": message_id,
            "thread_id": message.get("threadId"),
            "subject": subject,
            "from": from_header,
        },
    }

    return create_application(row)
