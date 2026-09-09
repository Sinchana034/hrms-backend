import smtplib

from email.message import EmailMessage

from app.config import get_settings


def send_assessment_email(
    candidate_name: str,
    candidate_email: str,
    position: str,
    assessment_url: str,
    expires_at,
):
    """
    Send assessment invitation email to candidate.
    """

    settings = get_settings()

    smtp_host = settings.smtp_host
    smtp_port = settings.smtp_port
    smtp_username = settings.smtp_username
    smtp_password = settings.smtp_password
    from_email = settings.email_from or smtp_username

    if not smtp_username or not smtp_password:
        raise RuntimeError(
            "SMTP email configuration is missing"
        )

    message = EmailMessage()

    message["Subject"] = (
        f"Assessment Invitation - {position}"
    )

    message["From"] = from_email
    message["To"] = candidate_email

    message.set_content(
        f"""
Hello {candidate_name},

Congratulations!

You have been shortlisted for the {position} position.

As the next step in our recruitment process,
please complete the assessment using the link below:

{assessment_url}

This assessment link is valid until:

{expires_at}

Please complete the assessment before the link expires.

There is no account or password required.

Good luck!

HRMS Recruitment Team
"""
    )

    try:
        with smtplib.SMTP(
            smtp_host,
            smtp_port
        ) as server:

            server.starttls()

            server.login(
                smtp_username,
                smtp_password
            )

            server.send_message(message)

    except Exception as e:
        raise RuntimeError(
            f"Failed to send assessment email: {str(e)}"
        )