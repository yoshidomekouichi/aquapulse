"""HTTP endpoint: thermostat logic and Tapo P300 fan control."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any

import google.auth
import functions_framework
from google.cloud import bigquery, secretmanager
from google.cloud.exceptions import GoogleCloudError
from kasa import Discover

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

THRESHOLD_HIGH = float(os.environ.get("THRESHOLD_HIGH", "28.0"))
THRESHOLD_LOW = float(os.environ.get("THRESHOLD_LOW", "26.0"))
FAN_CHILD_INDEX = int(os.environ.get("FAN_CHILD_INDEX", "0"))
THERMOSTAT_DEVICE_ID = os.environ.get("THERMOSTAT_DEVICE_ID", "cloud_function_thermostat_v1")
DEFAULT_TRIGGER_SENSOR_ID = os.environ.get("DEFAULT_TRIGGER_SENSOR_ID", "ds18b20_001")

CORS_HEADERS = {"Access-Control-Allow-Origin": "*"}


def _table_id(project_id: str) -> str:
    dataset = os.environ.get("BQ_DATASET", "aquapulse")
    return f"{project_id}.{dataset}.control_events"


def _project_id() -> str:
    project = (
        os.environ.get("GCP_PROJECT")
        or os.environ.get("GOOGLE_CLOUD_PROJECT")
        or os.environ.get("GCLOUD_PROJECT")
    )
    if project:
        return project
    _, project = google.auth.default()
    if not project:
        raise RuntimeError("GCP project not configured")
    return project


def _options_headers() -> dict[str, str]:
    return {
        **CORS_HEADERS,
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Max-Age": "3600",
    }


def _get_secret(project_id: str, secret_id: str) -> str:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("utf-8")


def _record_event(
    project_id: str,
    *,
    action: str,
    temperature: float,
    threshold: float | None,
    success: bool,
    error_message: str | None = None,
    duration_ms: int | None = None,
) -> None:
    row: dict[str, Any] = {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": "automated_thermostat",
        "device_id": THERMOSTAT_DEVICE_ID,
        "action": action,
        "action_details": {
            "hysteresis_upper": THRESHOLD_HIGH,
            "hysteresis_lower": THRESHOLD_LOW,
        },
        "trigger_type": "threshold_exceeded" if success else "error",
        "trigger_sensor_id": DEFAULT_TRIGGER_SENSOR_ID,
        "trigger_value": temperature,
        "trigger_threshold": threshold,
        "success": success,
        "error_message": error_message,
        "duration_ms": duration_ms,
    }
    client = bigquery.Client(project=project_id)
    errors = client.insert_rows_json(_table_id(project_id), [row])
    if errors:
        logger.error("Failed to record control event: %s", errors)


async def _control_fan_async(project_id: str, temperature: float) -> dict[str, Any]:
    started = datetime.now(timezone.utc)

    tapo_username = _get_secret(project_id, "tapo-username")
    tapo_password = _get_secret(project_id, "tapo-password")
    tapo_ip = _get_secret(project_id, "tapo-p300-ip")

    dev = await Discover.discover_single(
        tapo_ip,
        username=tapo_username,
        password=tapo_password,
        timeout=10,
    )
    await dev.update()

    children = list(dev.children or [])
    if not children:
        raise RuntimeError("Tapo P300 has no child outlets")

    fan = children[FAN_CHILD_INDEX]
    is_on = bool(fan.is_on)

    if temperature >= THRESHOLD_HIGH and not is_on:
        await fan.turn_on()
        duration_ms = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)
        _record_event(
            project_id,
            action="fan_on",
            temperature=temperature,
            threshold=THRESHOLD_HIGH,
            success=True,
            duration_ms=duration_ms,
        )
        return {"action": "fan_on", "temperature": temperature, "threshold": THRESHOLD_HIGH}

    if temperature <= THRESHOLD_LOW and is_on:
        await fan.turn_off()
        duration_ms = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)
        _record_event(
            project_id,
            action="fan_off",
            temperature=temperature,
            threshold=THRESHOLD_LOW,
            success=True,
            duration_ms=duration_ms,
        )
        return {"action": "fan_off", "temperature": temperature, "threshold": THRESHOLD_LOW}

    return {
        "action": "no_change",
        "temperature": temperature,
        "fan_is_on": is_on,
        "threshold_high": THRESHOLD_HIGH,
        "threshold_low": THRESHOLD_LOW,
    }


@functions_framework.http
def thermostat(request):
    """Apply hysteresis fan control from a temperature reading."""
    if request.method == "OPTIONS":
        return ("", 204, _options_headers())

    headers = {**CORS_HEADERS, "Content-Type": "application/json"}

    try:
        payload = request.get_json(silent=True)
        if not payload or "value" not in payload:
            return (json.dumps({"error": "Missing temperature value"}), 400, headers)

        temperature = float(payload["value"])
        project_id = _project_id()
        result = asyncio.run(_control_fan_async(project_id, temperature))
        return (json.dumps(result), 200, headers)

    except GoogleCloudError as exc:
        logger.exception("Google Cloud error")
        return (json.dumps({"error": str(exc)}), 500, headers)
    except Exception as exc:  # noqa: BLE001 - HTTP boundary
        logger.exception("Thermostat error")
        project_id = _project_id()
        error_payload = request.get_json(silent=True) or {}
        if project_id and "value" in error_payload:
            _record_event(
                project_id,
                action="error",
                temperature=float(error_payload["value"]),
                threshold=None,
                success=False,
                error_message=str(exc),
            )
        return (json.dumps({"error": str(exc)}), 500, headers)
