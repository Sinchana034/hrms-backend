import base64
import time
from datetime import datetime, timezone


from email.message import EmailMessage

from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build



from app.config import get_settings
from app.services.crypto import decrypt, encrypt

# Section 6.2: HR mailbox connected via Gmail API (OAuth2). Read-only scope
# is deliberately minimal — this system never sends from the HR mailbox
# via Gmail (candidate emails go out through the dedicated dispatch
# provider, Section 8), it only reads inbound applications.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]


def _flow() -> Flow:
    settings = get_settings()
    client_config = {
        "web": {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.google_oauth_redirect_uri],
        }
    }
    return Flow.from_client_config(
        client_config, scopes=SCOPES, redirect_uri=settings.google_oauth_redirect_uri
    )


def get_authorization_url(state: str | None = None) -> str:
    """HR-only: URL to send the admin to for Gmail consent (Section 3).
    state carries a signed token identifying which HR user initiated the
    connect flow, since Google's redirect back to our callback is a plain
    browser navigation with no Authorization header on it.
    """
    flow = _flow()
    kwargs = {
        "access_type": "offline",  # required to get a refresh_token
        "prompt": "consent",  # force refresh_token on re-auth too
        "include_granted_scopes": "true",
    }
    if state:
        kwargs["state"] = state
    url, _state = flow.authorization_url(**kwargs)
    return url


def exchange_code_for_credentials(code: str) -> Credentials:
    flow = _flow()
    flow.fetch_token(code=code)
    return flow.credentials


def credentials_to_account_row(creds: Credentials, connected_by: str) -> dict:
    """Encrypted fields ready to insert/update in email_accounts."""
    if not creds.refresh_token:
        raise ValueError(
            "Google did not return a refresh_token. This happens on re-consent "
            "without prompt=consent, or if offline access wasn't granted — "
            "revoke app access in the Google Account and reconnect."
        )
    return {
        "provider": "gmail",
        "account_email": _get_account_email(creds),
        "access_token_encrypted": encrypt(creds.token) if creds.token else None,
        "refresh_token_encrypted": encrypt(creds.refresh_token),
        "token_expires_at": creds.expiry.replace(tzinfo=timezone.utc).isoformat()
        if creds.expiry
        else None,
        "connected_by": connected_by,
    }


def _get_account_email(creds: Credentials) -> str:
    service = build("gmail", "v1", credentials=creds)
    profile = service.users().getProfile(userId="me").execute()
    return profile["emailAddress"]


def load_credentials(account_row: dict) -> tuple[Credentials, bool]:
    """
    Builds Credentials from a stored account row, refreshing the access
    token if expired. Returns (credentials, was_refreshed) — caller should
    persist the refreshed token back to the DB when was_refreshed is True.
    """
    settings = get_settings()
    creds = Credentials(
        token=decrypt(account_row["access_token_encrypted"])
        if account_row.get("access_token_encrypted")
        else None,
        refresh_token=decrypt(account_row["refresh_token_encrypted"]),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        scopes=SCOPES,
    )

    was_refreshed = False
    if not creds.valid:
        creds.refresh(GoogleAuthRequest())
        was_refreshed = True

    return creds, was_refreshed


def list_message_ids_since(creds: Credentials, since_unix: int) -> list[str]:
    """Poll-based sync: list inbox messages newer than the given timestamp."""
    service = build("gmail", "v1", credentials=creds)
    query = f"in:inbox after:{since_unix}"
    ids: list[str] = []
    page_token = None
    while True:
        resp = (
            service.users()
            .messages()
            .list(userId="me", q=query, pageToken=page_token, maxResults=50)
            .execute()
        )
        ids.extend(m["id"] for m in resp.get("messages", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return ids


def get_message(creds: Credentials, message_id: str) -> dict:
    service = build("gmail", "v1", credentials=creds)
    return service.users().messages().get(userId="me", id=message_id, format="full").execute()


def get_attachment_bytes(creds: Credentials, message_id: str, attachment_id: str) -> bytes:
    from app.services.email_parser import decode_base64url

    service = build("gmail", "v1", credentials=creds)
    attachment = (
        service.users()
        .messages()
        .attachments()
        .get(userId="me", messageId=message_id, id=attachment_id)
        .execute()
    )
    return decode_base64url(attachment["data"])


def now_unix() -> int:
    return int(time.time())

def send_email(
    creds: Credentials,
    to_email: str,
    subject: str,
    body: str,
):
    """Send an email using the Gmail API."""

    message = EmailMessage()

    message["To"] = to_email
    message["Subject"] = subject

    message.set_content(body)

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    service = build(
        "gmail",
        "v1",
        credentials=creds,
    )

    return (
        service
        .users()
        .messages()
        .send(
            userId="me",
            body={
                "raw": encoded_message
            },
        )
        .execute()
    )
