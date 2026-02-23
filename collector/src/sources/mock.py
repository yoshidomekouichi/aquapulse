import random
import datetime


def get_readings():
    """
    モックの水温データを1件、共通フォーマットの辞書にしてリストで返す。
    """
    base_temp = 25.0
    random_fluctuation = random.uniform(-1, 1)
    temperature = base_temp + random_fluctuation

    reading = {
        "time": datetime.datetime.now(datetime.timezone.utc),
        "sensor_id": "mock_temperature",
        "metric": "temperature",
        "value": round(temperature, 2),
    }
    return [reading]