"""
Tapo T310/T315 温度・湿度センサーからデータを取得する。
H100/H110 ハブ経由で子デバイス（T310/T315）の温度・湿度を取得。
python-kasa を使用（tapo ライブラリの InvalidRequest エラー回避）。
"""
import asyncio
import datetime
import os

from kasa import Discover


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

    dev = await Discover.discover_single(
        hub_ip,
        username=username,
        password=password,
    )
    await dev.update()

    readings = []
    now = datetime.datetime.now(datetime.timezone.utc)

    for child in dev.children or []:
        # T310/T315 は model に "T310" または "T315" を含む
        model = getattr(child, "model", "") or ""
        if "T310" not in model and "T315" not in model:
            continue

        sensor_id = f"tapo_{child.device_id}"
        temp_val = None
        hum_val = None

        # features から temperature / humidity を取得
        # 注意: temperature_unit, humidity_warning 等は除外（完全一致のみ）
        features = getattr(child, "features", None) or {}
        for fid, feat in features.items():
            val = getattr(feat, "value", feat) if not isinstance(feat, (int, float)) else feat
            if val is None or not isinstance(val, (int, float)):
                continue
            fid_lower = (fid or "").lower()
            if fid_lower == "temperature":
                temp_val = val
            elif fid_lower == "humidity":
                hum_val = val

        # フォールバック: よくある ID で直接取得
        if temp_val is None:
            f = features.get("temperature") or features.get("current_temperature")
            if f is not None:
                v = getattr(f, "value", f)
                if isinstance(v, (int, float)):
                    temp_val = v
        if hum_val is None:
            f = features.get("humidity") or features.get("current_humidity")
            if f is not None:
                v = getattr(f, "value", f)
                if isinstance(v, (int, float)):
                    hum_val = v

        if temp_val is not None:
            readings.append({
                "time": now,
                "sensor_id": sensor_id,
                "metric": "temperature",
                "value": round(float(temp_val), 2),
                "source": "python-kasa",
            })
        if hum_val is not None:
            readings.append({
                "time": now,
                "sensor_id": sensor_id,
                "metric": "humidity",
                "value": round(float(hum_val), 2),
                "source": "python-kasa",
            })

    return readings
