#!/usr/bin/env bash
# Create BigQuery dataset and Phase 1 tables.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT_ID="${1:-$(gcloud config get-value project 2>/dev/null)}"
DATASET="${BQ_DATASET:-aquapulse}"
LOCATION="${BQ_LOCATION:-asia-northeast1}"

if [[ -z "${PROJECT_ID}" || "${PROJECT_ID}" == "(unset)" ]]; then
  echo "Usage: $0 [PROJECT_ID]" >&2
  exit 1
fi

echo "Project: ${PROJECT_ID}"
echo "Dataset: ${DATASET} (${LOCATION})"

if ! bq show --project_id="${PROJECT_ID}" "${DATASET}" >/dev/null 2>&1; then
  bq mk \
    --project_id="${PROJECT_ID}" \
    --location="${LOCATION}" \
    --description="AquaPulse sensor and control data" \
    "${DATASET}"
fi

bq mk --project_id="${PROJECT_ID}" \
  --table \
  --time_partitioning_field=timestamp \
  --time_partitioning_type=DAY \
  --clustering_fields=sensor_id,sensor_type \
  --description="Sensor readings" \
  "${DATASET}.sensor_readings" \
  "${ROOT_DIR}/infra/bigquery/sensor_readings.schema.json" \
  2>/dev/null || echo "sensor_readings already exists"

bq mk --project_id="${PROJECT_ID}" \
  --table \
  --time_partitioning_field=timestamp \
  --time_partitioning_type=DAY \
  --clustering_fields=event_type,action \
  --description="Control and intervention events" \
  "${DATASET}.control_events" \
  "${ROOT_DIR}/infra/bigquery/control_events.schema.json" \
  2>/dev/null || echo "control_events already exists"

echo "BigQuery setup complete."
bq ls --project_id="${PROJECT_ID}" "${DATASET}"
