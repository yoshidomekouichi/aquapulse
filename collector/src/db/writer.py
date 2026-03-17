# db/writer.py
"""
データベース書き込みモジュール。
- sensor_readings: アクアリウムセンサーデータ
- ops_metrics: システム監視・収集ヘルス
"""


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


def save_ops_metric(conn, metric):
    """
    ops_metrics テーブルに 1 件 INSERT する。
    metric: {
        "time": datetime,
        "host": str (default: 'raspi5'),
        "category": str ('system' | 'collector'),
        "metric": str,
        "source": str (optional, collector の場合),
        "value": float
    }
    """
    cols = ["time", "host", "category", "metric", "value"]
    vals = [
        metric["time"],
        metric.get("host", "raspi5"),
        metric["category"],
        metric["metric"],
        metric["value"],
    ]
    if metric.get("source"):
        cols.append("source")
        vals.append(metric["source"])
    placeholders = ", ".join(["%s"] * len(cols))
    col_list = ", ".join(cols)
    with conn.cursor() as cur:
        cur.execute(
            f"INSERT INTO ops_metrics ({col_list}) VALUES ({placeholders})",
            tuple(vals),
        )
    conn.commit()


def save_ops_metrics_batch(conn, metrics):
    """
    ops_metrics テーブルに複数件を一括 INSERT する。
    """
    if not metrics:
        return
    for m in metrics:
        save_ops_metric(conn, m)