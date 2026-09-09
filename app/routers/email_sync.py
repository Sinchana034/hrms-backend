import logging
from datetime import timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse

from app.auth import CurrentUser, require_hr_admin
from app.config import get_settings
from app.database import get_service_client
from app.models.email_sync import EmailAccountStatusOut, EmailAuthUrlOut, EmailSyncResultOut
from app.services import gmail_client
from app.services.audit import write_audit_log
from app.services.crypto import encrypt
from app.services.email_intake import ingest_gmail_message
from app.services.oauth_state import OAuthStateError, create_state_token, verify_state_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/email-sync", tags=["email-sync"])

DEFAULT_FIRST_SYNC_LOOKBACK_SECONDS = 30 * 24 * 60 * 60  # 30 days


def _get_active_account(provider: str) -> dict | None:
    client = get_service_client()
    result = (
        client.table("email_accounts")
        .select("*")
        .eq("provider", provider)
        .eq("is_active", True)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


@router.get("/status", response_model=EmailAccountStatusOut)
async def email_sync_status(user: CurrentUser = Depends(require_hr_admin)):
    account = _get_active_account("gmail")
    if not account:
        return {"connected": False}
    return {
        "connected": True,
        "provider": account["provider"],
        "account_email": account["account_email"],
        "is_active": account["is_active"],
        "last_synced_at": account.get("updated_at"),
    }


# ---------------------------------------------------------------------------
# Gmail OAuth (Section 6.2, Section 14: credentials encrypted at rest,
# backend-only). Outlook/Graph is a documented open decision (Section 27)
# and isn't implemented — see /email-sync/outlook/connect below.
# ---------------------------------------------------------------------------
@router.get("/gmail/connect", response_model=EmailAuthUrlOut)
async def gmail_connect(user: CurrentUser = Depends(require_hr_admin)):
    settings = get_settings()
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(
            status_code=503,
            detail="Gmail integration is not configured (set GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET)",
        )
    state = create_state_token(str(user.user_id))
    url = gmail_client.get_authorization_url(state=state)
    return {"authorization_url": url}


@router.get("/gmail/callback")
async def gmail_callback(code: str = Query(...), state: str = Query(...)):
    settings = get_settings()

    try:
        user_id = verify_state_token(state)
    except OAuthStateError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        creds = gmail_client.exchange_code_for_credentials(code)
        account_row = gmail_client.credentials_to_account_row(creds, connected_by=user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    client = get_service_client()
    # Only one active mailbox connection at a time (Section 3: single HR mailbox).
    client.table("email_accounts").update({"is_active": False}).eq("provider", "gmail").eq(
        "is_active", True
    ).execute()
    client.table("email_accounts").insert(account_row).execute()

    write_audit_log(
        action="email_account_connected",
        role="hr",
        hr_user=user_id,
        metadata={"provider": "gmail", "account_email": account_row["account_email"]},
    )

    return RedirectResponse(url=f"{settings.frontend_url}/settings/email?connected=1")


@router.get("/outlook/connect")
async def outlook_connect(user: CurrentUser = Depends(require_hr_admin)):
    # Section 27: "Confirm HR mailbox provider (Gmail vs Outlook)" is still
    # an open decision. Endpoint shape is reserved so adding Graph API
    # support later doesn't change the frontend's integration contract.
    raise HTTPException(status_code=501, detail="Outlook/Microsoft Graph integration is not implemented yet")


# ---------------------------------------------------------------------------
# Manual sync trigger. Periodic polling (Celery beat) is a later-phase
# addition once Celery/Redis is running — see README.
# ---------------------------------------------------------------------------
@router.post("/gmail/sync", response_model=EmailSyncResultOut)
async def gmail_sync(user: CurrentUser = Depends(require_hr_admin)):
    account = _get_active_account("gmail")
    if not account:
        raise HTTPException(status_code=400, detail="No Gmail account connected. Connect one first.")

    creds, was_refreshed = gmail_client.load_credentials(account)
    client = get_service_client()

    if was_refreshed:
        client.table("email_accounts").update(
            {
                "access_token_encrypted": encrypt(creds.token),
                "token_expires_at": creds.expiry.replace(tzinfo=timezone.utc).isoformat()
                if creds.expiry
                else None,
            }
        ).eq("account_id", account["account_id"]).execute()

    since_unix = (
        int(account["sync_cursor"])
        if account.get("sync_cursor")
        else gmail_client.now_unix() - DEFAULT_FIRST_SYNC_LOOKBACK_SECONDS
    )

    message_ids = gmail_client.list_message_ids_since(creds, since_unix)

    created_count = 0
    skipped_count = 0
    error_count = 0

    for message_id in message_ids:
        try:
            created = ingest_gmail_message(creds, message_id)
            if created:
                created_count += 1
            else:
                skipped_count += 1
        except Exception:  # noqa: BLE001 — one bad message shouldn't abort the batch
            error_count += 1
            logger.warning("Failed to ingest Gmail message %s", message_id, exc_info=True)

    client.table("email_accounts").update({"sync_cursor": str(gmail_client.now_unix())}).eq(
        "account_id", account["account_id"]
    ).execute()

    write_audit_log(
        action="email_sync_run",
        role="hr",
        hr_user=user.user_id,
        metadata={
            "provider": "gmail",
            "messages_seen": len(message_ids),
            "applications_created": created_count,
            "skipped": skipped_count,
            "errors": error_count,
        },
    )

    return {
        "messages_seen": len(message_ids),
        "applications_created": created_count,
        "skipped": skipped_count,
        "errors": error_count,
    }
