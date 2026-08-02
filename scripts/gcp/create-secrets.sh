#!/usr/bin/env bash
# Create Tapo secrets in Secret Manager (interactive).
set -euo pipefail

PROJECT_ID="${1:-$(gcloud config get-value project 2>/dev/null)}"

if [[ -z "${PROJECT_ID}" || "${PROJECT_ID}" == "(unset)" ]]; then
  echo "Usage: $0 [PROJECT_ID]" >&2
  exit 1
fi

read -r -p "Tapo username (email): " TAPO_USERNAME
read -r -s -p "Tapo password: " TAPO_PASSWORD
echo
read -r -p "Tapo P300 IP (e.g. 192.168.3.8): " TAPO_IP

create_or_update() {
  local name="$1"
  local value="$2"
  if gcloud secrets describe "${name}" --project="${PROJECT_ID}" >/dev/null 2>&1; then
    printf '%s' "${value}" | gcloud secrets versions add "${name}" \
      --project="${PROJECT_ID}" \
      --data-file=-
  else
    printf '%s' "${value}" | gcloud secrets create "${name}" \
      --project="${PROJECT_ID}" \
      --replication-policy=automatic \
      --data-file=-
  fi
}

create_or_update tapo-username "${TAPO_USERNAME}"
create_or_update tapo-password "${TAPO_PASSWORD}"
create_or_update tapo-p300-ip "${TAPO_IP}"

echo "Secrets created/updated in project ${PROJECT_ID}."
