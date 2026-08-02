# ADR-0007: ESP32 Edge Thermostat for Phase 1

## Status

Superseded (2026-08-02) → See ADR-0008 for Phase 1 split decision  
Original approval: 2026-08-02  
Superseded by: ADR-0008 (Phase 1a: Monitoring only, Phase 1b: Automation post-Obon)

## Context

Phase 1 originally assumed this flow:

```
ESP32 → ingest (GCP) → BigQuery
ESP32 → thermostat (GCP) → Tapo P300 (192.168.x.x)
```

On 2026-08-02 we deployed `thermostat` to GCP (`aquapulse-dev`, `asia-northeast1`) and tested with curl:

```json
{"error": "Timed out getting discovery response for 192.168.10.101"}
```

**Root cause:** Cloud Functions run on GCP public cloud. Tapo P300 uses a private LAN IP. GCP cannot reach home LAN devices without a VPN or LAN-side agent.

We also verified the home router:

| Item | Result |
|------|--------|
| Device | NEC Aterm 3000D4AX (BIGLOBE rental) |
| VPN server (WireGuard / OpenVPN / Tailscale) | **Not available** in admin UI |
| Port mapping | Available (empty entries) |
| BIGLOBE fixed IP option | ~¥3,850/month; often incompatible with IPoE/IPv6-heavy setups |

The feasibility report marked cloud Tapo control as "no problem" **without validating cloud→LAN reachability**. This ADR records the correction.

### User constraints

- Avoid Raspberry Pi (SSH recovery risk, physical access behind aquarium)
- Minimize extra hardware and monthly cost
- Prefer editing logic on Mac when possible
- Phase 1 deadline: **2026-08-08**

## Alternatives Considered

### A. Cloud Function thermostat + home VPN

- GL.iNet subnet router (~¥5,000–10,000) + GCP VM with Tailscale
- pros: Keep `cloud-functions/thermostat/main.py`; edit on Mac; deploy via git
- cons: Extra hardware; VM setup (free tier possible in `us-west1`, not Tokyo); more moving parts

### B. Cloud Function thermostat + BIGLOBE fixed IP

- pros: No extra LAN device
- cons: ~¥3,850/month; may not work with current IPoE/IPv6 setup; still needs inbound path design

### C. Raspberry Pi on home LAN running thermostat

- pros: Reuse existing `python-kasa` code
- cons: Conflicts with ADR-0001 goals; SSH/access risk returns

### D. ESP32 edge control (Adopted for Phase 1)

- ESP32 on same WiFi as Tapo: read DS18B20, apply hysteresis, control Tapo, POST telemetry to `ingest`
- pros: **No extra hardware**; **~¥0/month**; no VPN; aligns with "ESP32 only" hardware goal
- cons: Tapo control must work in **MicroPython** (not `python-kasa`); firmware updates via **USB** unless OTA added later; no remote curl fan override

## Decision

Adopt **D: ESP32 edge thermostat for Phase 1**.

Keep **`ingest` on GCP** (already deployed and verified). **Do not use GCP `thermostat` for production** in Phase 1. The code in `cloud-functions/thermostat/` remains as reference / future VPN path.

### Phase 1 architecture

```
[ESP32 + DS18B20]
      │
      ├─ WiFi → ingest (GCP) → BigQuery → Grafana
      │
      └─ WiFi (LAN) → Tapo P300 → 12V fan
            (28°C ON / 26°C OFF hysteresis on ESP32)
```

## Consequences

### Positive

- Lowest cost and simplest hardware for Phase 1
- `ingest` + BigQuery + Grafana path unchanged
- No Raspberry Pi, no VPN router, no always-on GCP VM
- Validates LAN path to Tapo from a device on the same network

### Negative

- Thermostat logic moves from Cloud Functions to ESP32 firmware
- Code changes require USB flash (or future OTA per BACKLOG)
- Tapo credentials stored on ESP32 (not Secret Manager)
- `control_events` must be POSTed from ESP32 if we want BigQuery audit trail

### Risks

- **MicroPython Tapo library may not exist or may be fragile** — must verify before implementation
- Threshold changes need reflash unless config-over-HTTP/GCS is added later
- Manual override only via Tapo app (not curl to cloud)

## Related Materials

- [Cloud Agent handoff memo](../guides/cloud-agent-handoff-2026-08.md) — **start here for new sessions**
- [Implementation kickoff](../guides/implementation-kickoff-2026-08.md)
- [ADR-0001](2026-07-05-migrate-to-esp32-gcp.md)
- `cloud-functions/thermostat/` — deployed once for test; not used in production Phase 1
- `scripts/gcp/deploy-thermostat.sh` — keep for future VPN experiments
