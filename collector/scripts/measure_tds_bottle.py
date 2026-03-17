#!/usr/bin/env python3
"""
TDS 瓶測定用スクリプト。プローブをガラス瓶に浸した状態で実行する。

アイソレータ導入前の暫定運用：水槽内では 0ppm になるため、1日1回瓶で測定する。
.env の変更や docker compose の起動は不要。ホスト上で実行する。

Usage:
    # プローブを瓶に浸してから実行
    python3 collector/scripts/measure_tds_bottle.py

    # DB に保存する場合（db コンテナが起動していること）
    python3 collector/scripts/measure_tds_bottle.py --save

事前に `sudo modprobe i2c-dev` を実行しておくこと。
"""
import argparse
import datetime
import os
import subprocess
import sys
import time
from pathlib import Path

try:
    import smbus2 as smbus
except ImportError:
    import smbus

I2C_BUS = 1
MCP3424_ADDR = 0x68
TDS_K = float(os.getenv("TDS_K", "500"))
SENSOR_ID = os.getenv("TDS_SENSOR_ID") or "tds_bottle"


def read_ch1_voltage() -> float:
    """MCP3424 CH1 の電圧（V）を返す。"""
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


def voltage_to_ppm(voltage: float) -> float:
    """電圧(V)を TDS(ppm) に換算。"""
    return round(max(0, voltage * TDS_K), 2)


def save_to_db(ppm: float) -> bool:
    """docker compose exec で DB に INSERT。成功で True。"""
    project_root = Path(__file__).resolve().parent.parent.parent
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S+00")
    sql = f"INSERT INTO sensor_readings (time, sensor_id, metric, value) VALUES ('{now}', '{SENSOR_ID}', 'tds', {ppm});"
    try:
        subprocess.run(
            ["docker", "compose", "exec", "-T", "db", "psql", "-U", "postgres", "-d", "aquapulse", "-c", sql],
            cwd=project_root,
            check=True,
            capture_output=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def main():
    parser = argparse.ArgumentParser(description="TDS 瓶測定（プローブを瓶に浸して実行）")
    parser.add_argument("--save", action="store_true", help="DB に保存（db コンテナ起動中であること）")
    args = parser.parse_args()

    try:
        voltage = read_ch1_voltage()
        ppm = voltage_to_ppm(voltage)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"TDS: {ppm} ppm  (voltage: {voltage:.4f} V)")

    if args.save:
        if save_to_db(ppm):
            print("Saved to DB.")
        else:
            print("Failed to save to DB. Is 'docker compose up -d db' running?", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
