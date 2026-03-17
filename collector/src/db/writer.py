# db/writer.py
def save_reading(conn, reading):
    """
    共通フォーマットの辞書 1 件を sensor_readings に INSERT する。
    reading: {"time": datetime, "sensor_id": str, "metric": str, "value": float, "source": str (optional)}
    """
    cols = ["time", "sensor_id", "metric", "value"]
    vals = [reading["time"], reading["sensor_id"], reading["metric"], reading["value"]]
    if "source" in reading and reading["source"]:
        cols.append("source")
        vals.append(reading["source"])
    placeholders = ", ".join(["%s"] * len(cols))
    col_list = ", ".join(cols)
    with conn.cursor() as cur:
        cur.execute(
            f"INSERT INTO sensor_readings ({col_list}) VALUES ({placeholders})",
            tuple(vals),
        )
    conn.commit()