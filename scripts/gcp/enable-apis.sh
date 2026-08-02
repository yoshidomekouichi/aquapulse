#!/usr/bin/env bash
# Enable APIs required for AquaPulse Phase 1.
set -euo pipefail

PROJECT_ID="${1:-$(gcloud config get-value project 2>/dev/null)}"
if [[ -z "${PROJECT_ID}" || "${PROJECT_ID}" == "(unset)" ]]; then
  echo "Usage: $0 [PROJECT_ID]" >&2
  echo "Or run: gcloud config set project aquapulse-dev" >&2
  exit 1
fi

echo "Enabling APIs for project: ${PROJECT_ID}"

gcloud services enable \
  cloudfunctions.googleapis.com \
  cloudbuild.googleapis.com \
  bigquery.googleapis.com \
  secretmanager.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  --project="${PROJECT_ID}"

echo "Done."
