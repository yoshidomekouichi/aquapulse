import os
import sys
import time
import json
import threading

# プロジェクトルート（/app）で src をパスに追加し、db / sources を import できるようにする
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import psycopg2

from db.writer import save_reading

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


if __name__ == "__main__":
    # gpio_temp, gpio_tds 以外のソース（Tapo 等）
    other_sources = {k: v for k, v in SOURCE_LOADERS.items() if k not in ("gpio_temp", "gpio_tds")}
    if not other_sources:
        other_sources = {"mock": SOURCE_LOADERS.get("mock", lambda: [])}

    print(f"--- AquaPulse Collector {SOURCES} (Tapo: {SAMPLE_INTERVAL}s, GPIO temp: {GPIO_TEMP_INTERVAL}s, TDS: {TDS_INTERVAL}s) ---")
    conn = connect_db()
    print("Connected to DB.")

    stop_event = threading.Event()
    gpio_temp_thread = None
    gpio_tds_thread = None
    if "gpio_temp" in SOURCES:
        gpio_temp_thread = threading.Thread(target=_gpio_temp_loop, args=(stop_event,), daemon=True)
        gpio_temp_thread.start()
        print(f"GPIO temp loop started ({GPIO_TEMP_INTERVAL}s interval).")
    if "gpio_tds" in SOURCES:
        gpio_tds_thread = threading.Thread(target=_gpio_tds_loop, args=(stop_event,), daemon=True)
        gpio_tds_thread.start()
        print(f"GPIO TDS loop started ({TDS_INTERVAL}s interval).")

    try:
        while True:
            readings = []
            for name, get_readings_fn in other_sources.items():
                try:
                    readings.extend(get_readings_fn())
                except Exception as e:
                    print(f"[{name}] Failed: {e}", flush=True)
            for r in readings:
                save_reading(conn, r)
                print(json.dumps({k: str(v) if hasattr(v, "isoformat") else v for k, v in r.items()}, ensure_ascii=False))
            time.sleep(SAMPLE_INTERVAL)
    except KeyboardInterrupt:
        print("\n--- Stopped by User ---")
    finally:
        stop_event.set()
        if gpio_temp_thread:
            gpio_temp_thread.join(timeout=GPIO_TEMP_INTERVAL + 2)
        if gpio_tds_thread:
            gpio_tds_thread.join(timeout=TDS_INTERVAL + 2)
        conn.close()