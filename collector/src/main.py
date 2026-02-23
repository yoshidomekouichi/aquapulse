import os
import sys
import time
import json

# プロジェクトルート（/app）で src をパスに追加し、db / sources を import できるようにする
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import psycopg2

from db.writer import save_reading
from sources.mock import get_readings

SAMPLE_INTERVAL = 5

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "172.28.0.2"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
    "dbname": os.getenv("POSTGRES_DB", "aquapulse"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "password"),
}


def connect_db():
    """DB に接続。失敗時はリトライしてから諦める。"""
    retry_delay = 5
    for attempt in range(6):
        try:
            return psycopg2.connect(**DB_CONFIG)
        except psycopg2.OperationalError as e:
            print(f"DB connection failed (attempt {attempt + 1}/6): {e}. Retrying in {retry_delay}s...")
            time.sleep(retry_delay)
    print("Could not connect to DB. Exiting.")
    raise SystemExit(1)


if __name__ == "__main__":
    print(f"--- AquaPulse Collector (Interval: {SAMPLE_INTERVAL}s) ---")
    conn = connect_db()
    print("Connected to DB.")
    try:
        while True:
            readings = get_readings()
            for r in readings:
                save_reading(conn, r)
                print(json.dumps({k: str(v) if hasattr(v, "isoformat") else v for k, v in r.items()}, ensure_ascii=False))
            time.sleep(SAMPLE_INTERVAL)
    except KeyboardInterrupt:
        print("\n--- Stopped by User ---")
    finally:
        conn.close()