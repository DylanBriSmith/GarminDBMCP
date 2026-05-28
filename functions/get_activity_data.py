import json
import sqlite3
from pathlib import Path
import os
import dotenv

dotenv.load_dotenv()

GARMIN_DB_PATH = os.getenv("GARMIN_DBs_PATH") + "/garmin_activities.db"
ACTIVITIES_JSON_DIR = Path(os.getenv("FITFILES_PATH"))


def get_activity_data(
    start_date: str,
    end_date: str,
    *,
    sport: str | None = None,
    sub_sport: str | None = None,
    name_contains: str | None = None,
) -> list[dict]:
    """
    Activities in a date range (summary rows from SQLite).

    Optional filters (omit or pass None to skip):
      sport         e.g. "running", "fitness_equipment", "cycling"
      sub_sport     e.g. "strength_training", "generic", "cardio_training"
      name_contains substring match on activity name (case-insensitive)
    """
    sql = """
        SELECT * FROM activities
        WHERE date(start_time) BETWEEN ? AND ?
    """
    params: list = [start_date, end_date]

    if sport is not None:
        sql += " AND sport = ?"
        params.append(sport)
    if sub_sport is not None:
        sql += " AND sub_sport = ?"
        params.append(sub_sport)
    if name_contains is not None:
        sql += " AND name LIKE ? ESCAPE '\\'"
        params.append(f"%{name_contains}%")

    sql += " ORDER BY start_time DESC"

    with sqlite3.connect(GARMIN_DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]


# Keep typo alias so existing imports do not break.
get_actitivity_data = get_activity_data


def get_activity_by_id(activity_id: str) -> dict | None:
    """One activity summary row from SQLite, or None if not imported."""
    activity_id = str(activity_id)
    with sqlite3.connect(GARMIN_DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM activities WHERE activity_id = ?",
            (activity_id,),
        ).fetchone()
        return dict(row) if row else None


def try_load_activity_json(activity_id: str, *, details: bool = False) -> dict | None:
    """Load activity JSON if the file exists; otherwise return None."""
    activity_id = str(activity_id)
    filename = (
        f"activity_details_{activity_id}.json"
        if details
        else f"activity_{activity_id}.json"
    )
    path = ACTIVITIES_JSON_DIR / filename
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_activity_json(activity_id: str, *, details: bool = False) -> dict:
    """
    Load Garmin Connect JSON for an activity.

    details=False → activity_{id}.json (includes summarizedExerciseSets for strength).
    details=True  → activity_details_{id}.json (metadata + summaryDTO).

    Raises FileNotFoundError if the file is missing.
    """
    data = try_load_activity_json(activity_id, details=details)
    if data is None:
        kind = "activity_details" if details else "activity"
        raise FileNotFoundError(
            f"No {kind} JSON for activity_id={activity_id} under {ACTIVITIES_JSON_DIR}"
        )
    return data


def get_activity_laps(activity_id: str) -> list[dict]:
    """Lap/split rows for an activity (often empty for strength)."""
    activity_id = str(activity_id)
    with sqlite3.connect(GARMIN_DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT * FROM activity_laps
            WHERE activity_id = ?
            ORDER BY lap
            """,
            (activity_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def get_activity_records(activity_id: str, *, limit: int | None = None) -> list[dict]:
    """Second-by-second points (HR, speed, etc.). Use limit to cap size."""
    activity_id = str(activity_id)
    sql = """
        SELECT * FROM activity_records
        WHERE activity_id = ?
        ORDER BY timestamp
    """
    params: list = [activity_id]
    if limit is not None:
        sql += " LIMIT ?"
        params.append(limit)

    with sqlite3.connect(GARMIN_DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]


def get_activity_data_full(
    activity_id: str,
    *,
    include_details_json: bool = False,
    include_laps: bool = True,
    include_records: bool = False,
    records_limit: int = 500,
) -> dict:
    """
    Bundle everything useful for one activity (for MCP / generative UI).

    Returns:
        activity_id, summary (SQLite or None), json, json_details (optional),
        laps (optional), records (optional; can be large).
    """
    activity_id = str(activity_id)
    return {
        "activity_id": activity_id,
        "summary": get_activity_by_id(activity_id),
        "json": try_load_activity_json(activity_id),
        "json_details": (
            try_load_activity_json(activity_id, details=True)
            if include_details_json
            else None
        ),
        "laps": get_activity_laps(activity_id) if include_laps else None,
        "records": (
            get_activity_records(activity_id, limit=records_limit)
            if include_records
            else None
        ),
    }


# Shorter alias
get_activity_full = get_activity_data_full


if __name__ == "__main__":
    aid = "23007971314"
    full = get_activity_data_full(aid)
    print("activity_id:", full["activity_id"])
    print("has summary:", full["summary"] is not None)
    print("has json:", full["json"] is not None)
    print("laps:", len(full["laps"] or []))
    sets = (full["json"] or {}).get("summarizedExerciseSets")
    print("exercise set groups:", len(sets) if sets else 0)
    print("range count:", len(get_activity_data("2026-05-22", "2026-05-24")))
