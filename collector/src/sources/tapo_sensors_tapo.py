"""
Tapo T310/T315 温度・湿度センサーからデータを取得する（tapo ライブラリ版）。
H100/H110 ハブ経由で子デバイス（T310/T315）の温度・湿度を取得。
"""
import asyncio
import datetime
import os

from tapo import ApiClient


def get_readings():
    """
    Tapo H100/H110 に接続された T310/T315 センサーから温度・湿度を取得し、
    共通フォーマットの辞書リストで返す。
    """
    return asyncio.run(_get_readings_async())


async def _get_readings_async():
    username = os.getenv("TAPO_USERNAME")
    password = os.getenv("TAPO_PASSWORD")
    hub_ip = os.getenv("TAPO_HUB_IP") or os.getenv("IP_ADDRESS")

    if not all([username, password, hub_ip]):
        raise ValueError(
            "TAPO_USERNAME, TAPO_PASSWORD, TAPO_HUB_IP (or IP_ADDRESS) を設定してください"
        )

    client = ApiClient(username, password)
    device = await client.h100(hub_ip)
    children = await device.get_child_device_list()

    readings = []
    now = datetime.datetime.now(datetime.timezone.utc)

    for child in children or []:
        # T31XResult の current_temperature, current_humidity を取得
        temp_val = getattr(child, "current_temperature", None)
        hum_val = getattr(child, "current_humidity", None)
        device_id = getattr(child, "device_id", None)

        if device_id is None:
            continue

        sensor_id = f"tapo_{device_id}"

        if temp_val is not None and isinstance(temp_val, (int, float)):
            readings.append({
                "time": now,
                "sensor_id": sensor_id,
                "metric": "temperature",
                "value": round(float(temp_val), 2),
                "source": "tapo",
            })
        if hum_val is not None and isinstance(hum_val, (int, float)):
            readings.append({
                "time": now,
                "sensor_id": sensor_id,
                "metric": "humidity",
                "value": round(float(hum_val), 2),
                "source": "tapo",
            })

    return readings
