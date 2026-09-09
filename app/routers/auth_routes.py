from fastapi import APIRouter, Depends

from app.auth import CurrentUser, get_current_user
from app.database import get_service_client

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
async def me(user: CurrentUser = Depends(get_current_user)):
    return {
        "user_id": user.user_id,
        "email": user.email,
        "role": user.role,
        "mfa_verified_this_session": user.aal == "aal2",
    }


@router.post("/mfa/sync-status")
async def sync_mfa_status(user: CurrentUser = Depends(get_current_user)):
    """
    MFA enrollment itself happens client-side via the Supabase Auth SDK
    (supabase.auth.mfa.enroll / .challenge / .verify) — the frontend talks
    to Supabase directly for that, since it's Supabase's own auth flow, not
    application data (Section 4: only *external third-party* APIs must be
    backend-mediated).

    This endpoint just flips users.mfa_enabled to true once the frontend
    confirms a factor was verified, so /auth/me and the MFA-enforcement
    check in app.auth reflect it going forward.
    """
    client = get_service_client()
    client.table("users").update({"mfa_enabled": True}).eq("user_id", user.user_id).execute()
    return {"mfa_enabled": True}
