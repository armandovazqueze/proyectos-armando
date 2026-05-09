"""
Bridge between the Telegram bot and tracker.db.
Reuses app/db.py — no SQL written here, no schema knowledge duplicated.
"""
import sys
from pathlib import Path

# Make 'app' importable when running from any working directory.
_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app import db  # noqa: E402  (import after sys.path fix)


def checkin_exists_today(date_str: str) -> bool:
    with db.get_connection() as conn:
        return db.checkin_exists(conn, date_str)


def fetch_activities_catalog() -> list[dict]:
    """Return active activities as plain dicts, ordered by category then name."""
    with db.get_connection() as conn:
        rows = db.fetch_activities(conn)
        return [dict(row) for row in rows]


def save_completed_checkin(data: dict) -> int:
    """
    Write a completed check-in to tracker.db and return the new checkin_id.

    Required keys in data:
        checkin_date, mood_score, energy_score, stress_score,
        meaningfulness_level, best_part_of_day, energy_drainer,
        selected_activity_ids (list[int], may be empty)
    """
    with db.get_connection() as conn:
        checkin_id = db.insert_checkin(conn, data)
        activity_ids = data.get("selected_activity_ids", [])
        if activity_ids:
            db.insert_checkin_activities(conn, checkin_id, activity_ids)
    return checkin_id
