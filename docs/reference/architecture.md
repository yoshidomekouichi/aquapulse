# System Architecture Reference

**Technical specifications for AquaPulse ESP32 + GCP configuration**

---

## System Architecture Diagram

### ESP32 + GCP Configuration

```
┌──────────────────────────────────────────────┐
│  Aquarium Side                                │
│                                              │
│  ┌──────────────┐                            │
│  │   ESP32      │  MicroPython               │
│  │              │                            │
│  │  Sensors     │                            │
│  │  ├ DS18B20   │  Physical sensors only     │
│  │  └ MCP3424   │                            │
│  └──────┬───────┘                            │
│         │ WiFi/MQTT                          │
└─────────┼────────────────────────────────────┘
          │
          ↓
┌──────────────────────────────────────────────┐
│  GCP (Cloud)                                 │
│                                              │
│  ┌─────────────────┐                         │
│  │    Pub/Sub      │  Messaging             │
│  │  sensor-data    │  Buffering             │
│  └────────┬────────┘                         │
│           │                                  │
│           ↓                                  │
│  ┌─────────────────┐                         │
│  │ Cloud Functions │  Serverless execution  │
│  │                 │                         │
│  │  1. ingest      │  ← ESP32 data          │
│  │  2. tapo        │  ← Tapo API            │
│  └────────┬────────┘                         │
│           │                                  │
│           ↓                                  │
│  ┌─────────────────┐                         │
│  │   BigQuery      │  Data warehouse        │
│  │                 │                         │
│  │  sensor_readings│  Time-series data      │
│  │  (partitioned)  │                         │
│  └────────┬────────┘                         │
│           │                                  │
└───────────┼──────────────────────────────────┘
            │
            ↓
┌──────────────────────────────────────────────┐
│  Grafana Cloud                               │
│                                              │
│  Dashboard (reuse existing, minor query edits)│
└──────────────────────────────────────────────┘
            ↑
            │ HTTPS
┌──────────────────────────────────────────────┐
│  User (Mac/Mobile)                           │
│                                              │
│  Browser access                              │
│  Accessible anywhere                         │
└──────────────────────────────────────────────┘
```

**Benefits:**
- ✅ No IP address dependency
- ✅ No physical access needed
- ✅ Fully remote managed
- ✅ Scalable
- ✅ Low cost (within free tier)

---

## Tech Stack

### Hardware

| Item | Raspberry Pi (Previous) | ESP32 (New) |
|------|------------------------|-------------|
| **Main Device** | Raspberry Pi 5 (8GB) | ESP32-DevKitC |
| **Size** | 10cm × 7cm | 5cm × 2.5cm |
| **Power** | 15W (5V 3A) | 2.5W (5V 0.5A) |
| **Price** | $100 | $15 |
| **Sensors** | DS18B20, MCP3424, Tapo | Same (reuse) |
| **Breadboard** | Not needed (direct wiring) | 830-point breadboard |

### Software Stack

| Layer | Raspberry Pi | ESP32 + GCP | Language |
|-------|--------------|-------------|----------|
| **Sensor Reading** | Python 3.11 | MicroPython | Python |
| **Messaging** | None (direct DB) | Pub/Sub | - |
| **Data Processing** | collector (Python) | Cloud Functions | Python |
| **Database** | TimescaleDB (PostgreSQL) | BigQuery | SQL |
| **Visualization** | Grafana (self-hosted) | Grafana Cloud | - |
| **Infrastructure** | docker-compose | Terraform | HCL |
| **CI/CD** | Manual | GitHub Actions | YAML |

---

## Data Flow

### Raspberry Pi (Previous)

```python
# collector/src/main.py

while True:
    # 1. Read sensors
    readings = []
    for source in SOURCES:
        data = source.get_readings()
        readings.extend(data)
    
    # 2. Write to DB (direct)
    save_readings(readings)
    
    time.sleep(60)

Problems:
  - Data loss on error
  - Complex thread management
  - Doesn't scale
```

### ESP32 + GCP (New)

```python
# esp32/main.py

while True:
    # 1. Read sensor
    temp = ds_sensor.read_temp(rom)
    
    # 2. Send via MQTT (buffering)
    mqtt.publish("aquapulse/sensor", {"value": temp})
    
    time.sleep(60)

# cloud-functions/ingest/main.py

def ingest(event, context):
    # 3. Receive from Pub/Sub
    data = decode(event['data'])
    
    # 4. Save to BigQuery
    client.insert_rows_json(table, [data])

Benefits:
  ✅ Data guarantee (Pub/Sub)
  ✅ Simple (each ~50 lines)
  ✅ Scalable
```

---

## GCP Services Detail

### Pub/Sub

**Role**: Message buffering and delivery guarantee

```
ESP32 → Pub/Sub Topic
          ↓ (buffer up to 7 days)
        Cloud Functions
```

**Key features:**
- Automatic retry on failure
- 7-day message retention
- SLA 99.95%
- At-least-once delivery guarantee

**Why needed:**
- ESP32 is simple, no retry logic
- Cloud Functions may be cold-started
- Network interruptions handled gracefully

### Cloud Functions

**Role**: Serverless data processing

```
Function: ingest
  Trigger: Pub/Sub message
  Runtime: Python 3.11
  Memory: 256MB
  Timeout: 60s
```

**Execution flow:**
1. Triggered by Pub/Sub message
2. Decode and validate data
3. Insert to BigQuery
4. Return success/failure

**Cost model:**
- Pay per invocation
- Free tier: 2 million invocations/month
- Our usage: ~110K/month (well within free tier)

### BigQuery

**Role**: Time-series data warehouse

```
Dataset: aquapulse_prod
Table: sensor_readings
  Partitioning: BY DAY (timestamp)
  Clustering: sensor_id, location
```

**Schema:**
```sql
CREATE TABLE sensor_readings (
  timestamp TIMESTAMP NOT NULL,
  sensor_id STRING NOT NULL,
  sensor_type STRING NOT NULL,
  value FLOAT64 NOT NULL,
  unit STRING NOT NULL,
  location STRING
)
PARTITION BY DATE(timestamp)
CLUSTER BY sensor_id, location;
```

**Query optimization:**
- Partition pruning (query only specific dates)
- Clustering (fast sensor_id lookup)
- Column-based storage (scan only needed columns)

**Cost model:**
- Storage: $0.02/GB/month (after 10GB free tier)
- Query: $5/TB scanned (after 1TB free tier/month)
- Our usage: ~134MB/year storage, ~1GB/month query (within free tier)

### Cloud Scheduler

**Role**: Periodic task execution

```
Job: tapo-collector
  Schedule: */5 * * * * (every 5 minutes)
  Target: Cloud Functions (tapo)
  Timezone: Asia/Tokyo
```

**Why needed:**
- Tapo sensors don't push data
- Need to pull via API periodically
- Cron-like scheduling in cloud

---

## Cost Estimate

### Initial Cost

| Item | Price |
|------|-------|
| ESP32-DevKitC | $15 |
| Breadboard (830-point) | $5 |
| Jumper wires | $3 |
| USB Type-C cable | $5 |
| Sensors | $0 (reuse existing) |
| **Total** | **$28** |

### Monthly Cost

#### Data Volume Estimate

```
Sensors: 4 (temp, TDS, humidity/temp, light)
Collection interval:
  - Physical sensors (ESP32): 60s
  - WiFi sensors (Tapo): 300s

Monthly records:
  ESP32: 2 sensors × 1,440/day × 30 days = 86,400 records
  Tapo: 3 sensors × 288/day × 30 days = 25,920 records
  Total: 112,320 records

Data size: ~100 bytes/record
Monthly data: 11.2MB
Annual data: 134MB
```

#### GCP Cost Breakdown

| Service | Usage/month | Free Tier | Billable | Cost |
|---------|-------------|-----------|----------|------|
| **Pub/Sub** | 11MB | 10GB | 0MB | $0 |
| **Cloud Functions (invocations)** | 110K | 2M | 0 | $0 |
| **Cloud Functions (compute)** | 3.7GB-sec | 400K GB-sec | 0 | $0 |
| **BigQuery (storage)** | 134MB/year | 10GB | 0GB | $0 |
| **BigQuery (query)** | 1GB/month | 1TB | 0GB | $0 |
| **Cloud Scheduler** | 1 job | 3 jobs | 0 | $0 |
| **Grafana Cloud** | 3 users | 3 users | 0 | $0 |
| **Cloud Logging** | 1GB/month | 50GB | 0GB | $0 |
| **Total** | - | - | - | **$0** |

**Conclusion: Entirely within free tier!** 🎉

### Annual Cost Comparison

| Configuration | Initial | Electricity/month | Service/month | Annual Total |
|---------------|---------|-------------------|---------------|--------------|
| **Raspberry Pi** | Sunk | $2 | $0 | $24 |
| **ESP32 + GCP** | $28 | $0.2 | $0 | $30 |

**Difference: +$6/year** (acceptable)

---

## Data Schema

### sensor_readings Table

```sql
-- Table: aquapulse_prod.sensor_readings

CREATE TABLE `aquapulse_prod.sensor_readings` (
  timestamp TIMESTAMP NOT NULL OPTIONS(description="Measurement time (UTC)"),
  sensor_id STRING NOT NULL OPTIONS(description="Unique sensor identifier"),
  sensor_type STRING NOT NULL OPTIONS(description="e.g., DS18B20, MCP3424, T310"),
  value FLOAT64 NOT NULL OPTIONS(description="Measured value"),
  unit STRING NOT NULL OPTIONS(description="e.g., celsius, ppm, percent"),
  location STRING OPTIONS(description="e.g., aquarium_main, room")
)
PARTITION BY DATE(timestamp)
CLUSTER BY sensor_id, location
OPTIONS(
  description="Time-series sensor readings from aquarium monitoring",
  require_partition_filter=true
);
```

### Example Queries

**Latest readings:**
```sql
SELECT 
  sensor_id,
  sensor_type,
  value,
  unit,
  timestamp
FROM `aquapulse_prod.sensor_readings`
WHERE DATE(timestamp) = CURRENT_DATE()
ORDER BY timestamp DESC
LIMIT 10;
```

**Daily average:**
```sql
SELECT 
  DATE(timestamp) as date,
  sensor_id,
  AVG(value) as avg_value,
  MIN(value) as min_value,
  MAX(value) as max_value
FROM `aquapulse_prod.sensor_readings`
WHERE DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
GROUP BY date, sensor_id
ORDER BY date DESC, sensor_id;
```

---

## Network Architecture

### Connectivity

```
ESP32 WiFi Configuration:
  SSID: (from environment variable)
  Security: WPA2-PSK
  DHCP: Dynamic IP (no fixed IP needed)
  DNS: Auto (Google DNS fallback: 8.8.8.8)

MQTT Connection:
  Protocol: MQTT over TLS (port 8883)
  QoS: 1 (at-least-once delivery)
  Keep-alive: 60s
  Clean session: False (persistent)
```

### Security

```
Authentication:
  - GCP: Service account key (JSON)
  - MQTT: Username/password (from Pub/Sub)
  - Tapo: API token (OAuth)

Encryption:
  - All traffic over TLS 1.2+
  - Certificates auto-renewed

Secrets Management:
  - Environment variables (not in code)
  - Secret Manager (GCP, future)
  - .env.example template (tracked in Git)
```

---

## Performance Specifications

### Target Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Data collection success rate** | ≥99.9% | BigQuery record count |
| **Data latency** | ≤5s average | Cloud Logging timestamp diff |
| **System uptime** | ≥99.5% | Cloud Monitoring |
| **Monthly cost** | ≤$5 | GCP Billing report |

### Actual Performance (Expected)

Based on similar ESP32 projects:
- Data collection: 96-99% (real-world)
- Latency: 1-3s typical, 10s worst-case
- ESP32 uptime: 99.9% (power-dependent)
- GCP uptime: 99.95% (SLA)

---

## Scalability

### Current Scale

```
Sensors: 4
Data points: 112K/month
Storage: 11MB/month
Query: 1GB/month
```

### Future Scale (Phase 3)

```
Sensors: 20 (5 aquariums)
Data points: 560K/month
Storage: 56MB/month
Query: 5GB/month

Still within free tier!
```

### Horizontal Scaling

```
Add new aquarium:
  1. Deploy new ESP32 (copy firmware)
  2. Configure WiFi + sensor_id
  3. No GCP changes needed (automatic)
  
BigQuery auto-scales:
  - No provisioning
  - No capacity planning
  - Pay per query (after free tier)
```

---

## Related Documentation

- **Why this architecture?** [why-cloud-migration.md](../explanation/why-cloud-migration.md)
- **Hardware setup:** [hardware-setup.md](../guides/hardware-setup.md)
- **GCP setup:** [gcp-setup.md](../guides/gcp-setup.md)
- **Deployment:** [deployment.md](../guides/deployment.md)

---

**Next:** [Hardware Setup Guide](../guides/hardware-setup.md)
