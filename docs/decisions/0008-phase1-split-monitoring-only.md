# ADR-0008: Phase 1 Split — Monitoring Only (Manual Fan Control)

## Status

Approved (2026-08-02)

## Context

ADR-0007 proposed ESP32 edge thermostat with direct Tapo P300 control via MicroPython. On 2026-08-02, investigation revealed:

### MicroPython Tapo Control Investigation Results

**Finding:** MicroPython cannot control Tapo P300 directly.

**Evidence:**

1. **No MicroPython Tapo library exists**
   - PyPI `tapo` (v0.9.0): Python-only, 6.5MB binary (Rust-based), incompatible with MicroPython
   - No community ports found

2. **Tapo P300 uses complex encryption**
   - Older firmware: KLAP v1/v2 (MD5/SHA-256 based)
   - **Newer firmware (2023+):** TPAP/SPAKE2+ protocol
     - Requires: SPAKE2+ key exchange, AES-128-CCM encryption, NIST P-256 elliptic curve
     - **Not implementable in MicroPython** (no elliptic curve crypto library)

3. **No ESP32 + Tapo direct control examples found**
   - Only example found: ESP32 → separate web server (Python) → Tapo
   - Quote: "A direct port to the ESP32 would be nice, for now, using the web server is a functional workaround"

4. **Kasa (old models) are MicroPython-compatible**
   - Simple XOR encryption (port 9999, TCP)
   - Multiple MicroPython implementations exist (`the-kwak/Micro-python-kasa`, etc.)
   - **But:** User already integrated Tapo P300 into Tapo app ecosystem; switching devices is disruptive

### User Constraints

- Tapo P300 already in production use via Tapo app
- Cannot switch to Kasa at this stage (disrupts existing workflows)
- Deadline: 2026-08-08 (6 days remaining)
- Goal: Fish safety during 1-week Obon absence

## Alternatives Considered

### A. Switch to Kasa HS100/HS110 (Rejected)

- pros: MicroPython-compatible; proven implementations
- cons: **Tapo P300 already in production**; switching disrupts existing Tapo app workflows; requires new hardware purchase

### B. GL.iNet + VPN + Cloud Functions (Deferred to Phase 1b)

- pros: Reuses Cloud Functions `thermostat` code; Tapo P300 stays in use
- cons: **Cannot meet 6-day deadline**; requires GL.iNet purchase (~¥5,000-10,000) + VPN setup (1-2 weeks)

### C. Mac relay server (Rejected)

- pros: Can be implemented quickly; Tapo P300 stays in use
- cons: **Mac must run 24/7 during Obon**; single point of failure; conflicts with ADR-0001 (avoid always-on devices)

### D. Phase 1 split: Monitoring only + manual fan control (Adopted)

**Phase 1a (by 2026-08-08):**
- ESP32 + DS18B20 → ingest (GCP) → BigQuery → Grafana
- Grafana alerts on temperature thresholds (≥28°C)
- **Fan control: Manual via Tapo app** (user receives alert, toggles fan remotely)

**Phase 1b (post-Obon, after 2026-08-16):**
- Implement automated fan control (GL.iNet + VPN or alternative)

- pros: **Meets deadline with certainty**; fish safety via monitoring + alerts; manual control is viable (remote Tapo app access); Tapo P300 stays in use
- cons: Not fully automated for Obon period; requires user intervention on alerts

## Decision

Adopt **D: Phase 1 split**.

### Phase 1a Architecture (by 2026-08-08)

```
[ESP32 + DS18B20]
      │
      └─ WiFi → ingest (GCP) → BigQuery → Grafana
                                              │
                                              └─ Alerts (≥28°C) → Email/LINE
                                                      │
                                                      ↓
                                                  User checks Tapo app
                                                      ↓
                                                  Manual fan ON/OFF
```

### Phase 1b (post-Obon)

Deferred to ADR-0009 (to be written). Candidates:
- GL.iNet + Tailscale VPN + Cloud Functions `thermostat`
- Alternative relay solution (evaluate based on Obon experience)

## Consequences

### Positive

- **Meets Phase 1 deadline with high confidence** (3 days implementation + 3 days testing)
- **Fish safety ensured** via real-time monitoring + alerts
- Simple, proven technology stack (DS18B20, HTTP POST, BigQuery, Grafana)
- Tapo P300 remains in existing workflow
- Manual fan control is **viable** (Tapo app accessible remotely from anywhere)
- No new hardware purchases required
- No complex encryption/VPN setup under time pressure

### Negative

- Not fully automated during Obon absence
- Requires user to respond to alerts (check phone, open Tapo app, toggle fan)
- Alert fatigue risk if temperature oscillates near threshold (mitigated by hysteresis in alerting)

### Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| User misses alert (phone off, no signal) | High | **Redundant alerts**: Email + LINE; test alert delivery before departure |
| Grafana/GCP downtime | Medium | **Pre-Obon test**: 3-day continuous monitoring; verify 99%+ uptime |
| False alarms (sensor drift) | Low | **Calibration**: Test DS18B20 accuracy vs thermometer before deployment |
| User forgets Tapo credentials | Low | **Document credentials** in secure location (password manager) |

### Success Criteria (Phase 1a)

- [ ] ESP32 sends temperature every 60s to BigQuery (verified via Grafana)
- [ ] Grafana dashboard displays real-time temperature
- [ ] Alert triggers at ≥28°C (tested by heating water or injecting test data)
- [ ] Alert delivered to user's phone (Email + LINE)
- [ ] User can toggle Tapo P300 via app from remote location (tested)
- [ ] System runs continuously for 3+ days without restart (99%+ uptime)

## Implementation Timeline

```
Day 1-2 (2026-08-02 ~ 08-03):
  - ESP32 + DS18B20 wiring
  - MicroPython: WiFi + HTTP POST to ingest
  - Verify data in BigQuery

Day 3 (2026-08-04):
  - Grafana dashboard
  - Alert configuration (≥28°C → Email/LINE)
  - Test alert delivery

Day 4-6 (2026-08-05 ~ 08-07):
  - Continuous 3-day test
  - Monitor for failures, alert accuracy
  - User practices remote Tapo app control

Day 7 (2026-08-08):
  - Departure-ready
  - Final checklist verification
```

## Related Materials

- [ADR-0007](0007-esp32-edge-thermostat-phase1.md) — Superseded (ESP32 edge control investigation)
- [Cloud Agent handoff memo](../guides/cloud-agent-handoff-2026-08.md) — Update with Phase 1a scope
- [Implementation kickoff](../guides/implementation-kickoff-2026-08.md) — Update with monitoring-only scope
- [MicroPython Tapo investigation](../guides/cloud-agent-handoff-2026-08.md#micropython-tapo-research) — Technical findings (to be added)

## Post-Obon Review

After returning from Obon (2026-08-16+), evaluate:

1. **How many alerts were received?**
2. **Response time to alerts** (alert → Tapo app action)
3. **False positive rate** (unnecessary alerts)
4. **User experience** (was manual control acceptable?)

Based on this data, decide Phase 1b automation approach (ADR-0009).
