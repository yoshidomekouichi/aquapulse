# Cloud Agent Handoff — Phase 1 (2026-08-02)

**If you are a Cloud Agent (or any new AI session): read this file first.**

This memo captures decisions and live state after architecture validation on 2026-08-02. It prevents re-discovering the same Tapo/LAN/GCP issues.

**→ 2026-08-03 追記:** Mac Tapo poller **稼働中**。試行錯誤の全ログは  
[`docs/operations/tapo-poller-mac-setup-log-2026-08-03.md`](../operations/tapo-poller-mac-setup-log-2026-08-03.md) を読むこと。

---

## LIVE — Mac Tapo poller (2026-08-03)

| Item | Value |
|------|-------|
| Status | ✅ Hub + P300 → `ingest` → BigQuery (`device_id=mac_poller_v1`) |
| Mac WiFi | `aterm-b88a47-2s` (2.4GHz) — **must stay on `-2s`** |
| H100 hub IP | **192.168.10.110** (`TAPO_HUB_IP` in local `.env`) |
| P300 IP | **192.168.10.104** (`TAPO_P300_IP`) |
| Router | Aterm 3000D4AX: mesh **OFF**, secondary `-2s` **network isolation OFF** |
| Tapo app | 私 → 音声アシスタント → **サードパーティ連携 ON** (required for P300 / TPAP) |
| Schedule | cron `*/15` → `scripts/run-tapo-poller.sh` |
| Sleep | `scripts/keep-mac-awake.sh start` (caffeinate); lid close stops poller |
| Grafana | **Not set up** — data only in BigQuery for now |

**Stale docs warning:** handoff still listed P300 `.101` / hub `.103` — use table above.

---

## TL;DR

| Topic | Decision |
|-------|----------|
| **Phase 1a fan control** | **Manual via Tapo app** (alert-driven) |
| **Phase 1a scope** | **Monitoring only** — ESP32 → ingest → BigQuery → Grafana + Alerts |
| **GCP role** | **`ingest` only** — telemetry to BigQuery |
| **GCP `thermostat`** | Deployed for test; **does not work** to Tapo (LAN unreachable) — **not used in Phase 1** |
| **ESP32 Tapo control** | **Not possible** — MicroPython cannot handle Tapo encryption (TPAP/SPAKE2+) |
| **Raspberry Pi** | **Not used** (ADR-0001) |
| **VPN / extra router** | Deferred to Phase 1b (post-Obon) |
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

### MicroPython cannot control Tapo P300

**Finding:** Direct Tapo control from ESP32/MicroPython is **not feasible**.

**Reasons:**

1. **No MicroPython library** — PyPI `tapo` is Python-only (6.5MB Rust binary)
2. **Complex encryption** — Tapo uses TPAP/SPAKE2+ (requires elliptic curve crypto, not available in MicroPython)
3. **No implementation examples** — All ESP32+Tapo examples use intermediate relay servers

**Decision:** Phase 1 split into monitoring-only (Phase 1a) + automation later (Phase 1b).

See: [ADR-0008](../decisions/0008-phase1-split-monitoring-only.md)

### Home network

| Item | Value |
|------|-------|
| ISP | BIGLOBE Hikari + NTT ONU |
| Router | NEC **Aterm 3000D4AX** (BIGLOBE rental) |
| Router mode | Local router |
| IPv4 / IPv6 | Both internet available |
| VPN server menu | **None** (WireGuard/OpenVPN/Tailscale not built-in) |
| Port mapping | Available, currently empty |
| Tapo P300 IP | **`192.168.10.104`** (local `.env`; Secret Manager `tapo-p300-ip` may still be `.101`) |
| Tapo H100 hub IP | **`192.168.10.110`** (was `.103` before mesh/off SSID migration) |
| WiFi SSID (IoT) | **`aterm-b88a47-2s`** (2.4GHz secondary; isolation must be OFF) |

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

## Phase 1a target architecture (updated 2026-08-02)

```
┌─────────────────────────────────────┐
│  Aquarium (same WiFi LAN)           │
│                                     │
│  ESP32 ──DS18B20── water temp       │
│    │                                │
│    └──HTTP POST──► ingest (GCP)     │
│                      └──► BigQuery  │
│                           └──► Grafana
│                                │
│                                └──► Alerts (≥28°C)
│                                     └──► Email/LINE
│                                          │
│                                          ↓
│                                      User checks phone
│                                          │
│                                          ↓
│                                      Tapo app (manual)
│                                          │
│                                          ↓
│                                      Tapo P300 ─► Fan
└─────────────────────────────────────┘
```

### Thresholds (Alert-based, manual action)

- Alert **trigger** when temperature **≥ 28.0°C**
- User manually turns fan ON via Tapo app
- Monitor temperature drop
- User manually turns fan OFF when **≤ 26.0°C**

---

## Repository map (what to read)

| Priority | Path | Purpose |
|----------|------|---------|
| 1 | **This file** | Session context |
| 2 | [ADR-0008](../decisions/0008-phase1-split-monitoring-only.md) | **Phase 1a: Monitoring only (manual fan control)** |
| 3 | [ADR-0007](../decisions/0007-esp32-edge-thermostat-phase1.md) | Superseded (ESP32 edge control investigation) |
| 4 | [implementation-kickoff-2026-08.md](./implementation-kickoff-2026-08.md) | Phase 1 tasks & deadline |
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
- [x] Architecture decision: ESP32 edge thermostat (ADR-0007) → Superseded
- [x] **MicroPython Tapo control investigation: Not feasible** (ADR-0008)
- [x] **Phase 1 split decision: Monitoring only + manual fan control** (ADR-0008)
- [x] **Tapo sensor relocation** (2026-08-02 22:41 JST): Moved from window area to near aquarium for accurate temperature monitoring
- [x] **Event logging started**: `docs/logs/intervention-events.md` for manual AC/fan control tracking
- [x] **Mac Tapo poller** — scripts, cron, Hub+P300 → BigQuery (2026-08-03)
- [x] **Aterm WiFi fix** — mesh off, `-2s` isolation off, all IoT on `-2s` (see setup log)
- [x] **BigQuery verified** — `mac_poller_v1` room temp/humidity + P300 power_state

### TODO 🔲 (Phase 1a — by 2026-08-08)

- [ ] ESP32 wiring + DS18B20 read
- [ ] ESP32 WiFi + POST to `ingest`
- [ ] Verify **ESP32** data in BigQuery (Tapo path ✅)
- [ ] **Grafana Cloud + BigQuery** datasource + dashboard (see B5 manual; ~30–45 min)
- [ ] Update Secret Manager `tapo-p300-ip` → `.104` (if still `.101`)
- [ ] Router DHCP reservation for `.110` / `.104`
- [ ] Grafana alert (≥28°C → Email/LINE)
- [ ] Test alert delivery (heat water or inject test data)
- [ ] Test remote Tapo app fan control
- [ ] 3-day continuous monitoring test (99%+ uptime)

### Deferred / Backlog (Phase 1b — post-Obon)

- Automated fan control (GL.iNet + VPN or alternative) — ADR-0009 (to be written)
- ESP32 OTA updates ([BACKLOG.md](../../BACKLOG.md))
- Update `aquarium-thermostat-complete-manual.md` for Phase 1a scope

---

## What changed vs original design

| Original | Phase 1a (current) |
|----------|-------------------|
| ESP32 sends temperature only | ESP32 sends temperature only (**unchanged**) |
| GCP `thermostat` controls fan | **No automation** — user controls via Tapo app |
| Tapo creds in Secret Manager | Tapo creds **stay in Tapo app only** |
| Change thresholds via env/deploy | Alert thresholds in Grafana (editable) |
| Remote curl fan control | **Manual Tapo app control** |

**Unchanged:** ingest, BigQuery schema, Grafana data path, ESP32 as sensor platform.

---

## Suggested next conversation topics

1. ESP32 `main.py` structure: measure → POST ingest (no Tapo control)
2. Where to store WiFi credentials on ESP32 (`secrets.py`, gitignored)
3. Grafana alert configuration (Email/LINE integration)
4. Local test on Mac LAN before mounting behind aquarium
5. **Post-Obon:** Evaluate Phase 1b automation approach (GL.iNet + VPN or alternative)

---

## Copy-paste prompt for Cloud Agent

```
AquaPulse Phase 1a. Read in order:
1. docs/guides/cloud-agent-handoff-2026-08.md
2. docs/operations/tapo-poller-mac-setup-log-2026-08-03.md  ← try/error log

LIVE: Mac poller → ingest → BigQuery OK (Hub .110, P300 .104, WiFi -2s).
TODO next: Grafana Cloud + BQ dashboard, ESP32+DS18B20, alerts ≥28°C.
Do NOT redo Tapo LAN troubleshooting unless poller breaks.
Deadline 2026-08-08. Reply in Japanese. Ask before GCP deploy/commit.
```

*(Replace branch/path if not yet merged to `main`.)*

---

**Last updated:** 2026-08-03  
**Author context:** Local Mac session — Tapo poller E2E + Aterm WiFi migration complete.
