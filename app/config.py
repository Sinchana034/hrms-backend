from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    supabase_jwt_secret: str

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    email_from: str = ""

    captcha_provider: str = "none"
    captcha_secret_key: str = ""

    resume_storage_bucket: str = "resumes"
    resume_max_size_mb: int = 5
    resume_signed_url_ttl_seconds: int = 600  # 10 min, HR-facing view link

    # Section 6.2 — email ingestion. Provider choice is an open decision
    # (Section 27); 'none' disables sync entirely so the rest of the app
    # runs fine before that's confirmed.
    email_sync_provider: str = "none"  # 'gmail' | 'outlook' | 'none'
    encryption_key: str = ""  # Fernet key — encrypts OAuth tokens at rest

    google_client_id: str = ""
    google_client_secret: str = ""
    google_oauth_redirect_uri: str = "http://localhost:8000/email-sync/gmail/callback"
    oauth_state_secret: str = ""  # falls back to supabase_jwt_secret if unset
    frontend_url: str = "https://hrms-frontend-snowy-three.vercel.app"  # where /gmail/callback redirects after connecting

    # Section 10 — bounce/complaint webhook (SendGrid event webhook format)
    sendgrid_webhook_verification_key: str = ""  # optional, skip signature check if unset

    # Section 6.3 — duplicate detection
    duplicate_fuzzy_name_threshold: int = 90  # rapidfuzz similarity score, 0-100

    environment: str = "staging"
    allowed_origins: str = "http://localhost:5173,http://192.168.0.147:5173"

    rate_limit_applications_per_ip: str = "5/minute"
    rate_limit_applications_per_email: str = "3/hour"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
