# db/writer.py
def save_reading(conn, reading):
    """
    共通フォーマットの辞書 1 件を sensor_readings に INSERT する。
    reading: {"time": datetime, "sensor_id": str, "metric": str, "value": float}
    """
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO sensor_readings (time, sensor_id, metric, value) VALUES (%s, %s, %s, %s)",
            (
                reading["time"],
                reading["sensor_id"],
                reading["metric"],
                reading["value"],
            ),
        )
    conn.commit()