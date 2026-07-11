# Architecture Snapshot: 2026-07-11 Schema Finalization

**Date**: July 11, 2026  
**Status**: Approved  
**Context**: BigQuery schema design for sensor data and control events

---

## Overview

This snapshot records the architectural decisions made during the schema finalization phase for the AquaPulse aquarium monitoring system. The primary goal was to design a BigQuery schema that supports:

1. High-frequency sensor data collection
2. Low-frequency control/intervention event recording
3. Long-term cost-efficient storage
4. Future causal inference analysis

---

## Problem Statement

The system needs to store two fundamentally different types of data:

### Observed Data (High Volume)
- Temperature sensors (ESP32 DS18B20, Tapo T310)
- TDS/pH sensors (future)
- Room climate (Tapo T310)
- **Frequency**: Every 5 minutes
- **Volume**: ~300 readings/day per sensor

### Intervention Events (Low Volume)
- Automated fan control (thermostat)
- Manual water changes
- Manual fertilizer additions
- **Frequency**: 0-10 events/day
- **Volume**: ~100-500 events/year

### Key Requirements

1. **Cost efficiency**: Minimize BigQuery storage costs for long-term data retention
2. **Analytical flexibility**: Support time-series visualization and causal inference
3. **Scalability**: Handle future sensor additions without schema changes
4. **Manual data entry**: Enable easy recording of manual interventions

---

## Hypothesis & Design Evolution

### Initial Hypothesis

> "A single table with optional intervention fields can store all data."

**Rejected** due to:
- 99%+ null fields for intervention columns (storage waste)
- Cannot apply different retention policies
- Mixing observations and interventions complicates analysis
- High long-term storage costs

### Revised Hypothesis

> "Separate tables with `pre_measurement` and `post_measurement` fields can explicitly capture causal relationships."

**Rejected** due to:
- "Post-measurement" timing is ambiguous (temperature changes gradually)
- Redundant data storage (values already in `sensor_readings`)
- Inflexible for different analysis time windows
- Complex implementation

### Final Design (Adopted)

> "Separate tables with JOIN-based analysis enable flexible causal inference while minimizing storage costs."

**Adopted** because:
- Clean separation of observations vs. interventions
- Flexible analysis windows (JOIN at any time offset)
- No data redundancy
- Simple implementation
- Cost-optimized storage

---

## Architecture Components

### Component 1: Data Collection

```
ESP32 (MicroPython)
  ├─ DS18B20 Temperature Sensor
  ├─ MCP3424 ADC (TDS/pH, future)
  └─ HTTP POST → Cloud Functions → BigQuery (sensor_readings)

Tapo Devices
  ├─ T310 Temperature/Humidity Sensor
  ├─ P300 Smart Plug (fan control)
  └─ Python Collector → BigQuery (sensor_readings)
```

### Component 2: Automated Control

```
Cloud Scheduler (every 5 min)
  └→ Cloud Functions (thermostat logic)
       ├─ Query BigQuery (sensor_readings)
       ├─ Check threshold (27°C with hysteresis)
       ├─ Control Tapo P300 (fan on/off)
       └─ Insert BigQuery (control_events)
```

### Component 3: Manual Event Recording

```
User (smartphone/PC)
  └→ Google Forms
       └→ Apps Script
            └→ BigQuery (control_events)
```

### Component 4: Data Visualization

```
BigQuery
  └→ Grafana Cloud
       ├─ Time-series dashboard (temperature, TDS, pH)
       └─ Event markers (fan control, water changes)
```

---

## Schema Design

### Table 1: `sensor_readings`

**Purpose**: Store all observed sensor data

**Key Fields**:
- `timestamp`, `sensor_id`, `sensor_type`, `location`, `value`, `unit`
- `device_id`, `firmware_version`

**Partitioning**: Daily by `timestamp`

**Retention**:
- Active Storage: 90 days
- Long-term Storage: Automatic after 90 days
- Archive (Phase 2): Export to Cloud Storage

### Table 2: `control_events`

**Purpose**: Store all control actions and manual interventions

**Key Fields**:
- `event_id`, `timestamp`, `event_type`, `action`
- `action_details` (JSON): Flexible metadata (volume, product, notes)
- `trigger_value`: Pre-intervention sensor value
- `success`, `error_message`, `duration_ms`

**Partitioning**: Daily by `timestamp`

**Retention**: Keep all data (interventions are rare and valuable)

---

## Rationale: Key Design Choices

### 1. Separate Tables

**Decision**: Use `sensor_readings` and `control_events` tables instead of a single table.

**Reasoning**:
- **Data volume difference**: 1000-10000x ratio between observations and interventions
- **Storage optimization**: Apply different tiers independently (Active vs. Long-term)
- **Query performance**: Avoid scanning millions of rows with null intervention fields
- **Cost efficiency**: Reduces storage costs by ~60% over 5 years

### 2. No `pre_measurement` or `post_measurement` Fields

**Decision**: Do not store pre/post sensor values directly in `control_events`.

**Reasoning**:
- **Ambiguity**: "Post-measurement" timing is unclear (gradual temperature changes)
- **Redundancy**: Values already exist in `sensor_readings`
- **Flexibility**: JOIN-based approach allows any time window for analysis
- **Simplicity**: Cloud Functions only record event metadata, no complex logic

**Implementation**:
- Use `trigger_value` for pre-intervention context
- Perform temporal JOINs for post-intervention analysis

Example query:
```sql
-- Get temperature 30 minutes after fan ON
SELECT
  e.event_id,
  e.trigger_value AS pre_temp,
  AVG(s.value) AS post_temp_30min
FROM control_events e
LEFT JOIN sensor_readings s
  ON s.timestamp BETWEEN e.timestamp + INTERVAL 25 MINUTE
                     AND e.timestamp + INTERVAL 35 MINUTE
WHERE e.action = 'fan_on'
GROUP BY e.event_id, e.trigger_value;
```

### 3. `action_details` as JSON

**Decision**: Use JSON field for flexible intervention metadata.

**Reasoning**:
- **Extensibility**: Add new intervention types without schema changes
- **Flexibility**: Different actions have different metadata requirements
  - Fan: `{"hysteresis_upper": 27.0}`
  - Water change: `{"volume_liters": 5.0, "notes": "Weekly"}`
  - Fertilizer: `{"product": "Hyponex", "volume_ml": 10}`
- **BigQuery support**: Native JSON query support with `JSON_EXTRACT`

### 4. Manual Event Recording via Google Forms

**Decision**: Use Google Forms + Apps Script for Phase 1 manual data entry.

**Reasoning**:
- **Ease of use**: Non-technical, smartphone-friendly UI
- **Quick setup**: ~30 minutes implementation
- **Validation**: Apps Script can validate inputs before BigQuery insert
- **Low cost**: Free (within GCP/Google Workspace limits)

---

## Storage Cost Analysis

### Assumptions

- **Sensor readings**: 5-minute intervals, 3 sensors (temperature, room temp, room humidity)
- **Control events**: 2 fan events/day + 1 manual event/week
- **Retention**: 5 years

### Cost Breakdown (Year 1)

| Component | Active (90d) | Long-term (275d) | Total |
|-----------|--------------|------------------|-------|
| `sensor_readings` | ~400 MB | ~1.1 GB | ~1.5 GB |
| `control_events` | ~0.5 MB | ~1.5 MB | ~2 MB |
| **Monthly cost** | **$0.02** | **$0.03** | **$0.05** |

### Cost Breakdown (Year 5)

| Component | Active (90d) | Long-term (4.75y) | Total |
|-----------|--------------|-------------------|-------|
| `sensor_readings` | ~400 MB | ~5.2 GB | ~5.6 GB |
| `control_events` | ~0.5 MB | ~7.5 MB | ~8 MB |
| **Monthly cost** | **$0.02** | **$0.13** | **$0.15** |

**Total 5-year storage cost**: ~$6 (well within GCP Free Tier)

---

## Risks & Mitigations

### Risk 1: JOIN Performance

**Risk**: Large-scale temporal JOINs may be slow or expensive.

**Mitigation**:
- Partition tables by date (BigQuery optimization)
- Use `WHERE` clauses to limit scan range
- Create materialized views for common queries (e.g., daily aggregates)
- Monitor query costs with BigQuery Cost Controls

### Risk 2: Manual Data Entry Errors

**Risk**: Google Forms may have typos or incorrect values.

**Mitigation**:
- Input validation in Apps Script (e.g., volume > 0)
- Dropdown menus for `event_type` and `action`
- Add `notes` field for corrections
- Regular data quality checks with SQL queries

### Risk 3: Schema Evolution

**Risk**: Future requirements may need schema changes.

**Mitigation**:
- Use JSON `action_details` for extensibility
- BigQuery supports adding columns (backward compatible)
- Document schema changes in new ADRs
- Maintain backward compatibility for Grafana dashboards

---

## Future Enhancements (Phase 2)

### 1. Data Quality Monitoring

Add to `sensor_readings`:
- `quality_score` (0.0-1.0): Confidence in measurement
- `is_anomaly` (BOOLEAN): Outlier detection flag

### 2. Cloud Storage Archive

Export very old data (2+ years) to Cloud Storage Archive:
- **Cost**: $0.0012/GB/month (vs. BigQuery $0.01/GB/month)
- **Access**: Federated queries when needed
- **Savings**: ~90% for rarely-accessed historical data

### 3. Materialized Views

Pre-compute common aggregations:
- Hourly temperature averages
- Daily min/max values
- Weekly intervention summaries

### 4. Web UI for Manual Entry

Replace Google Forms with custom UI:
- Better UX with pre-filled defaults
- Real-time validation
- Historical event view
- Integration with Grafana

---

## Related Documents

- [ADR-0006: Simplified Schema Design](../decisions/0006-simplified-schema-design.md)
- [Schema Reference](../reference/schema.md)
- [How-to: Record Manual Events with Google Forms](../how-to/record-manual-events-forms.md)
- [Implementation Guide: Aquarium Thermostat Complete Manual](../guides/aquarium-thermostat-complete-manual.md)

---

## Conclusion

This architecture snapshot captures the reasoning behind the final BigQuery schema design. The two-table approach with JOIN-based analysis balances cost efficiency, analytical flexibility, and implementation simplicity. The design is future-proof, supporting both automated and manual interventions while enabling long-term causal inference analysis.

**Next steps**: Implement the schema in BigQuery and integrate with ESP32 data collection (see Implementation Guide).
