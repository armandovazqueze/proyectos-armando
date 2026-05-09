import sqlite3
from pathlib import Path

import pandas as pd

_DB_NAME = "tracker.db"


def get_db_path() -> Path:
    return Path(__file__).parent.parent / _DB_NAME


def db_exists() -> bool:
    return get_db_path().exists()


def load_checkins_with_activities() -> pd.DataFrame:
    """One row per check-in; activities as a ' · '-separated string."""
    if not db_exists():
        return pd.DataFrame()
    query = """
        SELECT
            dc.checkin_date,
            dc.mood_score,
            dc.energy_score,
            dc.stress_score,
            dc.meaningfulness_level,
            dc.best_part_of_day,
            dc.energy_drainer,
            GROUP_CONCAT(a.activity_name, ' · ') AS activities
        FROM daily_checkins dc
        LEFT JOIN checkin_activities ca ON ca.checkin_id = dc.id
        LEFT JOIN activities a         ON a.id = ca.activity_id
        GROUP BY dc.id
        ORDER BY dc.checkin_date
    """
    with sqlite3.connect(get_db_path()) as conn:
        df = pd.read_sql_query(query, conn)
    if not df.empty:
        df["checkin_date"] = pd.to_datetime(df["checkin_date"])
    return df


def load_detailed_activity_data() -> pd.DataFrame:
    """One row per (check-in × activity) — used to compute filtered activity stats."""
    if not db_exists():
        return pd.DataFrame()
    query = """
        SELECT
            dc.checkin_date,
            dc.mood_score,
            dc.stress_score,
            dc.meaningfulness_level,
            a.activity_name,
            a.activity_category
        FROM checkin_activities ca
        JOIN activities      a  ON a.id  = ca.activity_id
        JOIN daily_checkins  dc ON dc.id = ca.checkin_id
    """
    with sqlite3.connect(get_db_path()) as conn:
        df = pd.read_sql_query(query, conn)
    if not df.empty:
        df["checkin_date"] = pd.to_datetime(df["checkin_date"])
    return df


def get_activity_names() -> list[str]:
    """Sorted list of activity names that appear in at least one check-in."""
    if not db_exists():
        return []
    query = """
        SELECT DISTINCT a.activity_name
        FROM checkin_activities ca
        JOIN activities a ON a.id = ca.activity_id
        ORDER BY a.activity_name
    """
    with sqlite3.connect(get_db_path()) as conn:
        df = pd.read_sql_query(query, conn)
    return df["activity_name"].tolist() if not df.empty else []
