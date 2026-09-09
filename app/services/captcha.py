import httpx

from app.config import get_settings

TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"


class CaptchaError(Exception):
    pass


async def verify_captcha(token: str, remote_ip: str | None = None) -> bool:
    """
    Verifies a CAPTCHA token against the configured provider (Section 6.1).
    Returns True if verification passes. In staging with provider='none',
    always passes so local development isn't blocked.
    """
    settings = get_settings()

    if settings.captcha_provider == "none":
        if settings.is_production:
            raise CaptchaError("CAPTCHA provider must be configured in production")
        return True

    if not token:
        return False

    if settings.captcha_provider == "turnstile":
        url = TURNSTILE_VERIFY_URL
    elif settings.captcha_provider == "recaptcha_v3":
        url = RECAPTCHA_VERIFY_URL
    else:
        raise CaptchaError(f"Unknown captcha provider: {settings.captcha_provider}")

    payload = {"secret": settings.captcha_secret_key, "response": token}
    if remote_ip:
        payload["remoteip"] = remote_ip

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(url, data=payload)
        resp.raise_for_status()
        data = resp.json()

    return bool(data.get("success"))
