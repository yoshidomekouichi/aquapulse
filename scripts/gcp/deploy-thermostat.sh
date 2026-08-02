#!/usr/bin/env bash
# Deploy thermostat Cloud Function (Gen2).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT_ID="${1:-$(gcloud config get-value project 2>/dev/null)}"
REGION="${GCP_REGION:-asia-northeast1}"
PROJECT_NUMBER="$(gcloud projects describe "${PROJECT_ID}" --format='value(projectNumber)')"
SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

if [[ -z "${PROJECT_ID}" || "${PROJECT_ID}" == "(unset)" ]]; then
  echo "Usage: $0 [PROJECT_ID]" >&2
  exit 1
fi

echo "Granting Secret Manager access to ${SA} (if not already granted)..."
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SA}" \
  --role="roles/secretmanager.secretAccessor" \
  --condition=None >/dev/null 2>&1 || true

gcloud functions deploy thermostat \
  --gen2 \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --runtime=python312 \
  --source="${ROOT_DIR}/cloud-functions/thermostat" \
  --entry-point=thermostat \
  --trigger-http \
  --allow-unauthenticated \
  --timeout=120s \
  --memory=512Mi \
  --max-instances=5 \
  --set-env-vars="BQ_DATASET=aquapulse,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},THRESHOLD_HIGH=28.0,THRESHOLD_LOW=26.0"

THERMOSTAT_URL="$(gcloud functions describe thermostat \
  --gen2 \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --format='value(serviceConfig.uri)')"

echo "Deployed thermostat: ${THERMOSTAT_URL}"
