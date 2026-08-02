#!/usr/bin/env python3
"""
Mac Tapo poller — read Tapo sensors/plugs on LAN and POST to GCP ingest.

Phase 1a: observability only (no fan control). See scripts/tapo_poller/README.md.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
from kasa import Discover

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INGEST_URL = "https://ingest-e4jnfqozuq-an.a.run.app"
DEVICE_ID = "mac_poller_v1"
FIRMWARE_VERSION = "tapo-poller-0.1.0"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IngestReading:
    sensor_id: str
    sensor_type: str
    location: str
    value: float
    unit: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "sensor_id": self.sensor_id,
            "sensor_type": self.sensor_type,
            "location": self.location,
            "value": self.value,
            "unit": self.unit,
            "device_id": DEVICE_ID,
            "firmware_version": FIRMWARE_VERSION,
        }


def load_env() -> None:
    """Load KEY=VALUE lines from repo .env if present."""
    env_path = ROOT / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ValueError(f"Missing environment variable: {name}")
    return value


def ingest_url() -> str:
    return os.environ.get("INGEST_URL", DEFAULT_INGEST_URL).strip()


async def fetch_hub_readings() -> list[IngestReading]:
    username = require_env("TAPO_USERNAME")
    password = require_env("TAPO_PASSWORD")
    hub_ip = (
        os.environ.get("TAPO_HUB_IP")
        or os.environ.get("TAPO_SENSOR_HUB_IP")
        or ""
    ).strip()
    if not hub_ip:
        raise ValueError("Set TAPO_HUB_IP (H100/H110 hub for T310/T315)")

    dev = await Discover.discover_single(
        hub_ip,
        username=username,
        password=password,
        timeout=10,
    )
    await dev.update()

    readings: list[IngestReading] = []
    for child in dev.children or []:
        model = getattr(child, "model", "") or ""
        if "T310" not in model and "T315" not in model:
            continue

        sensor_id = f"tapo_{child.device_id}"
        features = getattr(child, "features", None) or {}

        temp_val = _feature_value(features, "temperature", "current_temperature")
        hum_val = _feature_value(features, "humidity", "current_humidity")

        if temp_val is not None:
            readings.append(
                IngestReading(
                    sensor_id=sensor_id,
                    sensor_type="room_temperature",
                    location="room",
                    value=round(float(temp_val), 2),
                    unit="celsius",
                )
            )
        if hum_val is not None:
            readings.append(
                IngestReading(
                    sensor_id=sensor_id,
                    sensor_type="room_humidity",
                    location="room",
                    value=round(float(hum_val), 2),
                    unit="percent",
                )
            )

    return readings


async def fetch_p300_readings() -> list[IngestReading]:
    username = require_env("TAPO_USERNAME")
    password = require_env("TAPO_PASSWORD")
    plug_ip = (
        os.environ.get("TAPO_P300_IP")
        or os.environ.get("TAPO_LIGHTING_IP")
        or os.environ.get("TAPO_PLUG_IP")
        or ""
    ).strip()
    if not plug_ip:
        raise ValueError("Set TAPO_P300_IP (P300 multi-outlet IP)")

    fan_index = int(os.environ.get("TAPO_P300_FAN_INDEX", "0"))
    light_index = int(os.environ.get("TAPO_P300_LIGHT_INDEX", "1"))
    fan_sensor_id = os.environ.get("TAPO_FAN_SENSOR_ID", "tapo_p300_fan")
    light_sensor_id = os.environ.get("TAPO_LIGHT_SENSOR_ID", "tapo_p300_light")

    dev = await Discover.discover_single(
        plug_ip,
        username=username,
        password=password,
        timeout=10,
    )
    await dev.update()

    children = list(dev.children or [])
    readings: list[IngestReading] = []

    for index, child in enumerate(children):
        value = 1.0 if child.is_on else 0.0
        if index == fan_index:
            sensor_id = fan_sensor_id
            location = "aquarium"
        elif index == light_index:
            sensor_id = light_sensor_id
            location = "room"
        else:
            sensor_id = f"tapo_p300_outlet_{index}"
            location = "room"

        readings.append(
            IngestReading(
                sensor_id=sensor_id,
                sensor_type="power_state",
                location=location,
                value=value,
                unit="boolean",
            )
        )
        logger.info(
            "P300 outlet %s (%s): %s",
            index,
            sensor_id,
            "ON" if value else "OFF",
        )

    return readings


def _feature_value(features: dict, *keys: str) -> float | None:
    for key in keys:
        feat = features.get(key)
        if feat is None:
            continue
        val = getattr(feat, "value", feat) if not isinstance(feat, (int, float)) else feat
        if isinstance(val, (int, float)):
            return float(val)
    return None


def post_reading(payload: dict[str, Any], *, dry_run: bool) -> bool:
    if dry_run:
        logger.info("DRY-RUN POST %s", json.dumps(payload, ensure_ascii=False))
        return True

    url = ingest_url()
    for attempt in range(1, 4):
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.ok:
                logger.info(
                    "ingest OK: sensor_id=%s value=%s",
                    payload.get("sensor_id"),
                    payload.get("value"),
                )
                return True
            logger.warning(
                "ingest HTTP %s: %s (attempt %d/3)",
                response.status_code,
                response.text[:200],
                attempt,
            )
        except requests.RequestException as exc:
            logger.warning("ingest error: %s (attempt %d/3)", exc, attempt)
        if attempt < 3:
            time.sleep(2**attempt)
    return False


async def collect_all(*, skip_hub: bool, skip_p300: bool) -> list[IngestReading]:
    readings: list[IngestReading] = []
    errors: list[str] = []

    if not skip_hub:
        try:
            hub = await fetch_hub_readings()
            readings.extend(hub)
            logger.info("Hub: %d reading(s)", len(hub))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"hub: {exc}")
            logger.error("Hub fetch failed: %s", exc)

    if not skip_p300:
        try:
            plug = await fetch_p300_readings()
            readings.extend(plug)
            logger.info("P300: %d reading(s)", len(plug))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"p300: {exc}")
            logger.error("P300 fetch failed: %s", exc)

    if not readings and errors:
        raise RuntimeError("; ".join(errors))
    return readings


def run_once(*, dry_run: bool, skip_hub: bool, skip_p300: bool) -> int:
    load_env()
    readings = asyncio.run(collect_all(skip_hub=skip_hub, skip_p300=skip_p300))

    if not readings:
        logger.warning("No readings collected")
        return 1

    ok = 0
    failed = 0
    for reading in readings:
        if post_reading(reading.to_payload(), dry_run=dry_run):
            ok += 1
        else:
            failed += 1

    logger.info("Done: %d ok, %d failed, total %d", ok, failed, len(readings))
    return 0 if failed == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Poll Tapo devices and send to GCP ingest")
    parser.add_argument("--dry-run", action="store_true", help="Fetch only; do not POST")
    parser.add_argument("--skip-hub", action="store_true", help="Skip T310/T315 hub")
    parser.add_argument("--skip-p300", action="store_true", help="Skip P300 outlets")
    args = parser.parse_args()
    try:
        return run_once(dry_run=args.dry_run, skip_hub=args.skip_hub, skip_p300=args.skip_p300)
    except Exception as exc:  # noqa: BLE001
        logger.error("Fatal: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
