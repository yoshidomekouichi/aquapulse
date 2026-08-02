# Implementation Kickoff: Aquarium Thermostat System

**Created:** 2026-08-01  
**Target Completion:** 2026-08-08 (1 week)  
**Phase:** Phase 1 - Basic Temperature Monitoring + Fan Control  
**Status:** 🚀 Ready to Start

---

## 🎯 Mission Critical Context

### Why This is Urgent

**Incident Background (2026-07-09):**
- Forgot to turn on fan manually
- Water temperature reached 30°C by evening
- Fish survived but were at risk
- **One more occurrence could be fatal**

**Upcoming Risk:**
- User will be absent for 1 week (Obon holiday)
- No manual intervention possible
- **Automated control is MANDATORY for fish survival**

### Success Criteria

By 2026-08-08, the system MUST:

✅ **Measure** water temperature every 60 seconds  
✅ **Send** data to GCP automatically  
✅ **Store** data in BigQuery  
✅ **Visualize** temperature in Grafana  
✅ **Control** Tapo P300 fan automatically:
   - Fan ON when ≥ 28°C
   - Fan OFF when ≤ 26°C
✅ **Notify** via LINE on fan state changes  
✅ **Test** continuously for 3-5 days before departure

---

## 🏗️ System Architecture

### Overview

```
[ESP32 + DS18B20]
      ↓ WiFi (HTTP POST every 60s)
[Cloud Functions: ingest]
      ↓
[BigQuery: sensor_readings] ← [Grafana: visualization]
      ↓ Query (every 60s)
[Cloud Functions: thermostat]
      ↓ Control command
[Tapo P300 Smart Plug]
      ↓ Power
[12V Cooling Fan]
```

### Key Technology Decisions

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Microcontroller | ESP32 (MicroPython) | WiFi built-in, Python simplicity |
| Sensor | DS18B20 (OneWire) | Waterproof, accurate (±0.5°C) |
| Cloud Platform | GCP (Cloud Functions + BigQuery) | Serverless, cost-effective |
| Smart Plug | Tapo P300 | Already owned, Python library available |
| Communication | HTTP POST (not MQTT) | **IoT Core retired Feb 2026**, HTTP is simpler |
| Visualization | Grafana Cloud | Free tier, BigQuery plugin available |

**Important:** Google Cloud IoT Core was retired. We use **direct HTTP POST to Cloud Functions** instead.

### Data Schema

**Table 1: `sensor_readings`** (Observations)

```sql
CREATE TABLE aquapulse.sensor_readings (
  timestamp TIMESTAMP,
  sensor_id STRING,
  sensor_type STRING,      -- 'temperature', 'tds', 'ph', 'room_temperature'
  location STRING,          -- 'aquarium', 'room'
  value FLOAT64,
  unit STRING,              -- 'celsius', 'ppm', 'pH', 'percent'
  device_id STRING,
  firmware_version STRING
)
PARTITION BY DATE(timestamp);
```

**Table 2: `control_events`** (Interventions)

```sql
CREATE TABLE aquapulse.control_events (
  event_id STRING,          -- UUID
  timestamp TIMESTAMP,
  event_type STRING,        -- 'automated_thermostat', 'manual_water_change'
  device_id STRING,
  action STRING,            -- 'fan_on', 'fan_off', 'water_change', 'fertilizer'
  action_details JSON,      -- Flexible field for non-switch actions
  trigger_type STRING,      -- 'automated', 'manual', 'scheduled'
  trigger_value FLOAT64,    -- Temperature that triggered action
  trigger_threshold FLOAT64,-- 28.0 for fan_on, 26.0 for fan_off
  success BOOLEAN,
  error_message STRING,
  execution_duration_ms INT64
)
PARTITION BY DATE(timestamp);
```

**Why two tables?**
- Different query patterns (observations vs interventions)
- Different retention policies (long-term vs short-term)
- Optimized for causal inference analysis

See: `docs/decisions/0006-simplified-schema-design.md`

---

## 📋 Implementation Plan

### Phase 1 Scope (This Week)

**In Scope:**
1. ESP32 temperature sensing (DS18B20)
2. WiFi connection and HTTP POST to Cloud Functions
3. BigQuery storage (`sensor_readings`, `control_events`)
4. Grafana visualization
5. Automated fan control (Tapo P300)
6. LINE notifications

**Out of Scope (Future):**
- TDS sensor (Phase 2)
- pH sensor (Phase 2)
- Universal PCB migration (Phase 2)
- OTA updates (Phase 3)
- Tapo IR remote control for AC (Phase 3)

### Development Environment Strategy

**Phase 1 (Current):**
- **No Cloud Agent environment setup** - Keep it simple, focus on implementation
- Use local agent for ESP32 (USB connection required)
- Use cloud agent opportunistically for GCP tasks (optional)
- Track dependencies as you go (for future environment setup)

**Phase 1 Completion (2 weeks from now):**
- Run system for 3-5 days, verify stability
- Decide: Continue to Phase 2 or stop here?
- If continuing → Set up Cloud Agent environment (10 minutes with agent-led setup)

**Phase 2+ (Future):**
- Cloud Agent environment ready (instant startup, 5 seconds)
- Parallel agent execution for multiple sensors
- Hybrid approach: Local for ESP32, Cloud for GCP/analysis
- 5-8 hours saved over Phase 2-3 development

**Why this order:**
1. Phase 1 is small enough to run efficiently without environment setup
2. ESP32 work requires local USB connection anyway
3. Agent-led setup needs a working repo to analyze (Phase 1 provides this)
4. Environment setup ROI is highest in Phase 2+ (parallel execution, long-running tasks)

### Recommended Implementation Order

Follow the manual's decoupled structure. You can work on these in parallel or any order:

#### Track A: Hardware (ESP32)

1. **A1-A3:** Hardware setup + MicroPython installation (1-2 hours)
   - Wire DS18B20 to ESP32 (GPIO 4, 3.3V, GND + 4.7kΩ pull-up)
   - Install MicroPython firmware
   - Test REPL connection

2. **A4-A5:** Sensor test + WiFi (1 hour)
   - Read temperature locally
   - Connect to WiFi
   - Test basic connectivity

#### Track B: Cloud (GCP)

1. **B1-B2:** GCP Project setup (30 min)
   - Create/verify project
   - Enable APIs (Cloud Functions, BigQuery, Secret Manager)
   - Set up gcloud CLI authentication

2. **B3:** Deploy `ingest` Cloud Function (1 hour)
   - HTTP endpoint to receive sensor data
   - Parses JSON payload
   - Inserts into BigQuery `sensor_readings`

3. **B4:** BigQuery setup (30 min)
   - Create dataset `aquapulse`
   - Create tables (`sensor_readings`, `control_events`)
   - Test with sample data

4. **B5:** Grafana setup (1 hour)
   - Connect to BigQuery
   - Create dashboard with temperature panel
   - Set up 30°C alert (optional)

5. **B6:** Tapo P300 setup (30 min)
   - Note IP address, username, password
   - Test with `python-kasa` library locally

6. **B3 (2nd function):** Deploy `thermostat` Cloud Function (1-2 hours)
   - Scheduled execution (every 60s)
   - Query latest temperature from BigQuery
   - Control Tapo P300 based on thresholds
   - Record events to `control_events` table
   - Send LINE notifications

#### Track C: Integration

1. **C1:** ESP32 → Cloud integration (1 hour)
   - Update ESP32 code to POST to `ingest` endpoint
   - Verify data arrives in BigQuery
   - Check Grafana displays new data

2. **C2:** Thermostat test (1 hour)
   - Manually heat water (or send test data)
   - Verify fan turns ON at 28°C
   - Verify fan turns OFF at 26°C
   - Check LINE notifications

3. **C3-C4:** End-to-end testing (2-3 hours)
   - Run continuously for 3-5 days
   - Monitor for errors
   - Verify 99%+ uptime
   - Check fan cycles correctly

### Time Estimate

| Track | Time | When |
|-------|------|------|
| A (Hardware) | 2-3 hours | Weekend afternoon |
| B (Cloud) | 4-5 hours | Weeknight sessions or weekend |
| C (Integration) | 2-3 hours | Weekend |
| **Total** | **8-11 hours** | **5-7 days** |

---

## 📚 Essential Documentation

### Primary Reference (Read This First)

**`docs/guides/aquarium-thermostat-complete-manual.md`** (4187 lines)
- Complete implementation manual in Japanese
- Includes all code, commands, and troubleshooting
- Sections A1-A5 (Hardware), B1-B6 (Cloud), C1-C4 (Integration)
- **Updated 2026-07-11 for new BigQuery schema**

### Schema and Design

**`docs/reference/schema.md`**
- Full schema definitions for `sensor_readings` and `control_events`
- Example JSON rows
- Storage strategy and cost analysis
- SQL query examples

**`docs/decisions/0006-simplified-schema-design.md`**
- Why separate tables for observations vs interventions
- Why `action_details` JSON field for flexibility
- Hybrid storage strategy (BigQuery + Cloud Storage Archive)

### Architecture History

**`docs/architecture/snapshots/2026-07-11-schema-finalization.md`**
- Evolution of schema design
- Hypothesis testing process
- Trade-offs and decisions

**`docs/decisions/2026-07-05-migrate-to-esp32-gcp.md`**
- Why ESP32 instead of Raspberry Pi
- Why GCP instead of local storage
- Technical constraints and rationale

### Project Management

**`BACKLOG.md`**
- Current task status
- Phase 1 (this week) vs Phase 2 (future)
- Completed work (PRs #55-59)

---

## ⚠️ Critical Technical Notes

### 1. Google Cloud IoT Core is Retired

**What happened:**
- Google Cloud IoT Core retired February 2026
- MQTT-based communication is no longer available via GCP

**Our solution:**
- Use **HTTP POST directly to Cloud Functions**
- No third-party MQTT broker needed for Phase 1
- Simpler setup, fewer dependencies

**Code impact:**
```python
# ESP32 code (MicroPython)
import urequests

url = "https://REGION-PROJECT.cloudfunctions.net/ingest"
payload = {"sensor_id": "ds18b20_001", "value": 26.5, ...}
response = urequests.post(url, json=payload)
```

### 2. Hysteresis for Fan Control

**Problem:** Without hysteresis, fan would cycle rapidly at threshold  
**Solution:** Use temperature range

```python
THRESHOLD_HIGH = 28.0  # Fan ON
THRESHOLD_LOW = 26.0   # Fan OFF
```

**Logic:**
```
27.9°C → Fan OFF (no change)
28.0°C → Fan ON
28.5°C → Fan ON (stays on)
27.0°C → Fan ON (stays on)
26.0°C → Fan OFF
25.5°C → Fan OFF (stays off)
```

### 3. Tapo P300 Control Library

**Library:** `python-kasa` (unofficial but actively maintained)

**Why not PyP100?**
- PyP100 less maintained
- python-kasa has better async support
- python-kasa supports Tapo devices via discovery

**Code example:**
```python
import asyncio
from kasa import Discover

async def control_fan(turn_on: bool):
    dev = await Discover.discover_single(
        "192.168.1.XXX",  # Tapo P300 IP
        username="user@example.com",
        password="password"
    )
    await dev.update()
    fan_plug = dev.children[0]  # First socket
    
    if turn_on:
        await fan_plug.turn_on()
    else:
        await fan_plug.turn_off()

asyncio.run(control_fan(True))
```

**Environment variables:**
- Store credentials in Secret Manager
- Never hardcode in code

### 4. Error Handling Priority

**Must handle:**
1. WiFi disconnection (ESP32 side)
2. HTTP request failure (ESP32 side)
3. Tapo connection failure (Cloud Functions side)
4. BigQuery insert failure (Cloud Functions side)

**Strategy:**
- ESP32: Retry 3 times with exponential backoff
- Cloud Functions: Log error, send alert, but don't crash
- Monitoring: Alert if >5% failure rate

### 5. MicroPython Memory Constraints

**ESP32 has limited RAM:**
- Keep imports minimal
- Reuse variables
- Use `gc.collect()` if needed

**Good practices:**
```python
# ✓ Good: Import only what you need
from machine import Pin
import onewire

# ✗ Bad: Import everything
import machine  # Wastes memory
```

---

## 🧪 Testing Strategy

### Unit Testing (Per Component)

1. **DS18B20 sensor**
   ```python
   # Test: Read temperature 10 times
   # Expected: Values between 20-30°C, stable (±1°C)
   ```

2. **WiFi connection**
   ```python
   # Test: Connect to WiFi, check IP assigned
   # Expected: IP address displayed, ping google.com succeeds
   ```

3. **HTTP POST**
   ```python
   # Test: POST to ingest endpoint
   # Expected: HTTP 200 response, data in BigQuery
   ```

4. **Tapo control**
   ```python
   # Test: Turn fan ON, check status, turn OFF
   # Expected: Fan audibly starts/stops, plug state reflects
   ```

5. **Thermostat logic**
   ```python
   # Test: Insert 28°C data, wait 60s, check fan
   # Expected: Fan turns ON, event in control_events
   ```

### Integration Testing (Full System)

1. **Normal operation**
   - Let system run for 6 hours
   - Verify data every 60s in BigQuery
   - Check Grafana updates correctly

2. **Threshold crossing**
   - Heat water to 28°C (or insert test data)
   - Verify fan turns ON within 60s
   - Check LINE notification received
   - Cool water to 26°C
   - Verify fan turns OFF within 60s

3. **Error scenarios**
   - Disconnect WiFi → ESP32 should reconnect
   - Unplug Tapo → Cloud Function should log error and alert
   - Stop Cloud Function → Data should queue (eventually consistent)

### Long-term Testing (3-5 days)

**Before leaving for Obon:**
- Run system continuously for 3-5 days
- Check daily for errors
- Verify no memory leaks (ESP32 uptime)
- Confirm fan cycles correctly
- Monitor BigQuery costs (should be <$1)

---

## 🔧 Development Environment

### Local Setup

**Required:**
- Python 3.9+ (for GCP CLI and testing)
- gcloud CLI (for deployment)
- esptool.py (for ESP32 flashing)
- USB cable (for ESP32 connection)

**Optional but recommended:**
- VS Code with Pymakr extension (for MicroPython development)
- Jupyter notebook (for BigQuery query testing)

### File Structure

```
aquapulse/
├── esp32/
│   ├── main.py              # ESP32 main code (auto-runs on boot)
│   ├── boot.py              # ESP32 boot configuration
│   └── config.py            # WiFi credentials, endpoint URL
├── cloud-functions/
│   ├── ingest/
│   │   ├── main.py          # HTTP endpoint for sensor data
│   │   └── requirements.txt # google-cloud-bigquery
│   └── thermostat/
│       ├── main.py          # Scheduled thermostat logic
│       └── requirements.txt # google-cloud-bigquery, python-kasa
├── docs/
│   ├── guides/
│   │   ├── aquarium-thermostat-complete-manual.md  # PRIMARY REFERENCE
│   │   └── implementation-kickoff-2026-08.md       # THIS FILE
│   ├── reference/
│   │   └── schema.md        # BigQuery schema
│   └── decisions/
│       └── 0006-simplified-schema-design.md
└── BACKLOG.md
```

### Secrets Management

**Never commit:**
- WiFi password
- GCP credentials
- Tapo username/password
- LINE notification tokens

**How to store:**
1. **ESP32:** `config.py` (add to `.gitignore`)
2. **Cloud Functions:** Secret Manager
3. **Local testing:** Environment variables

---

## 🚦 Getting Started (Next Steps)

### For Local Agent

You are now responsible for implementing Phase 1. Here's your immediate action plan:

1. **Read the primary reference:**
   ```
   docs/guides/aquarium-thermostat-complete-manual.md
   ```
   - Focus on sections A1-A5, B1-B6, C1-C4
   - Code examples are copy-paste ready
   - Troubleshooting sections cover common errors

2. **Choose your starting track:**
   - **Option A:** Start with Cloud (B1-B6) if hardware not ready
   - **Option B:** Start with Hardware (A1-A5) if you have ESP32 + sensor
   - **Option C:** Do both in parallel (recommended for speed)

3. **Create implementation branch:**
   ```bash
   git checkout -b cursor/thermostat-implementation-0d1c
   ```

4. **Follow the manual step-by-step:**
   - Each section has prerequisites, commands, expected output
   - Copy code directly from manual
   - Run verification commands after each step

5. **Ask Cloud Agent (me) for help when:**
   - Schema design questions
   - Architecture decisions
   - GCP-specific issues
   - Troubleshooting errors not covered in manual

6. **Test frequently:**
   - Don't wait until end to test
   - Verify each component works before integration
   - Use manual's test data for isolated testing

### For User

**Your role:**
1. **Provide hardware:** ESP32, DS18B20 sensor, breadboard, wires
2. **Provide credentials:** WiFi, GCP project, Tapo account
3. **Test physically:** Plug in ESP32, verify fan turns on/off
4. **Monitor:** Check Grafana, respond to LINE notifications

**Coordinate with Local Agent:**
- Give clear instructions using the manual as reference
- Example: "Implement section B3 (ingest Cloud Function)"
- Ask questions to Cloud Agent (me) for design/architecture

### For Cloud Agent (Me)

**My role:**
1. **Answer questions:** Design, architecture, troubleshooting
2. **Review code:** If requested
3. **Update docs:** If gaps found during implementation
4. **Support:** Help debug issues not in manual

**I'm available concurrently** while Local Agent implements.

---

## 📞 Escalation Path

If you get stuck:

1. **Check manual first:** `aquarium-thermostat-complete-manual.md` has extensive troubleshooting
2. **Check schema:** `docs/reference/schema.md` for data structure questions
3. **Check ADR:** `docs/decisions/0006-simplified-schema-design.md` for design rationale
4. **Ask Cloud Agent:** For questions about "why" or architectural decisions
5. **Check GitHub issues:** Past PRs (#55-59) might have context

---

## ✅ Pre-Departure Checklist

Before leaving for Obon (2026-08-08):

### Functional Requirements
- [ ] ESP32 sends temperature every 60s
- [ ] Data appears in BigQuery within 2 minutes
- [ ] Grafana shows live temperature
- [ ] Fan turns ON at 28°C automatically
- [ ] Fan turns OFF at 26°C automatically
- [ ] LINE notification on fan state change
- [ ] System runs continuously for 3+ days without restart

### Non-Functional Requirements
- [ ] ESP32 uptime > 99% (max 1 restart per day acceptable)
- [ ] Data loss < 1% (max 14 missing readings per day)
- [ ] Fan control latency < 2 minutes (from threshold to action)
- [ ] No manual intervention needed

### Safety Checks
- [ ] Alert configured for 30°C (emergency threshold)
- [ ] Fan power cable secure (won't unplug)
- [ ] ESP32 power cable secure
- [ ] Tapo P300 firmware up to date
- [ ] Backup plan documented (if system fails, who to call?)

### Documentation
- [ ] WiFi credentials backed up (in case ESP32 reset needed)
- [ ] Tapo credentials backed up
- [ ] GCP project ID and region documented
- [ ] Emergency contact has access to Grafana

---

## 📊 Success Metrics

**After 1 week of absence:**

| Metric | Target | Acceptable | Failure |
|--------|--------|------------|---------|
| Fish survival | 100% | 100% | <100% |
| System uptime | >99% | >95% | <95% |
| Data completeness | >99% | >95% | <95% |
| Fan cycles | 5-10 times | 3-15 times | >20 or 0 |
| Max water temp | <29°C | <30°C | ≥30°C |
| Manual interventions | 0 | 0 | >0 |

---

## 🎓 Learning Resources

If you're unfamiliar with a technology:

**ESP32 + MicroPython:**
- Official docs: https://docs.micropython.org/en/latest/esp32/quickref.html
- DS18B20 example: https://docs.micropython.org/en/latest/esp8266/tutorial/onewire.html

**Google Cloud Functions:**
- Quickstart: https://cloud.google.com/functions/docs/create-deploy-http-python
- Best practices: https://cloud.google.com/functions/docs/bestpractices/tips

**BigQuery:**
- Schema design: https://cloud.google.com/bigquery/docs/schemas
- Partitioning: https://cloud.google.com/bigquery/docs/partitioned-tables

**Grafana + BigQuery:**
- Plugin docs: https://grafana.com/grafana/plugins/doitintl-bigquery-datasource/

**python-kasa (Tapo control):**
- GitHub: https://github.com/python-kasa/python-kasa
- Tapo support: https://python-kasa.readthedocs.io/en/latest/tapo.html

---

## 🏁 Final Notes

**This is a life-critical system.** The fish depend on it. Prioritize:
1. **Reliability** over features
2. **Testing** over speed
3. **Simplicity** over elegance

**You have 1 week.** That's enough time if you:
- Follow the manual closely
- Test each component before integrating
- Ask for help when stuck (don't waste time debugging alone)

**The manual is your friend.** It's 4187 lines because it covers everything:
- Every command with expected output
- Every error with solution
- Every test with verification steps

**You've got this.** The design is finalized, the docs are ready, the path is clear. Execute step-by-step and the fish will be safe.

---

**Ready? Let's save some fish! 🐠**

---

## Appendix: Quick Command Reference

### ESP32 Flash MicroPython
```bash
esptool.py --chip esp32 erase_flash
esptool.py --chip esp32 write_flash -z 0x1000 esp32-20220618-v1.19.1.bin
```

### Deploy Cloud Function (ingest)
```bash
gcloud functions deploy ingest \
  --runtime python39 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point ingest \
  --source ./cloud-functions/ingest \
  --region us-central1
```

### Deploy Cloud Function (thermostat)
```bash
gcloud functions deploy thermostat \
  --runtime python39 \
  --trigger-topic thermostat-trigger \
  --entry-point thermostat \
  --source ./cloud-functions/thermostat \
  --region us-central1 \
  --set-env-vars TAPO_IP=192.168.1.XXX \
  --set-secrets TAPO_USERNAME=tapo-user:latest,TAPO_PASSWORD=tapo-pass:latest
```

### Create BigQuery Tables
```sql
-- sensor_readings
CREATE TABLE aquapulse.sensor_readings (
  timestamp TIMESTAMP,
  sensor_id STRING,
  sensor_type STRING,
  location STRING,
  value FLOAT64,
  unit STRING,
  device_id STRING,
  firmware_version STRING
)
PARTITION BY DATE(timestamp);

-- control_events
CREATE TABLE aquapulse.control_events (
  event_id STRING,
  timestamp TIMESTAMP,
  event_type STRING,
  device_id STRING,
  action STRING,
  action_details JSON,
  trigger_type STRING,
  trigger_value FLOAT64,
  trigger_threshold FLOAT64,
  success BOOLEAN,
  error_message STRING,
  execution_duration_ms INT64
)
PARTITION BY DATE(timestamp);
```

### Test Tapo Control (Local)
```python
import asyncio
from kasa import Discover

async def test_tapo():
    dev = await Discover.discover_single(
        "192.168.1.XXX",
        username="user@example.com",
        password="password"
    )
    await dev.update()
    print(f"Device: {dev.alias}")
    print(f"Children: {len(dev.children)}")
    fan = dev.children[0]
    print(f"Fan is: {'ON' if fan.is_on else 'OFF'}")

asyncio.run(test_tapo())
```

### Query Latest Temperature (BigQuery)
```sql
SELECT 
  timestamp,
  sensor_id,
  value,
  unit
FROM aquapulse.sensor_readings
WHERE sensor_type = 'temperature'
  AND location = 'aquarium'
ORDER BY timestamp DESC
LIMIT 1;
```

---

**Document Version:** 1.0  
**Last Updated:** 2026-08-01  
**Next Review:** After Phase 1 completion (2026-08-08)
