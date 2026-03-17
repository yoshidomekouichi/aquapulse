"""
Tapo P300 電源タップの照明口から ON/OFF 状態を取得する。
python-kasa を使用（tapo ライブラリの Serde エラー回避）。
"""
import asyncio
import datetime
import os

from kasa import Discover


def get_readings():
    """P300 の各口の ON/OFF を取得し、共通フォーマットで返す"""
    return asyncio.run(_get_readings_async())


async def _get_readings_async():
    username = os.getenv("TAPO_USERNAME")
    password = os.getenv("TAPO_PASSWORD")
    plug_ip = os.getenv("TAPO_LIGHTING_IP") or os.getenv("TAPO_P300_IP") or os.getenv("TAPO_PLUG_IP")

    if not all([username, password, plug_ip]):
        raise ValueError(
            "TAPO_USERNAME, TAPO_PASSWORD, TAPO_LIGHTING_IP (or TAPO_P300_IP) を設定してください"
        )

    dev = await Discover.discover_single(
        plug_ip,
        username=username,
        password=password,
    )
    await dev.update()

    readings = []
    now = datetime.datetime.now(datetime.timezone.utc)
    for child in dev.children or []:
        sensor_id = f"tapo_lighting_{child.device_id}"
        value = 1.0 if child.is_on else 0.0
        readings.append({
            "time": now,
            "sensor_id": sensor_id,
            "metric": "power_state",
            "value": value,
            "source": "python-kasa",
        })
    return readings
