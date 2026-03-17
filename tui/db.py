"""
AquaPulse DB から sensor_readings を取得するモジュール。
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import psycopg2
from psycopg2.extras import RealDictCursor


def get_conn():
    """DB 接続を返す"""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "aquapulse"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "password"),
    )


def fetch_latest(
    conn,
    sensor_pattern: str,
    metric: str,
    exclude_pattern: Optional[str] = None,
) -> tuple[Optional[float], Optional[datetime]]:
    """
    最新の value を 1 件取得。
    sensor_pattern: LIKE 用（例: 'ds18b20_water_%'）
    exclude_pattern: 除外する sensor_id の LIKE（例: 'tapo_lighting_%'）
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        if exclude_pattern:
            cur.execute(
                """
                SELECT value, time FROM sensor_readings
                WHERE sensor_id LIKE %s AND metric = %s AND sensor_id NOT LIKE %s
                ORDER BY time DESC LIMIT 1
                """,
                (sensor_pattern, metric, exclude_pattern),
            )
        else:
            cur.execute(
                """
                SELECT value, time FROM sensor_readings
                WHERE sensor_id LIKE %s AND metric = %s
                ORDER BY time DESC LIMIT 1
                """,
                (sensor_pattern, metric),
            )
        row = cur.fetchone()
        return (row["value"], row["time"]) if row else (None, None)


def fetch_series(
    conn,
    sensor_pattern: str,
    metric: str,
    hours: int = 24,
    exclude_pattern: Optional[str] = None,
) -> list[tuple[datetime, float]]:
    """
    過去 N 時間の時系列データを取得。
    返り値: [(time, value), ...] 古い順
    """
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        if exclude_pattern:
            cur.execute(
                """
                SELECT time, value FROM sensor_readings
                WHERE sensor_id LIKE %s AND metric = %s AND sensor_id NOT LIKE %s
                  AND time >= %s
                ORDER BY time ASC
                """,
                (sensor_pattern, metric, exclude_pattern, since),
            )
        else:
            cur.execute(
                """
                SELECT time, value FROM sensor_readings
                WHERE sensor_id LIKE %s AND metric = %s AND time >= %s
                ORDER BY time ASC
                """,
                (sensor_pattern, metric, since),
            )
        return [(r["time"], float(r["value"])) for r in cur.fetchall()]


def get_water_temp(conn) -> tuple[Optional[float], Optional[datetime]]:
    """水温の最新値"""
    return fetch_latest(conn, "ds18b20_water_%", "temperature")


def get_room_temp(conn) -> tuple[Optional[float], Optional[datetime]]:
    """気温の最新値（tapo、lighting 除外）"""
    return fetch_latest(
        conn, "tapo_%", "temperature", exclude_pattern="tapo_lighting_%"
    )


def get_humidity(conn) -> tuple[Optional[float], Optional[datetime]]:
    """湿度の最新値"""
    return fetch_latest(conn, "tapo_%", "humidity")


def get_light_state(conn) -> tuple[Optional[float], Optional[datetime]]:
    """照明 ON/OFF（0 or 1）"""
    return fetch_latest(conn, "tapo_lighting_%", "power_state")


def get_light_series(conn, hours: int = 24) -> list[tuple[datetime, float]]:
    """照明 ON/OFF の時系列（0 or 1）"""
    return fetch_series(conn, "tapo_lighting_%", "power_state", hours)


def get_water_temp_series(conn, hours: int = 24) -> list[tuple[datetime, float]]:
    """水温の時系列"""
    return fetch_series(conn, "ds18b20_water_%", "temperature", hours)


def get_room_temp_series(conn, hours: int = 24) -> list[tuple[datetime, float]]:
    """気温の時系列"""
    return fetch_series(
        conn, "tapo_%", "temperature", hours, exclude_pattern="tapo_lighting_%"
    )


def get_humidity_series(conn, hours: int = 24) -> list[tuple[datetime, float]]:
    """湿度の時系列"""
    return fetch_series(conn, "tapo_%", "humidity", hours)
