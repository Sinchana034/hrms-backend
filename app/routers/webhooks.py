from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from app.auth import CurrentUser, require_hr_admin
from app.config import get_settings
from app.database import get_service_client
from app.models.webhooks import SuppressionEntryOut
from app.services.audit import write_audit_log

router = APIRouter(tags=["webhooks"])

# SendGrid event webhook types that mean "stop sending to this address"
# (Section 10: hard bounce / complaint → suppression, never auto-retried).
HARD_BOUNCE_EVENTS = {"bounce", "dropped"}
COMPLAINT_EVENTS = {"spamreport"}


@router.post("/webhooks/email-bounce", status_code=204)
async def email_bounce_webhook(
    request: Request, x_webhook_secret: str | None = Header(default=None)
):
    """
    Receives bounce/complaint events from the email dispatch provider
    (Section 10). Written for SendGrid's event webhook payload shape
    (a JSON array of event objects) since that's the most common
    dispatch provider for this stack — adapt the per-event parsing below
    if a different provider is used.

    NOTE on verification: this checks a shared-secret header rather than
    SendGrid's ECDSA signed-webhook scheme. That's a real gap for
    production (a leaked/guessed secret lets someone forge bounce events
    and silently suppress candidate addresses) — implement provider-signature
    verification before go-live if SendGrid is the confirmed provider
    (Section 27 still has the dispatch provider as partially open).
    """
    settings = get_settings()
    if settings.sendgrid_webhook_verification_key:
        if x_webhook_secret != settings.sendgrid_webhook_verification_key:
            raise HTTPException(status_code=401, detail="Invalid webhook credentials")

    events = await request.json()
    if not isinstance(events, list):
        events = [events]

    client = get_service_client()

    for event in events:
        email = (event.get("email") or "").strip().lower()
        event_type = event.get("event")
        reason = event.get("reason") or event.get("response") or event_type
        if not email or not event_type:
            continue

        if event_type in HARD_BOUNCE_EVENTS:
            bounce_type = "hard"
        elif event_type in COMPLAINT_EVENTS:
            bounce_type = "complaint"
        else:
            continue  # soft bounces/deferrals/opens/clicks etc. — not suppression-worthy

        client.table("applications").update(
            {
                "email_bounced": True,
                "email_bounce_reason": reason,
            }
        ).eq("email", email).execute()

        client.table("suppression_list").upsert(
            {
                "email": email,
                "reason": bounce_type,
                "added_at": datetime.now(timezone.utc).isoformat(),
                "cleared_at": None,
                "cleared_by": None,
            },
            on_conflict="email",
        ).execute()

        write_audit_log(
            action="email_bounced",
            role="system",
            metadata={"email": email, "bounce_type": bounce_type, "reason": reason},
        )

    return None


@router.get("/suppression-list", response_model=list[SuppressionEntryOut])
async def list_suppressions(user: CurrentUser = Depends(require_hr_admin)):
    client = get_service_client()
    result = (
        client.table("suppression_list")
        .select("*")
        .is_("cleared_at", "null")
        .order("added_at", desc=True)
        .execute()
    )
    return result.data


@router.post("/suppression-list/{email}/clear")
async def clear_suppression(email: str, user: CurrentUser = Depends(require_hr_admin)):
    client = get_service_client()
    result = (
        client.table("suppression_list")
        .update(
            {
                "cleared_at": datetime.now(timezone.utc).isoformat(),
                "cleared_by": str(user.user_id),
            }
        )
        .eq("email", email.strip().lower())
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Email not found in suppression list")

    write_audit_log(
        action="suppression_cleared",
        role="hr",
        hr_user=user.user_id,
        metadata={"email": email},
    )
    return {"status": "cleared", "email": email}
