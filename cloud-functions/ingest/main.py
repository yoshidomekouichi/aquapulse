"""HTTP endpoint: receive ESP32 sensor payloads and write to BigQuery."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

import google.auth
import functions_framework
from google.cloud import bigquery
from google.cloud.exceptions import GoogleCloudError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REQUIRED_FIELDS = (
    "sensor_id",
    "sensor_type",
    "location",
    "value",
    "unit",
    "device_id",
)

CORS_HEADERS = {"Access-Control-Allow-Origin": "*"}


def _table_id(project_id: str) -> str:
    dataset = os.environ.get("BQ_DATASET", "aquapulse")
    return f"{project_id}.{dataset}.sensor_readings"


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


@functions_framework.http
def ingest(request):
    """Accept JSON sensor readings and insert into BigQuery."""
    if request.method == "OPTIONS":
        return ("", 204, _options_headers())

    headers = {**CORS_HEADERS, "Content-Type": "application/json"}

    try:
        payload = request.get_json(silent=True)
        if not payload:
            return (json.dumps({"error": "Missing JSON body"}), 400, headers)

        missing = [field for field in REQUIRED_FIELDS if field not in payload]
        if missing:
            return (
                json.dumps({"error": f"Missing fields: {', '.join(missing)}"}),
                400,
                headers,
            )

        project_id = _project_id()

        row: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sensor_id": str(payload["sensor_id"]),
            "sensor_type": str(payload["sensor_type"]),
            "location": str(payload["location"]),
            "value": float(payload["value"]),
            "unit": str(payload["unit"]),
            "device_id": str(payload["device_id"]),
            "firmware_version": payload.get("firmware_version"),
        }

        client = bigquery.Client(project=project_id)
        errors = client.insert_rows_json(_table_id(project_id), [row])
        if errors:
            logger.error("BigQuery insert errors: %s", errors)
            return (json.dumps({"error": "BigQuery insert failed", "details": errors}), 500, headers)

        logger.info("Inserted reading: sensor_id=%s value=%s", row["sensor_id"], row["value"])
        return (json.dumps({"status": "ok", "inserted": row}), 200, headers)

    except (TypeError, ValueError) as exc:
        logger.exception("Invalid payload")
        return (json.dumps({"error": str(exc)}), 400, headers)
    except GoogleCloudError as exc:
        logger.exception("BigQuery error")
        return (json.dumps({"error": str(exc)}), 500, headers)
    except Exception as exc:  # noqa: BLE001 - HTTP boundary
        logger.exception("Unexpected ingest error")
        return (json.dumps({"error": str(exc)}), 500, headers)
