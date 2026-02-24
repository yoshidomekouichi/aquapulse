"""
Tapo T310/T315 温度・湿度センサーからデータを取得する。
H100/H110 ハブ経由で子デバイス（T310/T315）の current_temperature, current_humidity を取得。
"""
import asyncio
import datetime
import os

from tapo import ApiClient
from tapo.responses import T31XResult


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
    hub = await client.h100(hub_ip)
    child_list = await hub.get_child_device_list()

    readings = []
    now = datetime.datetime.now(datetime.timezone.utc)

    for child in child_list or []:
        if not isinstance(child, T31XResult):
            continue

        sensor_id = f"tapo_{child.device_id}"

        readings.append({
            "time": now,
            "sensor_id": sensor_id,
            "metric": "temperature",
            "value": round(float(child.current_temperature), 2),
        })
        readings.append({
            "time": now,
            "sensor_id": sensor_id,
            "metric": "humidity",
            "value": round(float(child.current_humidity), 2),
        })

    return readings