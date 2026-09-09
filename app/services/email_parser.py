import base64
import re
from email.utils import parseaddr

# Section 6.2: "subject/body → parsed for name and position". This is a
# best-effort heuristic, not a guarantee — anything it can't confidently
# extract is left null and HR fills it in from the Applications view.
# Keep this in one place so it's easy to improve without touching the
# Gmail/Outlook-specific sync code.

_POSITION_PATTERNS = [
    re.compile(r"applying for(?: the)?\s*[:\-]?\s*(.+)", re.IGNORECASE),
    re.compile(r"application for(?: the)?\s*[:\-]?\s*(.+)", re.IGNORECASE),
    re.compile(r"position\s*[:\-]\s*(.+)", re.IGNORECASE),
    re.compile(r"role\s*[:\-]\s*(.+)", re.IGNORECASE),
]

_DEPARTMENT_PATTERN = re.compile(r"department\s*[:\-]\s*(.+)", re.IGNORECASE)

ALLOWED_RESUME_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def parse_sender(from_header: str) -> tuple[str, str]:
    """Returns (name, email) from an RFC 2822 'From' header."""
    name, email = parseaddr(from_header)
    email = (email or "").strip().lower()
    if not name:
        # Fall back to the email local-part, title-cased, as a display name.
        name = email.split("@")[0].replace(".", " ").replace("_", " ").title() if email else ""
    return name.strip(), email


def _first_match(patterns: list[re.Pattern], text: str) -> str | None:
    for pattern in patterns:
        m = pattern.search(text)
        if m:
            value = m.group(1).strip().splitlines()[0].strip(" .,-")
            if value:
                return value[:200]
    return None


def extract_position(subject: str, body: str) -> str | None:
    return _first_match(_POSITION_PATTERNS, subject) or _first_match(_POSITION_PATTERNS, body)


def extract_department(body: str) -> str | None:
    m = _DEPARTMENT_PATTERN.search(body)
    return m.group(1).strip()[:100] if m else None


def decode_base64url(data: str) -> bytes:
    """Gmail API bodies/attachments are base64url without padding."""
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded)


def extract_gmail_body_text(payload: dict) -> str:
    """
    Walks a Gmail API message payload (MIME tree) and concatenates any
    text/plain parts. Falls back to an empty string rather than raising —
    a body we can't parse just means position/department stay null.
    """
    text_parts: list[str] = []

    def walk(part: dict):
        mime_type = part.get("mimeType", "")
        body_data = part.get("body", {}).get("data")
        if mime_type == "text/plain" and body_data:
            try:
                text_parts.append(decode_base64url(body_data).decode("utf-8", errors="replace"))
            except Exception:  # noqa: BLE001 - best-effort parsing
                pass
        for sub in part.get("parts", []) or []:
            walk(sub)

    walk(payload)
    return "\n".join(text_parts)


def extract_gmail_attachments(payload: dict) -> list[dict]:
    """
    Returns [{filename, mime_type, attachment_id, size}] for every part
    that has a filename — i.e. is an attachment, not inline body content.
    """
    attachments: list[dict] = []

    def walk(part: dict):
        filename = part.get("filename")
        body = part.get("body", {})
        if filename and body.get("attachmentId"):
            attachments.append(
                {
                    "filename": filename,
                    "mime_type": part.get("mimeType", "application/octet-stream"),
                    "attachment_id": body["attachmentId"],
                    "size": body.get("size", 0),
                }
            )
        for sub in part.get("parts", []) or []:
            walk(sub)

    walk(payload)
    return attachments


def pick_resume_attachment(attachments: list[dict]) -> dict | None:
    """First attachment with an allowed resume MIME type, or None."""
    for a in attachments:
        if a["mime_type"] in ALLOWED_RESUME_TYPES:
            return a
    return None
