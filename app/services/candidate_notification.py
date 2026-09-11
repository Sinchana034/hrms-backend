from app.services import gmail_client


def send_candidate_notification(
    candidate_name: str,
    candidate_email: str,
    position: str,
    subject: str,
    body: str,
):
    """
    Send a recruitment status notification email to a candidate, via the
    Gmail API using the connected HR mailbox (Section 6.2). Switched from
    SMTP because outbound SMTP ports are blocked on our hosting
    platform's free tier — the Gmail API is HTTPS-based and unaffected.
    """

    try:
        creds, account_email = gmail_client.get_ready_credentials("gmail")
    except RuntimeError:
        raise

    message_body = f"""
Hello {candidate_name},

{body}

Position: {position}

Regards,

HRMS Recruitment Team
"""

    try:
        gmail_client.send_email_message(
            creds,
            from_email=account_email,
            to_email=candidate_email,
            subject=subject,
            body_text=message_body,
        )
    except Exception as e:
        raise RuntimeError(
            f"Failed to send candidate notification email: {str(e)}"
        )