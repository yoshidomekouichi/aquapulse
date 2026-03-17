import os
import time
import random
import datetime
import json
import psycopg2

# 設定：何秒ごとにデータを取るか
SAMPLE_INTERVAL = 5
# DB接続用の設定（環境変数から取得。docker-compose で渡す）
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "172.28.0.2"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
    "dbname": os.getenv("POSTGRES_DB", "aquapulse"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "password"),
}

def generate_mock_data():
    """
    本物のセンサーの代わりに、それっぽい水温データを生成する
    """
    # 25.0℃ を基準に、-0.5〜+0.5℃ のブレを作る
    base_temp = 25.0
    random_fluctuation = random.uniform(-1, 1)
    temperature = base_temp + random_fluctuation
    
    # データを辞書型（JSONの元）にする
    data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "sensor_id": "temp_sensor_01",
        "value": round(temperature, 2),
        "unit": "celsius",
        "type": "mock"
    }
    return data

def connect_db():
    """環境変数で DB に接続。失敗時はリトライしてから諦める。"""
    retry_delay = 5
    for attempt in range(6):  # 最大6回（約30秒）
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            return conn
        except psycopg2.OperationalError as e:
            print(f"DB connection failed (attempt {attempt + 1}/6): {e}. Retrying in {retry_delay}s...")
            time.sleep(retry_delay)
    print("Could not connect to DB. Exiting.")
    raise SystemExit(1)

def save_reading(conn, sensor_data):
    """1件のセンサーデータを sensor_readings に INSERT する。"""
    time_utc = datetime.datetime.now(datetime.timezone.utc)
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO sensor_readings (time, sensor_id, metric, value) VALUES (%s, %s, %s, %s)",
            (
                time_utc,
                sensor_data["sensor_id"],
                "temperature",
                sensor_data["value"],
            ),
        )
    conn.commit()

if __name__ == "__main__":
    print(f"--- AquaPulse Mock Collector Started (Interval: {SAMPLE_INTERVAL}s) ---")
    conn = connect_db()
    print("Connected to DB.")
    try:
        while True:
            # 1. データ生成
            sensor_data = generate_mock_data()
            
            # 2. DB に保存
            save_reading(conn, sensor_data)
            
            # 3. 画面にも表示（確認用）
            print(json.dumps(sensor_data, ensure_ascii=False))
            
            # 4. 待機
            time.sleep(SAMPLE_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n--- Stopped by User ---")
    finally:
        conn.close()