"""
DS18B20 水温センサー（1-Wire / GPIO）からデータを取得する。
/sys/bus/w1/devices/28-*/w1_slave を読み、t= の値をパースして摂氏に変換する。
"""

import asyncio
import datetime
import glob
import os
from typing import Optional

# 1-Wire デバイスのパス（ホストの /sys をマウントする前提）
W1_DEVICES_PATH = "/sys/bus/w1/devices"
W1_SLAVE_GLOB = "28-*/w1_slave"


def _read_temperature_sync(device_path: str) -> Optional[float]:
    """
    w1_slave ファイルを同期的に読み、温度（℃）を返す。
    失敗時は None。
    """
    try:
        with open(device_path, "r") as f:
            content = f.read()
    except (OSError, IOError):
        return None

    # 2行目に "t=12345" の形式で温度（ミリ度）が入る
    for line in content.strip().split("\n"):
        if line.strip().endswith("YES") and "crc=" in line:
            # CRC チェック成功
            pass
        elif "t=" in line:
            try:
                temp_str = line.split("t=")[-1].strip()
                temp_millideg = int(temp_str)
                return round(temp_millideg / 1000.0, 2)
            except (ValueError, IndexError):
                return None
    return None


def get_readings():
    """
    DS18B20 から水温を取得し、共通フォーマットの辞書リストで返す。
    センサー未検出・パース失敗時は空リスト。
    """
    return asyncio.run(_get_readings_async())


async def _get_readings_async():
    pattern = os.path.join(W1_DEVICES_PATH, W1_SLAVE_GLOB)
    device_files = glob.glob(pattern)

    if not device_files:
        return []

    now = datetime.datetime.now(datetime.timezone.utc)
    readings = []

    for device_path in device_files:
        # ファイル I/O はブロッキングなので、スレッドプールで実行
        temp = await asyncio.to_thread(_read_temperature_sync, device_path)
        if temp is not None:
            # デバイス ID を sensor_id に（例: 28-00001117a4e0 → ds18b20_28_00001117a4e0）
            device_id = os.path.basename(os.path.dirname(device_path)).replace("-", "_")
            sensor_id = f"ds18b20_water_{device_id}"
            readings.append({
                "time": now,
                "sensor_id": sensor_id,
                "metric": "temperature",
                "value": temp,
            })

    return readings