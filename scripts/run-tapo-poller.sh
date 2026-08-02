#!/usr/bin/env bash
# Run Mac Tapo poller (loads .env from repo root).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

if [[ -f "${ROOT}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${ROOT}/.env"
  set +a
fi

exec "${ROOT}/.venv/bin/python" "${ROOT}/scripts/tapo_poller.py" "$@"
