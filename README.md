# AquaPulse 🌊

**Freshwater Aquarium IoT: Data Collection, Visualization & Causal Inference**

[日本語版はこちら](README.ja.md)

## What's this?

**Goal**: Keep fish healthy and plants thriving by maintaining optimal water conditions — using data, not guesswork.

Collecting environmental data (water temp, room temp, humidity, lighting) and applying causal inference to understand what actually affects water quality and when to intervene.

**Risk Management** (minimize volatility) / **Cost Optimization** (reduce maintenance effort) / **SLA Improvement** (anomaly detection & rapid response)

### Dashboard Views

| PC (Full Analytics) | 7" Touch Display (At-a-Glance) |
|:-------------------:|:------------------------------:|
| ![PC Dashboard](docs/images/dashboard-pc.png) | ![Display Dashboard](docs/images/dashboard-display.png) |

## Current Status

> ⚠️ **Architecture Transition in Progress**
> 
> The project is migrating from Raspberry Pi to **ESP32 + GCP** cloud-native architecture to solve persistent IP address and physical access issues. See: [Why Cloud Migration](docs/explanation/why-cloud-migration.md)

### Legacy System (Raspberry Pi)

| Feature | Status | Notes |
|---------|--------|-------|
| Sensor Data Collection | 🔴 Stopped | Raspberry Pi SSH inaccessible |
| TimescaleDB Storage | 🔴 Inaccessible | Data cannot be retrieved |
| Grafana Dashboard | 🔴 Offline | No access to Raspberry Pi |
| Event Logging | ⚠️ Interim | Using Grafana Annotations |
| Causal Inference Model | 🔜 Planned | After sufficient data accumulation |

### New System (ESP32 + GCP)

| Feature | Status | Notes |
|---------|--------|-------|
| ESP32 Hardware | 🔜 Planned | Purchasing ESP32-DevKitC |
| Sensor Data Collection | 🔧 In Progress | DS18B20, MCP3424 (reuse from RPi) |
| GCP Pub/Sub | 🔜 Planned | Message buffering |
| Cloud Functions | 🔜 Planned | Data ingestion |
| BigQuery Storage | 🔜 Planned | Time-series data warehouse |
| Grafana Cloud | 🔜 Planned | Visualization |

---

## Roadmap

| Phase | Description | Status |
|-------|-------------|--------|
| **1** | Sensor data collection & visualization | ✅ Done |
| **2** | Intervention events (feeding, water changes, etc.) | ⚠️ Interim solution |
| **3** | Causal inference model (training on PC) | Not started |
| **4** | Edge inference (real-time prediction on Raspberry Pi) | Not started |

> **Why not use "fish death" as KGI?** Data is sparse and confounding factors are numerous. Instead, we use proxy KGIs: water temperature volatility, water change intervals, time in abnormal state. → [Details](docs/design/metrics.md)

---

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Sensors   │────▶│ TimescaleDB │────▶│   Grafana   │
│ (Tapo/GPIO) │     │   (Raw)     │     │  (Display)  │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                    ┌──────▼──────┐
                    │  Features   │  ← Continuous Aggregates
                    │ (1min/5min) │
                    └──────┬──────┘
                           │
              ┌────────────▼────────────┐
              │    ML Training (PC)     │
              │  - Point-in-Time JOIN   │
              │  - Causal Inference     │
              └────────────┬────────────┘
                           │
                    ┌──────▼──────┐
                    │ Edge Infer  │  ← Future
                    │ (Raspberry) │
                    └─────────────┘
```

**Design Principles**:
- **Async collection (Raw)** → Independent intervals per sensor constraints
- **Feature generation in TimescaleDB** → Continuous Aggregates, gapfill
- **Train on PC, infer on edge** → Proper separation of compute resources
- **Point-in-Time Correctness** → Prevent future data leakage

> Details: [docs/design/architecture.md](docs/design/architecture.md)

---

## Tech Stack

### Legacy (Raspberry Pi) - Deprecated

| Component | Technology |
|-----------|------------|
| Device | Raspberry Pi 5 (8GB) + NVMe SSD |
| Display | Pi Touch Display 1 (800x480) |
| OS | Raspberry Pi OS Lite (Bookworm, 64-bit) |
| Language | Python 3.11+ |
| Database | TimescaleDB (PostgreSQL) |
| Visualization | Grafana (kiosk mode: cage + Chromium) |
| Infrastructure | Docker / Docker Compose |

### New (ESP32 + GCP) - In Progress

| Component | Technology |
|-----------|------------|
| Hardware | ESP32-DevKitC (16MB flash) |
| Firmware | MicroPython |
| Messaging | GCP Pub/Sub |
| Compute | Cloud Functions (Python 3.11) |
| Database | BigQuery |
| Visualization | Grafana Cloud |
| Infrastructure | Terraform |
| CI/CD | GitHub Actions |

---

## Data Sources

### Sensors (Polling)

| Sensor | Status | Source | Interval |
|--------|--------|--------|----------|
| DS18B20 Water Temp | ✅ | `gpio_temp` | 60s |
| Tapo T310 Temp/Humidity | ✅ | `tapo_sensors` | 300s |
| Tapo P300 Lighting State | ✅ | `tapo_lighting` | 300s |
| TDS Sensor | ⚠️ Manual | `gpio_tds` | On-demand |
| pH Sensor | 🔜 | - | - |

### Events (Planned)

| Event | Recording Method |
|-------|------------------|
| Feeding | Mobile app |
| Water Change | Mobile app |
| Livestock Add/Death | Mobile app |

---

## Directory Structure

```
aquapulse/
├── esp32/              # ESP32 MicroPython code (NEW)
├── cloud-functions/    # GCP Cloud Functions (NEW)
├── terraform/          # Infrastructure as Code (NEW)
├── collector/          # Legacy: Sensor data collection (RPi)
├── db/                 # Legacy: Database init & migrations (RPi)
├── grafana/            # Legacy: Grafana configuration (RPi)
├── kiosk/              # Legacy: Kiosk mode scripts (RPi)
├── .cursor/rules/      # AI agent development rules
└── docs/
    ├── tutorials/      # Learning-oriented guides
    ├── guides/         # Task-oriented how-tos
    ├── reference/      # Technical specifications
    ├── explanation/    # Conceptual documentation
    ├── decisions/      # Architecture Decision Records (ADRs)
    ├── archive/        # Deprecated/archived documentation
    ├── display/        # Legacy: Display & kiosk setup (RPi)
    ├── hardware/       # Legacy: Wiring & sensors (RPi)
    ├── operations/     # Legacy: Operation logs (RPi)
    └── design/         # Legacy: Architecture & design (RPi)
```

---

## Quick Start

> ⚠️ **Note:** The project is transitioning to ESP32 + GCP architecture. The Raspberry Pi setup below is no longer functional due to SSH connectivity issues.

### Legacy (Raspberry Pi) - Deprecated

```bash
# Start with Docker Compose
cd /projects/aquapulse
docker compose up -d

# Enable kiosk mode (display)
sudo systemctl enable grafana-kiosk
sudo systemctl start grafana-kiosk
```

### New (ESP32 + GCP) - In Progress

Follow the [Getting Started Tutorial](docs/tutorials/getting-started-esp32.md) to:

1. Set up ESP32 hardware
2. Configure GCP project
3. Deploy Cloud Functions
4. View live sensor data in Grafana Cloud

**Estimated setup time:** 2-3 hours

---

## Documentation

Documentation is organized using the [Diátaxis framework](https://diataxis.fr/) to separate content by user intent:

### 📚 Tutorials (Learning-Oriented)

New to ESP32 aquarium monitoring? Start here:

- [Getting Started with ESP32](docs/tutorials/getting-started-esp32.md) - Your first ESP32 sensor project

### 📖 Guides (Task-Oriented)

Step-by-step instructions for specific tasks:

- [Hardware Setup](docs/guides/hardware-setup.md) - ESP32 wiring and sensor connections
- [GCP Setup](docs/guides/gcp-setup.md) - Account creation, project setup, authentication

### 📘 Reference (Information-Oriented)

Technical specifications and API documentation:

- [System Architecture](docs/reference/architecture.md) - Tech stack, data flow, schemas, costs

### 💡 Explanation (Understanding-Oriented)

Conceptual explanations and design decisions:

- [Why Cloud Migration](docs/explanation/why-cloud-migration.md) - Rationale behind ESP32 + GCP architecture

### 🗂️ Architecture Decision Records

Significant architectural decisions and their context:

- [Decision Log](docs/decisions/README.md) - Index of all ADRs
- [ADR-0001](docs/decisions/2026-07-05-migrate-to-esp32-gcp.md) - Migrate to ESP32 + GCP
- [ADR-0002](docs/decisions/2026-07-05-archive-directory-structure.md) - Archive directory structure
- [ADR-0003](docs/decisions/2026-07-05-shell-working-directory.md) - Explicit Shell `working_directory`

### 📦 Legacy Documentation

Raspberry Pi documentation has been archived:

- [Archived Docs](docs/archive/) - Old Japanese documentation (superseded)

---

## License

MIT
