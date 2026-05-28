import sqlite3
from pathlib import Path
import os
import dotenv

dotenv.load_dotenv()

GARMIN_DB_PATH = os.getenv("GARMIN_DB_PATH") + "/garmin.db"


def get_sleep_data(start_date, end_date):
    with sqlite3.connect(GARMIN_DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        sql_query = """
            SELECT * FROM sleep
            WHERE date(day) BETWEEN ? AND ?
              AND total_sleep != '00:00:00.000000'
            ORDER BY day DESC
        """
        rows = cursor.execute(sql_query, (start_date, end_date)).fetchall()
        return [dict(row) for row in rows]

def get_sleep_events_for_night(calendar_date: str) -> list[dict]:
    with sqlite3.connect(GARMIN_DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        sql_query = """
            SELECT * FROM sleep_events
            WHERE date(timestamp) = ?
        """
        rows = cursor.execute(sql_query, (calendar_date,)).fetchall()
        return [dict(row) for row in rows]

if __name__ == "__main__":
    start_date = "2026-05-22"
    end_date = "2026-05-24"
    sleep_data = get_sleep_data(start_date, end_date)
    print(sleep_data)