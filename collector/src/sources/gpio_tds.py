"""
TDS センサー（MCP3424 CH1 経由）からデータを取得する。

MCP3424 の CH1 で電圧を読み、TDS(ppm) に換算して返す。
sensor_id は TDS_SENSOR_ID で上書き可能（テスト時は tds_test_ch1 等）。
"""
import datetime
import os
import time

# smbus2 は pip で入る純 Python 実装。なければシステムの smbus を使用
try:
    import smbus2 as smbus
except ImportError:
    import smbus

# I2C バス・アドレス（scripts/read_mcp3424_ch1.py と同じ）
I2C_BUS = 1
MCP3424_ADDR = 0x68

# テスト時は TDS_SENSOR_ID=tds_test_ch1 を .env に設定
SENSOR_ID = os.getenv("TDS_SENSOR_ID") or "tds_ch1"
# 電圧→ppm の係数。キャリブレーション時は TDS_K で上書き
TDS_K = float(os.getenv("TDS_K", "500"))


def _read_ch1_voltage() -> float:
    """MCP3424 CH1 の電圧（V）を返す。18bit, 1x gain, one-shot。"""
    bus = smbus.SMBus(I2C_BUS)
    try:
        bus.write_byte(MCP3424_ADDR, 0x80)
        time.sleep(0.1)
        raw = bus.read_i2c_block_data(MCP3424_ADDR, 0, 4)
        val = ((raw[0] & 0x03) << 16) | (raw[1] << 8) | raw[2]
        if val & 0x20000:
            val -= 0x40000
        return val * 2.048 / 262144
    finally:
        bus.close()


def _voltage_to_ppm(voltage: float) -> float:
    """電圧(V)を TDS(ppm) に換算。線形: ppm = voltage * TDS_K"""
    return round(max(0, voltage * TDS_K), 2)


def get_readings():
    """
    TDS センサーから ppm を取得し、共通フォーマットの辞書リストで返す。
    失敗時は空リスト。
    """
    try:
        voltage = _read_ch1_voltage()
        ppm = _voltage_to_ppm(voltage)
        now = datetime.datetime.now(datetime.timezone.utc)
        return [{
            "time": now,
            "sensor_id": SENSOR_ID,
            "metric": "tds",
            "value": ppm,
        }]
    except Exception:
        return []
