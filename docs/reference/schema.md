# BigQuery Schema Reference

This document defines the schema for AquaPulse BigQuery tables.

## Table of Contents

- [sensor_readings](#sensor_readings)
- [control_events](#control_events)
- [Storage Strategy](#storage-strategy)
- [Query Examples](#query-examples)

---

## sensor_readings

Stores all observed sensor data from ESP32 and Tapo devices.

### Schema

| Field | Type | Mode | Description |
|-------|------|------|-------------|
| `timestamp` | TIMESTAMP | REQUIRED | Measurement timestamp (UTC) |
| `sensor_id` | STRING | REQUIRED | Unique sensor identifier (e.g., 'ds18b20_001', 'tapo_t310_kitchen') |
| `sensor_type` | STRING | REQUIRED | Type of sensor ('temperature', 'tds', 'ph', 'room_temperature', 'room_humidity') |
| `location` | STRING | REQUIRED | Measurement location ('aquarium', 'room') |
| `value` | FLOAT | REQUIRED | Measured value |
| `unit` | STRING | REQUIRED | Unit of measurement ('celsius', 'ppm', 'pH', 'percent') |
| `device_id` | STRING | REQUIRED | Device that collected the reading (e.g., 'esp32_001', 'tapo_t310_abc123') |
| `firmware_version` | STRING | NULLABLE | Firmware/software version |

### Phase 2 Fields (Deferred)

| Field | Type | Mode | Description |
|-------|------|------|-------------|
| `quality_score` | FLOAT | NULLABLE | Data quality score (0.0-1.0) |
| `is_anomaly` | BOOLEAN | NULLABLE | Anomaly detection flag |

### Partitioning

- **Partition field**: `timestamp` (daily partitions)
- **Retention**: 90 days in Active Storage, then Long-term Storage (automatic)

### Example Rows

```json
{
  "timestamp": "2026-07-11T12:00:00Z",
  "sensor_id": "ds18b20_001",
  "sensor_type": "temperature",
  "location": "aquarium",
  "value": 26.5,
  "unit": "celsius",
  "device_id": "esp32_001",
  "firmware_version": "v1.0.0"
}

{
  "timestamp": "2026-07-11T12:00:00Z",
  "sensor_id": "tapo_t310_room",
  "sensor_type": "room_temperature",
  "location": "room",
  "value": 28.2,
  "unit": "celsius",
  "device_id": "tapo_t310_abc123",
  "firmware_version": null
}
```

---

## control_events

Stores all control actions (automated and manual interventions).

### Schema

| Field | Type | Mode | Description |
|-------|------|------|-------------|
| `event_id` | STRING | REQUIRED | Unique event identifier (UUID v4) |
| `timestamp` | TIMESTAMP | REQUIRED | Event occurrence time (UTC) |
| `event_type` | STRING | REQUIRED | Event category ('automated_thermostat', 'manual_maintenance', 'manual_dosing') |
| `device_id` | STRING | NULLABLE | Device executing action (NULL for manual events) |
| `action` | STRING | REQUIRED | Specific action taken (see Action Types below) |
| `action_details` | JSON | NULLABLE | Additional metadata (volume, product, notes) |
| `trigger_type` | STRING | NULLABLE | What triggered the action ('threshold_exceeded', 'manual', 'scheduled') |
| `trigger_sensor_id` | STRING | NULLABLE | Sensor that triggered action (for automated events) |
| `trigger_value` | FLOAT | NULLABLE | Sensor value at trigger time (pre-intervention context) |
| `trigger_threshold` | FLOAT | NULLABLE | Threshold that was exceeded (for automated events) |
| `success` | BOOLEAN | REQUIRED | Whether action succeeded |
| `error_message` | STRING | NULLABLE | Error message if action failed |
| `duration_ms` | INTEGER | NULLABLE | Action execution time in milliseconds |

### Action Types

#### Automated Thermostat

- `event_type`: `'automated_thermostat'`
- `action`: `'fan_on'`, `'fan_off'`
- `action_details` example:
  ```json
  {
    "hysteresis_upper": 27.0,
    "hysteresis_lower": 26.0
  }
  ```

#### Manual Maintenance

- `event_type`: `'manual_maintenance'`
- `action`: `'water_change'`, `'water_addition'`, `'filter_cleaning'`
- `action_details` example:
  ```json
  {
    "volume_removed_liters": 5.0,
    "volume_added_liters": 5.0,
    "notes": "Weekly maintenance"
  }
  ```

#### Manual Dosing

- `event_type`: `'manual_dosing'`
- `action`: `'fertilizer_add'`, `'conditioner_add'`, `'ph_adjuster_add'`
- `action_details` example:
  ```json
  {
    "product_name": "Hyponex Original Liquid",
    "volume_ml": 10,
    "dilution_ratio": "1000x",
    "notes": "Weekly fertilization"
  }
  ```

### Partitioning

- **Partition field**: `timestamp` (daily partitions)
- **Retention**: Keep all data (interventions are rare and valuable for long-term analysis)

### Example Rows

#### Automated Fan ON Event

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-07-11T12:30:00Z",
  "event_type": "automated_thermostat",
  "device_id": "cloud_function_thermostat_v1",
  "action": "fan_on",
  "action_details": {
    "hysteresis_upper": 27.0
  },
  "trigger_type": "threshold_exceeded",
  "trigger_sensor_id": "ds18b20_001",
  "trigger_value": 27.2,
  "trigger_threshold": 27.0,
  "success": true,
  "error_message": null,
  "duration_ms": 1250
}
```

#### Manual Water Change Event

```json
{
  "event_id": "660e8400-e29b-41d4-a716-446655440001",
  "timestamp": "2026-07-11T10:00:00Z",
  "event_type": "manual_maintenance",
  "device_id": null,
  "action": "water_change",
  "action_details": {
    "volume_removed_liters": 5.0,
    "volume_added_liters": 5.0,
    "notes": "Weekly water change"
  },
  "trigger_type": "manual",
  "trigger_sensor_id": null,
  "trigger_value": null,
  "trigger_threshold": null,
  "success": true,
  "error_message": null,
  "duration_ms": null
}
```

#### Manual Fertilizer Addition Event

```json
{
  "event_id": "770e8400-e29b-41d4-a716-446655440002",
  "timestamp": "2026-07-11T10:15:00Z",
  "event_type": "manual_dosing",
  "device_id": null,
  "action": "fertilizer_add",
  "action_details": {
    "product_name": "Hyponex Original Liquid",
    "volume_ml": 10,
    "dilution_ratio": "1000x",
    "target_element": "N-P-K"
  },
  "trigger_type": "manual",
  "trigger_sensor_id": null,
  "trigger_value": null,
  "trigger_threshold": null,
  "success": true,
  "error_message": null,
  "duration_ms": null
}
```

---

## Storage Strategy

### BigQuery Storage Tiers

- **Active Storage** (first 90 days): Full query performance, standard pricing
- **Long-term Storage** (after 90 days): Automatic transition, 50% cheaper storage
- **Cloud Storage Archive** (Phase 2): Export very old data for extreme cost reduction

### Cost Optimization

#### sensor_readings

- **Active**: Recent 90 days (~400 MB for 5-min intervals)
- **Long-term**: Older data (~5 GB per year)
- **Estimated cost**: ~$0.02/month for active + $0.05/month for long-term = **$0.07/month**

#### control_events

- **Active**: All data (interventions are rare, ~1 MB total)
- **Estimated cost**: ~$0.002/month = **negligible**

### Total Estimated Storage Cost

**~$0.08/month** (under GCP Free Tier)

---

## Query Examples

### Basic Queries

#### Get recent temperature readings

```sql
SELECT
  timestamp,
  sensor_id,
  value,
  unit
FROM
  `project.dataset.sensor_readings`
WHERE
  sensor_type = 'temperature'
  AND location = 'aquarium'
  AND timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
ORDER BY
  timestamp DESC
LIMIT 100;
```

#### Get all fan control events

```sql
SELECT
  timestamp,
  action,
  trigger_value,
  trigger_threshold,
  success
FROM
  `project.dataset.control_events`
WHERE
  event_type = 'automated_thermostat'
ORDER BY
  timestamp DESC;
```

### Causal Analysis Queries

#### Fan cooling effect (30-minute post-intervention)

```sql
WITH fan_events AS (
  SELECT
    event_id,
    timestamp AS event_time,
    trigger_value AS pre_temp
  FROM
    `project.dataset.control_events`
  WHERE
    event_type = 'automated_thermostat'
    AND action = 'fan_on'
    AND success = true
)
SELECT
  e.event_id,
  e.event_time,
  e.pre_temp,
  AVG(s.value) AS post_temp_30min,
  e.pre_temp - AVG(s.value) AS cooling_effect
FROM
  fan_events e
LEFT JOIN
  `project.dataset.sensor_readings` s
ON
  s.sensor_id = 'ds18b20_001'
  AND s.timestamp BETWEEN TIMESTAMP_ADD(e.event_time, INTERVAL 25 MINUTE)
                      AND TIMESTAMP_ADD(e.event_time, INTERVAL 35 MINUTE)
GROUP BY
  e.event_id, e.event_time, e.pre_temp
ORDER BY
  e.event_time DESC;
```

#### Water change impact on parameters

```sql
WITH water_changes AS (
  SELECT
    event_id,
    timestamp AS change_time,
    JSON_EXTRACT_SCALAR(action_details, '$.volume_liters') AS volume
  FROM
    `project.dataset.control_events`
  WHERE
    action = 'water_change'
    AND success = true
)
SELECT
  wc.event_id,
  wc.change_time,
  wc.volume,
  s.sensor_type,
  AVG(CASE WHEN s.timestamp < wc.change_time THEN s.value END) AS pre_value,
  AVG(CASE WHEN s.timestamp > wc.change_time THEN s.value END) AS post_value,
  AVG(CASE WHEN s.timestamp > wc.change_time THEN s.value END) -
  AVG(CASE WHEN s.timestamp < wc.change_time THEN s.value END) AS delta
FROM
  water_changes wc
LEFT JOIN
  `project.dataset.sensor_readings` s
ON
  s.location = 'aquarium'
  AND s.timestamp BETWEEN TIMESTAMP_SUB(wc.change_time, INTERVAL 1 HOUR)
                      AND TIMESTAMP_ADD(wc.change_time, INTERVAL 1 HOUR)
GROUP BY
  wc.event_id, wc.change_time, wc.volume, s.sensor_type
ORDER BY
  wc.change_time DESC, s.sensor_type;
```

---

## Related Documents

- [ADR-0006: Simplified Schema Design](../decisions/0006-simplified-schema-design.md)
- [How-to: Record Manual Events with Google Forms](../how-to/record-manual-events-forms.md)
- [Implementation Guide: Aquarium Thermostat Complete Manual](../guides/aquarium-thermostat-complete-manual.md)
