from app.services import gmail_client


def send_assessment_email(
    candidate_name: str,
    candidate_email: str,
    position: str,
    assessment_url: str,
    expires_at,
):
    """
    Send assessment invitation email to candidate, via the Gmail API using
    the connected HR mailbox (Section 6.2). Switched from SMTP because
    outbound SMTP ports are blocked on our hosting platform's free tier —
    the Gmail API is HTTPS-based and unaffected.
    """

    try:
        creds, account_email = gmail_client.get_ready_credentials("gmail")
    except RuntimeError:
        raise

    subject = f"Assessment Invitation - {position}"

    body = f"""
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

    try:
        gmail_client.send_email_message(
            creds,
            from_email=account_email,
            to_email=candidate_email,
            subject=subject,
            body_text=body,
        )
    except Exception as e:
        raise RuntimeError(
            f"Failed to send assessment email: {str(e)}"
        )