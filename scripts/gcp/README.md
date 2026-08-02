# GCP Phase 1 Setup (Track B)

Scripts for AquaPulse Phase 1 cloud setup.

> **2026-08-02:** Fan control moved to ESP32 (ADR-0007). Deploy **`ingest` only** for Phase 1.  
> Handoff memo: [docs/guides/cloud-agent-handoff-2026-08.md](../../docs/guides/cloud-agent-handoff-2026-08.md)

## Prerequisites

1. `aquapulse-dev` project created in GCP Console
2. Billing linked to **aquapulse-dev only**
3. `gcloud auth login` completed
4. Default project set:

```bash
gcloud config set project aquapulse-dev
gcloud config set functions/region asia-northeast1
```

## Quick start

```bash
cd ~/Projects/aquapulse
chmod +x scripts/gcp/*.sh

./scripts/gcp/enable-apis.sh
./scripts/gcp/setup-bigquery.sh
./scripts/gcp/create-secrets.sh
./scripts/gcp/deploy-ingest.sh
```

## Test ingest

```bash
INGEST_URL="$(gcloud functions describe ingest --gen2 --region=asia-northeast1 --format='value(serviceConfig.uri)')"

curl -X POST "${INGEST_URL}" \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "ds18b20_001",
    "sensor_type": "temperature",
    "location": "aquarium",
    "value": 25.5,
    "unit": "celsius",
    "device_id": "esp32_001",
    "firmware_version": "v1.0.0"
  }'
```

Verify:

```bash
bq query --use_legacy_sql=false \
  'SELECT * FROM `aquapulse.sensor_readings` ORDER BY timestamp DESC LIMIT 5'
```

## Thermostat (not Phase 1 production)

GCP **`thermostat`** cannot reach Tapo on `192.168.x.x` without VPN. See ADR-0007.

- `deploy-thermostat.sh` — kept for experiments only
- Phase 1 fan control — **ESP32 on home LAN**

## Budget alert (recommended)

Billing → Budgets → create alert at ¥1,000/month for `aquapulse-dev`.
