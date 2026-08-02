#!/usr/bin/env bash
# Deploy ingest Cloud Function (Gen2).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT_ID="${1:-$(gcloud config get-value project 2>/dev/null)}"
REGION="${GCP_REGION:-asia-northeast1}"

if [[ -z "${PROJECT_ID}" || "${PROJECT_ID}" == "(unset)" ]]; then
  echo "Usage: $0 [PROJECT_ID]" >&2
  exit 1
fi

gcloud functions deploy ingest \
  --gen2 \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --runtime=python312 \
  --source="${ROOT_DIR}/cloud-functions/ingest" \
  --entry-point=ingest \
  --trigger-http \
  --allow-unauthenticated \
  --timeout=60s \
  --memory=256Mi \
  --max-instances=10 \
  --set-env-vars="BQ_DATASET=aquapulse,GOOGLE_CLOUD_PROJECT=${PROJECT_ID}"

INGEST_URL="$(gcloud functions describe ingest \
  --gen2 \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --format='value(serviceConfig.uri)')"

echo "Deployed ingest: ${INGEST_URL}"
