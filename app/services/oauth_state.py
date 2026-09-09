from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.config import get_settings

ALGORITHM = "HS256"


class OAuthStateError(Exception):
    pass


def _secret() -> str:
    settings = get_settings()
    # Falls back to the Supabase JWT secret so this doesn't need its own
    # env var in the common case — it's fine to share since both are
    # backend-only HMAC secrets with no external exposure.
    return settings.oauth_state_secret or settings.supabase_jwt_secret


def create_state_token(user_id: str) -> str:
    """
    Signed, 10-minute token carrying the initiating HR user's id through
    the OAuth redirect round-trip (Google's callback is a plain browser
    GET with no Authorization header, so we can't rely on the session).
    """
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=10),
    }
    return jwt.encode(payload, _secret(), algorithm=ALGORITHM)


def verify_state_token(token: str) -> str:
    try:
        payload = jwt.decode(token, _secret(), algorithms=[ALGORITHM])
    except JWTError:
        raise OAuthStateError("Invalid or expired OAuth state token")
    return payload["sub"]
