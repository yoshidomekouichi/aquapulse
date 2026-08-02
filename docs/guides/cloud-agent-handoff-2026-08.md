# Cloud Agent Handoff — Phase 1 (2026-08-02)

**If you are a Cloud Agent (or any new AI session): read this file first.**

This memo captures decisions and live state after architecture validation on 2026-08-02. It prevents re-discovering the same Tapo/LAN/GCP issues.

---

## TL;DR

| Topic | Decision |
|-------|----------|
| **Phase 1 fan control** | **ESP32 on home WiFi** controls Tapo P300 directly |
| **GCP role** | **`ingest` only** — telemetry to BigQuery |
| **GCP `thermostat`** | Deployed for test; **does not work** to Tapo (LAN unreachable) — **not used in Phase 1** |
| **Raspberry Pi** | **Not used** (ADR-0001) |
| **VPN / extra router** | Deferred — cost/complexity; router has no VPN server |
| **Deadline** | 2026-08-08 |
| **Language** | User prefers **Japanese** explanations |

---

## User preferences (important)

1. **Educational stance** — explain what/why/before doing; don't silently change code or deploy to GCP
2. **Minimize hardware** — ESP32 + existing Tapo P300 + existing router
3. **Avoid Pi dependency** — SSH/physical access behind aquarium is a known failure mode
4. **Mac is the dev environment** — ESP32 updates via USB (OTA is backlog, not Phase 1 blocker)
5. **Only commit/deploy when user explicitly asks**

---

## What we learned (2026-08-02)

### Cloud Function cannot reach Tapo

```
curl → thermostat (GCP Tokyo) → 192.168.10.101 (Tapo)
Result: TimeoutError — "Timed out getting discovery response"
```

GCP public cloud **cannot** open connections to private `192.168.x.x` on home LAN.

### Home network

| Item | Value |
|------|-------|
| ISP | BIGLOBE Hikari + NTT ONU |
| Router | NEC **Aterm 3000D4AX** (BIGLOBE rental) |
| Router mode | Local router |
| IPv4 / IPv6 | Both internet available |
| VPN server menu | **None** (WireGuard/OpenVPN/Tailscale not built-in) |
| Port mapping | Available, currently empty |
| Tapo P300 IP | `192.168.10.101` (Secret Manager: `tapo-p300-ip`) |

### Cost options we compared

| Option | Initial | Monthly | Verdict |
|--------|---------|---------|---------|
| ESP32 edge control | ESP32 ~¥2,500 | ~¥0 | **Chosen for Phase 1** |
| GL.iNet + GCP free VM (us-west1) + Tailscale | ~¥5,000–10,000 | ~¥0 | Future if ESP32 Tapo fails |
| GCP e2-micro Tokyo always-on | — | ~¥6,500 | Too expensive |
| BIGLOBE fixed IP | ¥8,800 | ¥3,850 | Expensive; IPoE may block |

Full rationale: [ADR-0007](../decisions/0007-esp32-edge-thermostat-phase1.md)

---

## GCP live state (`aquapulse-dev`)

| Resource | Status | Notes |
|----------|--------|-------|
| Project | ✅ `aquapulse-dev` | Billing linked |
| BigQuery dataset | ✅ `aquapulse` | `sensor_readings`, `control_events` |
| Secret Manager | ✅ | `tapo-username`, `tapo-password`, `tapo-p300-ip` |
| **`ingest`** CF Gen2 | ✅ **Working** | Test row in BigQuery (25.5°C) |
| **`thermostat`** CF Gen2 | ⚠️ Deployed, **not for production** | URL works but Tapo timeout |

### URLs (asia-northeast1)

- **ingest:** `https://ingest-e4jnfqozuq-an.a.run.app`
- **thermostat:** `https://thermostat-e4jnfqozuq-an.a.run.app` (LAN test failed)

### Test ingest

```bash
curl -X POST "https://ingest-e4jnfqozuq-an.a.run.app" \
  -H "Content-Type: application/json" \
  -d '{"sensor_id":"ds18b20_001","sensor_type":"temperature","location":"aquarium","value":25.5,"unit":"celsius","device_id":"esp32_001","firmware_version":"v1.0.0"}'
```

---

## Phase 1 target architecture

```
┌─────────────────────────────────────┐
│  Aquarium (same WiFi LAN)           │
│                                     │
│  ESP32 ──DS18B20── water temp       │
│    │                                │
│    ├──HTTP POST──► ingest (GCP)      │
│    │                 └──► BigQuery  │
│    │                      └──► Grafana
│    │                                │
│    └──LAN────────► Tapo P300        │
│                      └──► 12V fan   │
│         (hysteresis on ESP32)       │
└─────────────────────────────────────┘
```

### Thresholds

- Fan **ON** when temperature **≥ 28.0°C**
- Fan **OFF** when temperature **≤ 26.0°C**
- Measure / act every **~60 seconds**

---

## Repository map (what to read)

| Priority | Path | Purpose |
|----------|------|---------|
| 1 | **This file** | Session context |
| 2 | [ADR-0007](../decisions/0007-esp32-edge-thermostat-phase1.md) | Why ESP32 edge control |
| 3 | [implementation-kickoff-2026-08.md](./implementation-kickoff-2026-08.md) | Phase 1 tasks & deadline |
| 4 | [ADR-0001](../decisions/2026-07-05-migrate-to-esp32-gcp.md) | Why not Raspberry Pi |
| 5 | `cloud-functions/ingest/main.py` | Deployed ingest code |
| 6 | `cloud-functions/thermostat/main.py` | Reference only (python-kasa) |
| 7 | `scripts/gcp/` | Deploy scripts |
| 8 | [getting-started-esp32.md](../tutorials/getting-started-esp32.md) | ESP32 tutorial |
| 9 | [aquarium-thermostat-complete-manual.md](./aquarium-thermostat-complete-manual.md) | Long reference (部分は CF 前提で古い) |

---

## Done vs TODO

### Done ✅

- [x] GCP project `aquapulse-dev` + APIs + BigQuery + secrets
- [x] `ingest` deployed and curl-tested
- [x] `thermostat` deployed; **proved Tapo unreachable from GCP**
- [x] Router surveyed: no VPN server; port mapping available
- [x] Architecture decision: ESP32 edge thermostat (ADR-0007)

### TODO 🔲 (Phase 1)

- [ ] **Verify MicroPython can control Tapo P300** (blocker — research first)
- [ ] ESP32 wiring + DS18B20 read
- [ ] ESP32 WiFi + POST to `ingest`
- [ ] ESP32 hysteresis + Tapo fan ON/OFF
- [ ] Optional: POST `control_events` from ESP32
- [ ] Grafana dashboard
- [ ] 3–5 day soak test before 2026-08-08 absence
- [ ] LINE notify on fan state change (if time permits)

### Deferred / Backlog

- Cloud Function `thermostat` via VPN (GL.iNet + free VM)
- ESP32 OTA updates ([BACKLOG.md](../../BACKLOG.md))
- Update `aquarium-thermostat-complete-manual.md` CF sections

---

## What changed vs original design

| Original | Phase 1 (current) |
|----------|-------------------|
| ESP32 sends temperature only | ESP32 also controls Tapo |
| GCP `thermostat` controls fan | **`ingest` only on GCP** |
| Tapo creds in Secret Manager | Tapo creds on ESP32 (local config) |
| Change thresholds via env/deploy | USB reflash (or later: config JSON from GCS) |
| Remote curl fan control | Not in Phase 1 (Tapo app manual OK) |

**Unchanged:** ingest, BigQuery schema, Grafana data path, ESP32 as sensor platform.

---

## Suggested next conversation topics

1. Research: MicroPython / HTTP client for Tapo P300 (replace `python-kasa`)
2. ESP32 `main.py` structure: measure → decide → act → POST ingest
3. Where to store WiFi/Tapo secrets on ESP32 (`secrets.py`, gitignored)
4. Local test on Mac LAN before mounting behind aquarium

---

## Copy-paste prompt for Cloud Agent

```
AquaPulse Phase 1. Read first:
https://github.com/yoshidomekouichi/aquapulse/blob/main/docs/guides/cloud-agent-handoff-2026-08.md

Summary: ESP32 controls Tapo fan on LAN; GCP ingest only. CF thermostat doesn't reach Tapo.
Deadline 2026-08-08. Reply in Japanese. Ask before deploying to GCP.
```

*(Replace branch/path if not yet merged to `main`.)*

---

**Last updated:** 2026-08-02  
**Author context:** Desktop Cursor session validated GCP + router + architecture pivot.
