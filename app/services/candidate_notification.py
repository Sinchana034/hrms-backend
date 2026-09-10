from app.database import get_service_client
from app.services.gmail_client import (
    load_credentials,
    send_email,
)


def send_candidate_notification(
    candidate_name: str,
    candidate_email: str,
    position: str,
    subject: str,
    body: str,
):
    """
    Send a recruitment status notification using Gmail API.
    """

    try:
        client = get_service_client()

        # Get the connected Gmail account
        result = (
            client
            .table("email_accounts")
            .select("*")
            .eq("provider", "gmail")
            .execute()
        )

        if not result.data:
            raise RuntimeError(
                "No Gmail account connected."
            )

        account = result.data[0]

        # Load stored OAuth credentials
        creds, was_refreshed = load_credentials(
            account
        )

        # Send candidate notification
        email_body = f"""
Hello {candidate_name},

{body}

Position: {position}

Regards,
HRMS Recruitment Team
"""

        send_email(
            creds=creds,
            to_email=candidate_email,
            subject=subject,
            body=email_body,
        )

        # Save refreshed access token if needed
        if was_refreshed:
            from app.services.crypto import encrypt

            (
                client
                .table("email_accounts")
                .update(
                    {
                        "access_token_encrypted": encrypt(
                            creds.token
                        )
                    }
                )
                .eq(
                    "id",
                    account["id"]
                )
                .execute()
            )

    except Exception as e:
        raise RuntimeError(
            f"Failed to send candidate notification email: {str(e)}"
        )