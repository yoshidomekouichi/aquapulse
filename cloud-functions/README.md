# Cloud Functions (Phase 1)

GCP Cloud Functions for AquaPulse Phase 1.

> **Architecture update (2026-08-02):** See [ADR-0007](../docs/decisions/0007-esp32-edge-thermostat-phase1.md).  
> **New AI session:** [cloud-agent-handoff-2026-08.md](../docs/guides/cloud-agent-handoff-2026-08.md)

## Functions

| Function | Role | Phase 1 deploy target |
|----------|------|------------------------|
| `ingest` | Receive ESP32 JSON and write to BigQuery | **GCP Cloud Functions** ✅ |
| `thermostat` | Hysteresis fan control via Tapo P300 | **Not used** — see below |

## Why `thermostat` is not on GCP for Phase 1

Tapo P300 uses a private LAN IP (`192.168.x.x`). **Cloud Functions in GCP cannot reach it directly.**

Verified 2026-08-02:

```bash
curl -X POST "https://thermostat-e4jnfqozuq-an.a.run.app" \
  -H "Content-Type: application/json" -d '{"value": 29.0}'
# → {"error": "Timed out getting discovery response for 192.168.10.101"}
```

### Phase 1 approach (ADR-0007)

1. Deploy **`ingest`** to GCP (`asia-northeast1`) — **done**
2. Run **fan hysteresis + Tapo control on ESP32** (same WiFi as Tapo)
3. Keep `cloud-functions/thermostat/` as **reference** (`python-kasa`) for a future VPN path

### Future alternatives (not Phase 1)

- GL.iNet Tailscale subnet router + GCP VM (free tier) running this code
- Home LAN agent (avoid Raspberry Pi per ADR-0001 unless unavoidable)

## Thresholds (implemented on ESP32 in Phase 1)

- Fan ON: `>= 28.0` C (`THRESHOLD_HIGH`)
- Fan OFF: `<= 26.0` C (`THRESHOLD_LOW`)

## Local test

```bash
# ingest
cd cloud-functions/ingest
functions-framework --target=ingest --port=8081 --debug

curl -X POST http://127.0.0.1:8081 \
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

## Deploy

See `scripts/gcp/README.md`.

- **`ingest`:** `./scripts/gcp/deploy-ingest.sh`
- **`thermostat`:** `./scripts/gcp/deploy-thermostat.sh` — experimental only; not for Phase 1 production
