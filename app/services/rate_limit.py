import re
import time
from collections import defaultdict
from threading import Lock

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import get_settings

# Per-IP limiting (Section 6.1) — backs the public application-intake endpoint.
limiter = Limiter(key_func=get_remote_address)


class _PerEmailLimiter:
    """
    In-memory per-email submission cap. Fine for a single backend instance;
    once the system runs multiple workers (Celery/Redis is already planned
    per Section 5), swap this for a Redis-backed counter with the same
    interface so no caller code has to change.
    """

    def __init__(self):
        self._hits: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    @staticmethod
    def _parse_rate(rate: str) -> tuple[int, int]:
        # e.g. "3/hour" -> (3, 3600)
        count_str, _, period = rate.partition("/")
        count = int(count_str)
        seconds = {"second": 1, "minute": 60, "hour": 3600, "day": 86400}[period]
        return count, seconds

    def check(self, email: str, rate: str) -> bool:
        limit, window = self._parse_rate(rate)
        now = time.time()
        key = email.lower()
        with self._lock:
            hits = [t for t in self._hits[key] if now - t < window]
            if len(hits) >= limit:
                self._hits[key] = hits
                return False
            hits.append(now)
            self._hits[key] = hits
            return True


per_email_limiter = _PerEmailLimiter()


def check_email_rate_limit(email: str) -> bool:
    settings = get_settings()
    return per_email_limiter.check(email, settings.rate_limit_applications_per_email)
