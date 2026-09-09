import uuid

from app.config import get_settings
from app.database import get_service_client

ALLOWED_CONTENT_TYPES = {
    "application/pdf": "pdf",
    "application/msword": "doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
}


class ResumeUploadError(Exception):
    pass


def validate_resume(content_type: str, size_bytes: int) -> str:
    """Returns the file extension if valid, raises ResumeUploadError otherwise."""
    settings = get_settings()

    ext = ALLOWED_CONTENT_TYPES.get(content_type)
    if not ext:
        raise ResumeUploadError("Only PDF, DOC, or DOCX resumes are accepted")

    max_bytes = settings.resume_max_size_mb * 1024 * 1024
    if size_bytes > max_bytes:
        raise ResumeUploadError(f"Resume must be under {settings.resume_max_size_mb}MB")

    return ext


def upload_resume(file_bytes: bytes, content_type: str) -> str:
    """
    Uploads a resume to the private Supabase Storage bucket (Section 14:
    'Resume files ... stored in private Supabase Storage buckets, signed
    URLs only'). Returns the storage path — NOT a public URL — which is
    what gets saved into applications.resume_url.
    """
    settings = get_settings()
    ext = validate_resume(content_type, len(file_bytes))

    # Random path, not derived from candidate-supplied name — avoids path
    # traversal / collisions and doesn't leak candidate identity in the path.
    storage_path = f"{uuid.uuid4()}.{ext}"

    client = get_service_client()
    client.storage.from_(settings.resume_storage_bucket).upload(
        path=storage_path,
        file=file_bytes,
        file_options={"content-type": content_type},
    )
    return storage_path


def download_resume(storage_path: str) -> bytes:
    """
    Download a private resume directly from Supabase Storage.

    This uses the service-role client, so the resume does not need
    to be publicly accessible.
    """
    settings = get_settings()
    client = get_service_client()

    try:
        return client.storage.from_(
            settings.resume_storage_bucket
        ).download(storage_path)

    except Exception as exc:
        raise RuntimeError(
            f"Failed to download resume from storage: {exc}"
        ) from exc

def get_resume_signed_url(storage_path: str) -> str:
    """HR-only: generate a short-lived signed URL to view a stored resume."""
    settings = get_settings()
    client = get_service_client()
    result = client.storage.from_(settings.resume_storage_bucket).create_signed_url(
        storage_path, settings.resume_signed_url_ttl_seconds
    )
    # supabase-py has returned either 'signedURL' or 'signedUrl' across
    # versions — handle both defensively.
    url = result.get("signedURL") or result.get("signedUrl")
    if not url:
        raise RuntimeError("Failed to generate signed URL for resume")
    return url
