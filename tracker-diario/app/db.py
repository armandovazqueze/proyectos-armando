"""
Database access layer.
All functions receive an open sqlite3.Connection and execute a single
responsibility. Connection lifecycle is managed by get_connection().
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

# tracker.db lives at the project root (parent of the app/ folder)
DB_PATH = Path(__file__).parent.parent / "tracker.db"


@contextmanager
def get_connection():
    """
    Yield an open connection, commit on clean exit, rollback on exception.
    Always enables foreign-key enforcement.
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def checkin_exists(conn: sqlite3.Connection, date: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM daily_checkins WHERE checkin_date = ?", (date,)
    ).fetchone()
    return row is not None


def fetch_activities(conn: sqlite3.Connection) -> list:
    return conn.execute(
        """
        SELECT id, activity_name, activity_category
        FROM   activities
        WHERE  active = 1
        ORDER  BY activity_category, activity_name
        """
    ).fetchall()


def insert_checkin(conn: sqlite3.Connection, data: dict) -> int:
    cursor = conn.execute(
        """
        INSERT INTO daily_checkins
            (checkin_date, mood_score, energy_score, stress_score,
             meaningfulness_level, best_part_of_day, energy_drainer)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["checkin_date"],
            data["mood_score"],
            data["energy_score"],
            data["stress_score"],
            data["meaningfulness_level"],
            data["best_part_of_day"],
            data["energy_drainer"],
        ),
    )
    return cursor.lastrowid


def insert_checkin_activities(
    conn: sqlite3.Connection, checkin_id: int, activity_ids: list
):
    conn.executemany(
        "INSERT INTO checkin_activities (checkin_id, activity_id) VALUES (?, ?)",
        [(checkin_id, aid) for aid in activity_ids],
    )


def fetch_activity_names(conn: sqlite3.Connection, activity_ids: list) -> list:
    """Return activity names in the same order as activity_ids."""
    if not activity_ids:
        return []
    placeholders = ",".join("?" * len(activity_ids))
    rows = conn.execute(
        f"SELECT id, activity_name FROM activities WHERE id IN ({placeholders})",
        activity_ids,
    ).fetchall()
    id_to_name = {row["id"]: row["activity_name"] for row in rows}
    return [id_to_name[aid] for aid in activity_ids if aid in id_to_name]
