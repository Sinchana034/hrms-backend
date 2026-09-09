from functools import lru_cache

from supabase import create_client, Client

from app.config import get_settings


@lru_cache
def get_service_client() -> Client:
    """
    Backend-only client using the service role key. Bypasses RLS.
    Never expose this key or client to the frontend (Section 4: 'backend
    is the only component that talks to external APIs and holds credentials').
    """
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_service_role_key)
