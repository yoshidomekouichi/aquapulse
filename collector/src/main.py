import datetime
import os
import sys
import time
import json
import threading

# プロジェクトルート（/app）で src をパスに追加し、db / sources を import できるようにする
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import psycopg2

from db.writer import save_reading, save_ops_metric, save_ops_metrics_batch

SOURCES_RAW = os.getenv("SOURCES", os.getenv("SOURCE", "mock"))
SOURCES = [s.strip() for s in SOURCES_RAW.split(",") if s.strip()]

# 各ソースの get_readings を取得
def _load_source(name):
    if name == "tapo_sensors":
        if os.getenv("TAPO_BACKEND") == "tapo":
            from sources.tapo_sensors_tapo import get_readings
        else:
            from sources.tapo_sensors import get_readings
        return get_readings
    elif name == "tapo_lighting":
        from sources.tapo_lighting import get_readings
        return get_readings
    elif name == "gpio_temp":
        from sources.gpio_temp import get_readings
        return get_readings
    elif name == "gpio_tds":
        from sources.gpio_tds import get_readings
        return get_readings
    elif name == "mock":
        from sources.mock import get_readings
        return get_readings
    else:
        raise ValueError(f"Unknown source: {name}")

SOURCE_LOADERS = {name: _load_source(name) for name in SOURCES}

# tapo 系（sensors, lighting など）が含まれるなら 300 秒
TAPO_SOURCES = ("tapo_sensors", "tapo_lighting", "tapo_heater", "tapo_feeding")
DEFAULT_INTERVAL = 300 if any(s in SOURCES for s in TAPO_SOURCES) else 5
SAMPLE_INTERVAL = int(os.getenv("SAMPLE_INTERVAL") or str(DEFAULT_INTERVAL))

# gpio_temp は独立ループ（環境変数で上書き可、デフォルト 60 秒）
GPIO_TEMP_INTERVAL = int(os.getenv("GPIO_TEMP_INTERVAL") or "60")
# gpio_tds も独立ループ（環境変数で上書き可、デフォルト 60 秒。テスト時は 10 等に短縮可）
TDS_INTERVAL = int(os.getenv("TDS_INTERVAL") or "60")
# システムメトリクス収集間隔（デフォルト 60 秒）
SYSTEM_STATS_INTERVAL = int(os.getenv("SYSTEM_STATS_INTERVAL") or "60")
# ops_metrics 収集を有効にするか
OPS_METRICS_ENABLED = os.getenv("OPS_METRICS_ENABLED", "true").lower() in ("true", "1", "yes")

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


def collect_with_health(name, get_readings_fn, conn, ops_conn=None):
    """
    ソースからデータを収集し、ヘルスメトリクスも記録する。
    Returns: (readings, health_metrics)
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    host = os.getenv("HOSTNAME", "raspi5")
    health_metrics = []
    
    start_time = time.perf_counter()
    try:
        readings = get_readings_fn()
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        # 成功
        health_metrics.append({
            "time": now,
            "host": host,
            "category": "collector",
            "metric": "collection_success",
            "source": name,
            "value": 1.0,
        })
        health_metrics.append({
            "time": now,
            "host": host,
            "category": "collector",
            "metric": "collection_duration_ms",
            "source": name,
            "value": round(duration_ms, 2),
        })
        health_metrics.append({
            "time": now,
            "host": host,
            "category": "collector",
            "metric": "readings_count",
            "source": name,
            "value": float(len(readings)),
        })
        
        return readings, health_metrics
        
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        print(f"[{name}] Failed: {e}", flush=True)
        
        # 失敗
        health_metrics.append({
            "time": now,
            "host": host,
            "category": "collector",
            "metric": "collection_success",
            "source": name,
            "value": 0.0,
        })
        health_metrics.append({
            "time": now,
            "host": host,
            "category": "collector",
            "metric": "collection_duration_ms",
            "source": name,
            "value": round(duration_ms, 2),
        })
        
        return [], health_metrics


def _gpio_temp_loop(stop_event):
    """
    gpio_temp を GPIO_TEMP_INTERVAL 秒間隔で取得し、DB に保存する独立スレッド。
    stop_event が set されたら終了。
    """
    if "gpio_temp" not in SOURCES:
        return
    conn = connect_db()
    get_readings = SOURCE_LOADERS["gpio_temp"]
    try:
        while not stop_event.is_set():
            try:
                readings = get_readings()
                for r in readings:
                    save_reading(conn, r)
                    print(json.dumps({k: str(v) if hasattr(v, "isoformat") else v for k, v in r.items()}, ensure_ascii=False), flush=True)
            except Exception as e:
                print(f"[gpio_temp] Failed: {e}", flush=True)
            stop_event.wait(GPIO_TEMP_INTERVAL)
    finally:
        conn.close()


def _gpio_tds_loop(stop_event):
    """
    gpio_tds を TDS_INTERVAL 秒間隔で取得し、DB に保存する独立スレッド。
    stop_event が set されたら終了。
    """
    if "gpio_tds" not in SOURCES:
        return
    conn = connect_db()
    get_readings = SOURCE_LOADERS["gpio_tds"]
    try:
        while not stop_event.is_set():
            try:
                readings = get_readings()
                for r in readings:
                    save_reading(conn, r)
                    print(json.dumps({k: str(v) if hasattr(v, "isoformat") else v for k, v in r.items()}, ensure_ascii=False), flush=True)
            except Exception as e:
                print(f"[gpio_tds] Failed: {e}", flush=True)
            stop_event.wait(TDS_INTERVAL)
    finally:
        conn.close()


def _system_stats_loop(stop_event):
    """
    システムメトリクス（CPU, メモリ, ディスク, 温度）を収集する独立スレッド。
    """
    if not OPS_METRICS_ENABLED:
        return
    
    from sources.system_stats import get_metrics
    
    conn = connect_db()
    try:
        while not stop_event.is_set():
            try:
                metrics = get_metrics()
                for m in metrics:
                    save_ops_metric(conn, m)
            except Exception as e:
                print(f"[system_stats] Failed: {e}", flush=True)
            stop_event.wait(SYSTEM_STATS_INTERVAL)
    finally:
        conn.close()


if __name__ == "__main__":
    # gpio_temp, gpio_tds 以外のソース（Tapo 等）
    other_sources = {k: v for k, v in SOURCE_LOADERS.items() if k not in ("gpio_temp", "gpio_tds")}
    if not other_sources:
        other_sources = {"mock": SOURCE_LOADERS.get("mock", lambda: [])}

    print(f"--- AquaPulse Collector {SOURCES} (Tapo: {SAMPLE_INTERVAL}s, GPIO temp: {GPIO_TEMP_INTERVAL}s, TDS: {TDS_INTERVAL}s) ---")
    if OPS_METRICS_ENABLED:
        print(f"Ops metrics enabled (system stats: {SYSTEM_STATS_INTERVAL}s interval)")
    conn = connect_db()
    ops_conn = connect_db() if OPS_METRICS_ENABLED else None
    print("Connected to DB.")

    stop_event = threading.Event()
    threads = []
    
    if "gpio_temp" in SOURCES:
        t = threading.Thread(target=_gpio_temp_loop, args=(stop_event,), daemon=True)
        t.start()
        threads.append(("gpio_temp", t, GPIO_TEMP_INTERVAL))
        print(f"GPIO temp loop started ({GPIO_TEMP_INTERVAL}s interval).")
    
    if "gpio_tds" in SOURCES:
        t = threading.Thread(target=_gpio_tds_loop, args=(stop_event,), daemon=True)
        t.start()
        threads.append(("gpio_tds", t, TDS_INTERVAL))
        print(f"GPIO TDS loop started ({TDS_INTERVAL}s interval).")
    
    if OPS_METRICS_ENABLED:
        t = threading.Thread(target=_system_stats_loop, args=(stop_event,), daemon=True)
        t.start()
        threads.append(("system_stats", t, SYSTEM_STATS_INTERVAL))
        print(f"System stats loop started ({SYSTEM_STATS_INTERVAL}s interval).")

    try:
        while True:
            all_readings = []
            all_health = []
            
            for name, get_readings_fn in other_sources.items():
                if OPS_METRICS_ENABLED:
                    readings, health = collect_with_health(name, get_readings_fn, conn, ops_conn)
                    all_readings.extend(readings)
                    all_health.extend(health)
                else:
                    try:
                        all_readings.extend(get_readings_fn())
                    except Exception as e:
                        print(f"[{name}] Failed: {e}", flush=True)
            
            # センサーデータ保存
            for r in all_readings:
                save_reading(conn, r)
                print(json.dumps({k: str(v) if hasattr(v, "isoformat") else v for k, v in r.items()}, ensure_ascii=False))
            
            # ヘルスメトリクス保存
            if OPS_METRICS_ENABLED and all_health and ops_conn:
                save_ops_metrics_batch(ops_conn, all_health)
            
            time.sleep(SAMPLE_INTERVAL)
    except KeyboardInterrupt:
        print("\n--- Stopped by User ---")
    finally:
        stop_event.set()
        for name, thread, interval in threads:
            thread.join(timeout=interval + 2)
        conn.close()
        if ops_conn:
            ops_conn.close()