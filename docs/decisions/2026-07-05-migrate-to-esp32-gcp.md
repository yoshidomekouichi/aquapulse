# ADR-0001: Migration from Raspberry Pi to ESP32+GCP

## Status

Approved (2026-07-05)

## Context

The AquaPulse project initially ran on Raspberry Pi using Docker Compose (TimescaleDB, Grafana). However, the following problems occurred:

- **Unstable SSH connection**: Connection impossible even with fixed IP and Tailscale
- **Difficult recovery**: Headless configuration means no SSH = completely inaccessible
- **Physical constraints**: Sensors fixed to aquarium, cannot develop Raspberry Pi at desk
- **Network dependency**: Daily operation depends on IP address

Raspberry Pi became "dead" (no SSH, unrecoverable). Considering migration to new architecture.

## Alternatives Considered

### 1. Repair/Re-setup Raspberry Pi

- pros: Can reuse existing code
- cons: Same SSH problem may recur, not fundamental solution

### 2. Use Intermediate Device like DFRobot

- pros: Raspberry Pi operable at desk
- cons: Raspberry Pi ↔ DFRobot communication IP-dependent, adds one more layer of problems

### 3. ESP32 + GCP Cloud-Native Architecture (Adopted)

- pros:
  - No SSH needed (only USB connection for initial setup)
  - No IP address dependency (daily operation)
  - Handles physical constraint of fixed sensors
  - Cloud-native with high scalability
- cons:
  - Complete rewrite of existing code
  - GCP costs (estimated $5-10/month)
  - Learning curve for new tech stack

## Decision

Adopt **ESP32 + GCP Cloud-Native Architecture**

Tech stack:
- **Hardware**: ESP32 (MicroPython)
- **Sensors**: DS18B20 (temperature), Tapo T310/P300
- **Cloud**: GCP (Pub/Sub, Cloud Functions, BigQuery, Cloud Scheduler)
- **Visualization**: Grafana Cloud
- **IaC**: Terraform
- **CI/CD**: GitHub Actions

## Consequences

### Positive
- Complete liberation from SSH problems
- Operable with only power ON/OFF
- Safe power-off (no script stop needed)
- Cloud-native benefits (scalability, availability)

### Negative
- Archiving existing code (Python, Docker Compose)
- GCP costs (previously: $0 → new: $5-10/month)
- Learning cost for MicroPython, GCP

### Risks
- ESP32 rewrite requires physical connection (USB cable ≥ 2m needed)
- Mock testing limitations (sensor reading requires real hardware)
- Trial-and-error in initial development (expect 3-5 rewrites)

## Related Materials

- [docs/cloud-migration/](../cloud-migration/) (Full migration guide)
- [docs/cloud-migration/00_OVERVIEW.md](../cloud-migration/00_OVERVIEW.md) (System overview)
- [docs/cloud-migration/01_HARDWARE_SETUP.md](../cloud-migration/01_HARDWARE_SETUP.md) (ESP32 operation model)
- [ADR-0002](2026-07-05-archive-directory-structure.md) (Archiving existing code)
