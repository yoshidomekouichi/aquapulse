"""
Raspberry Pi システムメトリクス取得。
CPU使用率、メモリ、ディスク、温度などを収集する。
"""
import datetime
import os

import psutil


def _get_cpu_temp():
    """
    Raspberry Pi の CPU 温度を取得（℃）。
    /sys/class/thermal/thermal_zone0/temp から読み取る。
    """
    temp_path = "/sys/class/thermal/thermal_zone0/temp"
    try:
        with open(temp_path, "r") as f:
            temp_millideg = int(f.read().strip())
            return round(temp_millideg / 1000.0, 1)
    except (OSError, IOError, ValueError):
        return None


def get_metrics():
    """
    システムメトリクスを取得し、ops_metrics 用フォーマットで返す。
    Returns: list of dict
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    host = os.getenv("HOSTNAME", "raspi5")
    
    metrics = []
    
    # CPU 使用率
    cpu_percent = psutil.cpu_percent(interval=1)
    metrics.append({
        "time": now,
        "host": host,
        "category": "system",
        "metric": "cpu_percent",
        "value": cpu_percent,
    })
    
    # メモリ使用率
    mem = psutil.virtual_memory()
    metrics.append({
        "time": now,
        "host": host,
        "category": "system",
        "metric": "memory_percent",
        "value": mem.percent,
    })
    
    # ディスク使用率（ルートパーティション）
    disk = psutil.disk_usage("/")
    metrics.append({
        "time": now,
        "host": host,
        "category": "system",
        "metric": "disk_percent",
        "value": disk.percent,
    })
    
    # ロードアベレージ（1分）
    load_1m, _, _ = os.getloadavg()
    metrics.append({
        "time": now,
        "host": host,
        "category": "system",
        "metric": "load_1m",
        "value": round(load_1m, 2),
    })
    
    # CPU 温度（Raspberry Pi）
    cpu_temp = _get_cpu_temp()
    if cpu_temp is not None:
        metrics.append({
            "time": now,
            "host": host,
            "category": "system",
            "metric": "cpu_temp",
            "value": cpu_temp,
        })
    
    return metrics
