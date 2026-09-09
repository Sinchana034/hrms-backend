import smtplib

from email.message import EmailMessage

from app.config import get_settings


def send_candidate_notification(
    candidate_name: str,
    candidate_email: str,
    position: str,
    subject: str,
    body: str,
):
    """
    Send a recruitment status notification email to a candidate.

    This uses the same SMTP configuration as assessment emails.
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

    message["Subject"] = subject
    message["From"] = from_email
    message["To"] = candidate_email

    message.set_content(
        f"""
Hello {candidate_name},

{body}

Position: {position}

Regards,

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
            f"Failed to send candidate notification email: {str(e)}"
        )