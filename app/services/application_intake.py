import logging

from app.database import get_service_client
from app.services.audit import write_audit_log
from app.services.duplicate_detection import run_duplicate_check
from app.services.resume_parser import parse_resume
from app.services.storage import download_resume

logger = logging.getLogger(__name__)


EMAIL_INTAKE_CONSENT_VERSION = (
    "n/a-email-intake-pending-legal-review"
)


def create_application(row: dict) -> dict:
    """
    Shared insert path for website and email applications.

    After the application is inserted, if a resume exists,
    parse the resume and save the extracted candidate data.
    """

    client = get_service_client()

    # ---------------------------------------------------------
    # 1. Create application
    # ---------------------------------------------------------

    result = (
        client
        .table("applications")
        .insert(row)
        .execute()
    )

    if not result.data:
        raise RuntimeError(
            "Failed to save application"
        )

    created = result.data[0]

    application_id = created["application_id"]

    # ---------------------------------------------------------
    # 2. Audit log
    # ---------------------------------------------------------

    write_audit_log(
        action="application_submitted",
        role="system",
        candidate_id=created["candidate_id"],
        new_status=created["current_status"],
        metadata={
            "source": row["source"],
            "application_id": application_id,
        },
    )

    # ---------------------------------------------------------
    # 3. Duplicate detection
    # ---------------------------------------------------------

    try:

        run_duplicate_check(created)

    except Exception:
        logger.warning(
            "Duplicate check failed for application %s",
            application_id,
            exc_info=True,
        )

    # ---------------------------------------------------------
    # 4. Parse resume
    # ---------------------------------------------------------

    resume_path = created.get("resume_url")

    if resume_path:

        try:

            logger.info(
                "Parsing resume for application %s",
                application_id,
            )

            resume_bytes = download_resume(
                resume_path
            )

            parsed = parse_resume(
                resume_bytes,
                resume_path,
            )

            # -------------------------------------------------
            # 5. Save extracted resume information
            # -------------------------------------------------

            update_data = {
                "education": parsed["education"],
                "skills": parsed["skills"],
                "experience": parsed["experience"],
                "projects": parsed["projects"],
            }

            update_result = (
                client
                .table("applications")
                .update(update_data)
                .eq(
                    "application_id",
                    application_id,
                )
                .execute()
            )

            if update_result.data:

                created = update_result.data[0]

                logger.info(
                    "Resume parsed successfully for application %s. "
                    "Skills detected: %s",
                    application_id,
                    parsed["skills"],
                )

        except Exception:

            # Resume parsing should not destroy the application.
            # The application is already saved, so HR can retry
            # evaluation later.
            logger.warning(
                "Resume parsing failed for application %s",
                application_id,
                exc_info=True,
            )

    return created