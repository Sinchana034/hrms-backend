import re

from rapidfuzz import fuzz

from app.config import get_settings
from app.database import get_service_client


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _normalize_phone(phone: str | None) -> str | None:
    if not phone:
        return None
    digits = re.sub(r"\D", "", phone)
    # Compare on the last 10 digits so country-code prefixes (+91, 0, etc.)
    # don't produce false negatives.
    return digits[-10:] if len(digits) >= 10 else digits or None


def run_duplicate_check(application: dict) -> list[dict]:
    """
    Runs on every new application (Section 6.3). Matches on normalized
    email, phone, and fuzzy name against every other application. Creates
    duplicate_candidates rows for HR to resolve — never deletes or merges
    automatically.

    NOTE: this does a full-table compare, which is fine at Phase-2 volumes
    but should move to indexed normalized columns + a trigram/pg_trgm
    similarity query before candidate volume gets large (see README).
    """
    settings = get_settings()
    client = get_service_client()

    self_id = application["application_id"]
    self_email = _normalize_email(application["email"])
    self_phone = _normalize_phone(application.get("phone"))
    self_name = application["candidate_name"]

    others = (
        client.table("applications")
        .select("application_id,candidate_name,email,phone")
        .neq("application_id", self_id)
        .execute()
        .data
    )

    matches: dict[str, dict] = {}  # matched_application_id -> best match row

    for other in others:
        other_id = other["application_id"]
        other_email = _normalize_email(other["email"])
        other_phone = _normalize_phone(other.get("phone"))
        other_name = other["candidate_name"]

        if other_email == self_email:
            matches[other_id] = {"match_type": "email", "match_score": None}
            continue  # exact email match is the strongest signal, don't downgrade it

        if self_phone and other_phone and self_phone == other_phone:
            matches[other_id] = {"match_type": "phone", "match_score": None}
            continue

        name_score = fuzz.token_sort_ratio(self_name, other_name)
        if name_score >= settings.duplicate_fuzzy_name_threshold:
            matches[other_id] = {"match_type": "fuzzy_name", "match_score": round(name_score, 1)}

    created = []
    for other_id, match in matches.items():
        row = {
            "application_id": self_id,
            "matched_application_id": other_id,
            "match_type": match["match_type"],
            "match_score": match["match_score"],
        }
        # Unique constraint on (application_id, matched_application_id, match_type)
        # means a re-run is idempotent — duplicate inserts are skipped.
        result = (
            client.table("duplicate_candidates")
            .upsert(row, on_conflict="application_id,matched_application_id,match_type")
            .execute()
        )
        if result.data:
            created.append(result.data[0])

    if created:
        client.table("applications").update({"has_potential_duplicates": True}).eq(
            "application_id", self_id
        ).execute()
        client.table("applications").update({"has_potential_duplicates": True}).in_(
            "application_id", list(matches.keys())
        ).execute()

    return created
