import time
import random
import datetime
import json

# 設定：何秒ごとにデータを取るか
SAMPLE_INTERVAL = 5

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

if __name__ == "__main__":
    print(f"--- AquaPulse Mock Collector Started (Interval: {SAMPLE_INTERVAL}s) ---")
    try:
        while True:
            # 1. データ生成
            sensor_data = generate_mock_data()
            
            # 2. 画面に表示（後でここをDB保存に変える）
            # json.dumpsを使うと、辞書型を綺麗な文字列にできる
            print(json.dumps(sensor_data, ensure_ascii=False))
            
            # 3. 待機
            time.sleep(SAMPLE_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n--- Stopped by User ---")