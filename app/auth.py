from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
import httpx

from app.config import get_settings
from app.database import get_service_client

bearer_scheme = HTTPBearer(auto_error=True)


@dataclass
class CurrentUser:
    user_id: str
    email: str
    role: str          # 'hr_admin' | 'interviewer'
    aal: str            # 'aal1' | 'aal2' — Supabase auth assurance level


def _decode_token(token: str) -> dict:
    settings = get_settings()

    try:
        jwks = httpx.get(
            f"{settings.supabase_url}/auth/v1/.well-known/jwks.json",
            timeout=5.0,
        ).json()

        header = jwt.get_unverified_header(token)
        kid = header.get("kid")

        key = next(
            (k for k in jwks["keys"] if k.get("kid") == kid),
            None,
        )

        if not key:
            raise JWTError("Signing key not found")

        return jwt.decode(
            token,
            key,
            algorithms=["ES256"],
            audience="authenticated",
        )

    except (JWTError, httpx.HTTPError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> CurrentUser:
    payload = _decode_token(creds.credentials)
    user_id = payload.get("sub")
    email = payload.get("email", "")
    aal = payload.get("aal", "aal1")

    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing subject")

    # Look up app-level role from the users table (service client — this is
    # an internal lookup, not exposing the service key to the caller).
    client = get_service_client()
    result = client.table("users") \
    .select("role, mfa_enabled") \
    .eq("user_id", user_id) \
    .maybe_single() \
    .execute()

    if not result.data:
        raise HTTPException(status_code=403, detail="No HRMS profile for this account")

    

    role = result.data["role"]
    mfa_enabled = result.data["mfa_enabled"]

    # Section 14: mandatory MFA for HR/Admin, enforced at login. If the
    # profile says MFA is enabled but this session's token is only aal1,
    # the user authenticated with password only and must step up.
    if role == "hr_admin" and mfa_enabled and aal != "aal2":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="MFA verification required (aal2) for HR/Admin access",
        )

    return CurrentUser(user_id=user_id, email=email, role=role, aal=aal)


def require_role(*allowed_roles: str):
    async def _dependency(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient role for this action")
        return user

    return _dependency


require_hr_admin = require_role("hr_admin")
require_any_staff = require_role("hr_admin", "interviewer")
