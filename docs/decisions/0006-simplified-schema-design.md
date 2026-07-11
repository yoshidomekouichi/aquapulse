# ADR-0006: Simplified Schema Design for BigQuery Tables

## Status

Approved

## Context

The aquarium monitoring system needs to store two distinct types of data:

1. **Observed sensor readings**: Temperature, TDS, pH, room climate (continuous, high-frequency)
2. **Control/intervention events**: Fan control, water changes, fertilizer additions (discrete, low-frequency)

Initial schema design attempted to store both in a single table, but analysis revealed significant differences:

- **Data volume**: Sensor readings are 1000-10000x more frequent than interventions
- **Retention policy**: Observations may need archival, interventions require long-term storage
- **Query patterns**: Different analysis needs (time-series vs. causal inference)
- **Storage costs**: Different optimization strategies needed

Additionally, the user requested support for manual intervention recording (water changes, fertilizer additions) to enable future causal inference analysis alongside automated fan control.

## Alternatives Considered

### Alternative A: Single Extended Table

Store all data in one `sensor_readings` table with additional fields for interventions.

- **Pros**:
  - Simple schema
  - Single query for all data
  - No JOIN required for basic analysis

- **Cons**:
  - 99%+ of rows have null intervention fields (storage waste)
  - Difficult to optimize storage for different data types
  - Mixing observations and interventions complicates causal analysis
  - Cannot apply different retention policies
  - High long-term storage costs

### Alternative B: Separate Tables with `pre_measurement` and `post_measurement`

Create `control_events` table with fields to directly store pre- and post-intervention sensor values.

- **Pros**:
  - Explicit causal relationship in schema
  - No JOIN needed for basic impact analysis

- **Cons**:
  - "Post-measurement" is ambiguous (1 min? 10 min? 1 hour after?)
  - Temperature changes are gradual, not instantaneous
  - Redundant storage (values already in `sensor_readings`)
  - Inflexible for different analysis windows
  - Complex implementation in Cloud Functions

### Alternative C: Separate Tables with JOIN-Based Analysis (Adopted)

Create separate `sensor_readings` and `control_events` tables. Store trigger context in `control_events`, perform temporal JOINs for analysis.

- **Pros**:
  - Clean separation of observations vs. interventions
  - Flexible analysis windows (JOIN with any time offset)
  - No redundant data storage
  - Can apply different storage tiers independently
  - Simple implementation (Cloud Functions only records event metadata)
  - Optimizes for long-term storage costs

- **Cons**:
  - Requires SQL JOINs for causal analysis
  - Slightly more complex queries

## Decision

Adopt **Alternative C**: Separate tables with JOIN-based analysis.

### Schema Design

#### Table 1: `sensor_readings`

Stores all observed sensor data (temperature, TDS, pH, room climate).

**Phase 1 Fields:**
- `timestamp` (TIMESTAMP, REQUIRED)
- `sensor_id` (STRING, REQUIRED)
- `sensor_type` (STRING, REQUIRED): 'temperature', 'tds', 'ph', 'room_temperature', 'room_humidity'
- `location` (STRING, REQUIRED): 'aquarium', 'room'
- `value` (FLOAT, REQUIRED)
- `unit` (STRING, REQUIRED): 'celsius', 'ppm', 'pH', 'percent'
- `device_id` (STRING, REQUIRED): ESP32 or Tapo device ID
- `firmware_version` (STRING, NULLABLE)

**Phase 2 (Deferred):**
- `quality_score` (FLOAT, NULLABLE)
- `is_anomaly` (BOOLEAN, NULLABLE)

#### Table 2: `control_events`

Stores all control actions and manual interventions.

**Phase 1 Fields:**
- `event_id` (STRING, REQUIRED): UUID
- `timestamp` (TIMESTAMP, REQUIRED)
- `event_type` (STRING, REQUIRED): 'automated_thermostat', 'manual_maintenance', 'manual_dosing'
- `device_id` (STRING, NULLABLE): Device executing action (NULL for manual)
- `action` (STRING, REQUIRED): 'fan_on', 'fan_off', 'water_change', 'fertilizer_add', etc.
- `action_details` (JSON, NULLABLE): Additional metadata (volume, product name, notes)
- `trigger_type` (STRING, NULLABLE): 'threshold_exceeded', 'manual', 'scheduled'
- `trigger_sensor_id` (STRING, NULLABLE): Sensor that triggered action
- `trigger_value` (FLOAT, NULLABLE): Sensor value at trigger time (pre-intervention context)
- `trigger_threshold` (FLOAT, NULLABLE): Threshold that was exceeded
- `success` (BOOLEAN, REQUIRED): Action succeeded
- `error_message` (STRING, NULLABLE)
- `duration_ms` (INTEGER, NULLABLE): Action execution time

**Key Design Choices:**

1. **No `pre_measurement` or `post_measurement` fields**: Use `trigger_value` for pre-intervention context. For post-intervention analysis, JOIN with `sensor_readings` at desired time offsets.

2. **`action_details` as JSON**: Flexible schema for different intervention types:
   - Fan control: `{"hysteresis_upper": 27.0}`
   - Water change: `{"volume_liters": 5.0, "notes": "Weekly maintenance"}`
   - Fertilizer: `{"product": "Hyponex", "volume_ml": 10}`

3. **Support for manual interventions**: `event_type` distinguishes automated vs. manual events. Manual events recorded via Google Forms (see ADR-0007).

### Storage Strategy

- **BigQuery Active Storage**: Recent data (default 90 days)
- **BigQuery Long-term Storage**: Older data (automatic after 90 days, 50% cheaper)
- **Cloud Storage Archive** (Phase 2): Very old data (years), queryable via Federated Queries

## Consequences

### Positive

- **Cost-efficient**: Separate tables enable independent storage optimization
- **Flexible analysis**: JOIN-based approach supports any time window for causal analysis
- **Scalable**: Schema supports both automated and manual interventions
- **Simple implementation**: Cloud Functions only record event metadata, no complex pre/post measurement logic
- **Future-proof**: Easy to add new intervention types via `action_details` JSON

### Negative

- **Query complexity**: Causal analysis requires temporal JOINs
- **Learning curve**: Users must understand JOIN syntax for advanced analysis

### Risks

- **JOIN performance**: Large-scale temporal JOINs may be expensive
  - **Mitigation**: Partition tables by date, use materialized views for common queries
- **Manual data entry errors**: Google Forms may have input mistakes
  - **Mitigation**: Input validation in Apps Script, regular data quality checks

## Related Materials

- [Schema Reference](../reference/schema.md)
- [Architecture Snapshot: 2026-07-11 Schema Finalization](../architecture/snapshots/2026-07-11-schema-finalization.md)
- [How-to: Record Manual Events with Google Forms](../how-to/record-manual-events-forms.md)
- [Implementation Guide: Aquarium Thermostat Complete Manual](../guides/aquarium-thermostat-complete-manual.md)
