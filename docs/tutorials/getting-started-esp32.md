# Getting Started with ESP32 Aquarium Monitoring

**Your first steps with ESP32 + GCP cloud-native aquarium monitoring**

---

## What You'll Learn

By the end of this tutorial, you will:

- Set up ESP32 hardware with a temperature sensor
- Write your first MicroPython sensor reading code
- Send sensor data to GCP Pub/Sub
- View data in BigQuery
- Create a simple Grafana dashboard

**Time required:** 2-3 hours

**Prerequisites:**
- Basic understanding of Python
- Comfortable using terminal/command line
- GCP account with billing enabled (free tier is sufficient)

---

## Overview

### What We're Building

```
ESP32 (water temp sensor)
    ↓ WiFi
GCP Pub/Sub
    ↓
Cloud Functions
    ↓
BigQuery
    ↓
Grafana dashboard
```

**Goal:** See live water temperature in a dashboard!

---

## Step 1: Hardware Assembly (30 min)

### What You Need

- ESP32-DevKitC (38-pin)
- DS18B20 waterproof temperature sensor
- 4.7kΩ resistor
- Breadboard (830-point)
- Jumper wires (M-M, M-F)
- USB Type-C cable

### Wiring

1. **Insert ESP32 into breadboard**
   - Straddle the center gap
   - USB port facing up or down

2. **Connect power rails**
   - ESP32 `3V3` → breadboard `+` rail (red wire)
   - ESP32 `GND` → breadboard `-` rail (black wire)

3. **Connect DS18B20 sensor**
   - Red wire (VDD) → `+` rail
   - Black wire (GND) → `-` rail
   - Yellow wire (DATA) → ESP32 `GPIO4`

4. **Add pull-up resistor**
   - One leg → DS18B20 DATA line (or GPIO4)
   - Other leg → `+` rail

**Verify:**
- All connections are firm
- No wires touching each other
- Power polarity is correct

**Photo reference:** See [hardware-setup.md](../guides/hardware-setup.md) for detailed wiring diagrams.

---

## Step 2: Install MicroPython (20 min)

### Download MicroPython Firmware

1. Visit: https://micropython.org/download/esp32/

2. Download latest stable release:
   - File: `esp32-XXXXXXXX.bin` (~1.8MB)
   - Example: `esp32-20231005-v1.21.0.bin`

### Install esptool

```bash
# Install Python package
pip install esptool

# Verify installation
esptool.py version

# Expected output: esptool.py v4.7.0
```

### Flash MicroPython to ESP32

```bash
# 1. Connect ESP32 to computer via USB

# 2. Find serial port
# Mac: /dev/tty.usbserial-*
# Linux: /dev/ttyUSB0
# Windows: COM3

# 3. Erase flash (one-time)
esptool.py --port /dev/tty.usbserial-XXX erase_flash

# Output:
# Erasing flash (this may take a while)...
# Chip erase completed successfully

# 4. Flash MicroPython
esptool.py --chip esp32 --port /dev/tty.usbserial-XXX write_flash -z 0x1000 esp32-20231005-v1.21.0.bin

# Output:
# Writing at 0x00001000... (100%)
# Hash of data verified.
# Leaving...
# Hard resetting via RTS pin...
```

### Test MicroPython

```bash
# Install screen (if not already)
# Mac/Linux: usually pre-installed
# Windows: use PuTTY instead

# Connect to ESP32 REPL
screen /dev/tty.usbserial-XXX 115200

# You should see:
# >>>

# Test Python
>>> print("Hello from ESP32!")
Hello from ESP32!

# Check version
>>> import sys
>>> sys.version
'3.4.0; MicroPython v1.21.0 on 2023-10-05'

# Exit screen: Ctrl-A then K, then Y
```

**If connection fails:**
- Try pressing `EN` button on ESP32
- Check USB cable (must support data)
- Try different USB port
- On Mac, use `/dev/cu.usbserial-*` instead

---

## Step 3: Read Temperature Sensor (30 min)

### Create Sensor Reading Script

1. **Install file transfer tool:**
   ```bash
   pip install ampy
   ```

2. **Create test script:**
   ```bash
   # Create file: test_temp.py
   cat > test_temp.py << 'EOF'
   import machine
   import onewire
   import ds18x20
   import time

   # Initialize DS18B20 on GPIO4
   dat = machine.Pin(4)
   ds = ds18x20.DS18X20(onewire.OneWire(dat))

   # Scan for sensors
   print("Scanning for DS18B20...")
   roms = ds.scan()

   if not roms:
       print("ERROR: No DS18B20 found!")
       print("Check wiring:")
       print("  - Red (VDD) to 3V3")
       print("  - Black (GND) to GND")
       print("  - Yellow (DATA) to GPIO4")
       print("  - 4.7kΩ resistor between DATA and 3V3")
   else:
       print(f"Found {len(roms)} sensor(s):")
       for rom in roms:
           print(f"  - {rom.hex()}")
       
       print("\nReading temperature every 5 seconds...")
       print("Press Ctrl-C to stop\n")
       
       while True:
           ds.convert_temp()
           time.sleep_ms(750)  # Wait for conversion
           
           for rom in roms:
               temp = ds.read_temp(rom)
               print(f"Temperature: {temp:.2f}°C")
           
           time.sleep(5)
   EOF
   ```

3. **Upload and run:**
   ```bash
   # Upload to ESP32
   ampy --port /dev/tty.usbserial-XXX put test_temp.py

   # Connect to REPL
   screen /dev/tty.usbserial-XXX 115200

   # Run script
   >>> import test_temp

   # Expected output:
   # Scanning for DS18B20...
   # Found 1 sensor(s):
   #   - 28abcd1234567890
   # 
   # Reading temperature every 5 seconds...
   # 
   # Temperature: 25.31°C
   # Temperature: 25.37°C
   # Temperature: 25.34°C
   # ...
   ```

**Success criteria:**
- Sensor is detected (ROM address printed)
- Temperature readings are stable (±0.5°C variation)
- Values are reasonable (15-35°C room temp)

**If sensor not detected:**
- Check wiring (especially DATA → GPIO4)
- Verify pull-up resistor is installed
- Try measuring sensor resistance (should be ~10kΩ between VDD and GND)

**If readings are unstable:**
- Check for loose connections
- Try shorter wires
- Add 0.1µF capacitor near sensor (VDD to GND)

---

## Step 4: GCP Setup (45 min)

### Create GCP Resources

Follow the detailed guide: [gcp-setup.md](../guides/gcp-setup.md)

**Summary:**

1. **Create project:**
   ```bash
   gcloud projects create aquapulse-tutorial --name="AquaPulse Tutorial"
   gcloud config set project aquapulse-tutorial
   ```

2. **Enable APIs:**
   ```bash
   gcloud services enable \
     pubsub.googleapis.com \
     cloudfunctions.googleapis.com \
     bigquery.googleapis.com
   ```

3. **Create Pub/Sub topic:**
   ```bash
   gcloud pubsub topics create sensor-data
   ```

4. **Create BigQuery dataset:**
   ```bash
   bq mk --dataset aquapulse_tutorial
   ```

5. **Create BigQuery table:**
   ```bash
   cat > schema.json << 'EOF'
   [
     {"name": "timestamp", "type": "TIMESTAMP", "mode": "REQUIRED"},
     {"name": "sensor_id", "type": "STRING", "mode": "REQUIRED"},
     {"name": "value", "type": "FLOAT", "mode": "REQUIRED"},
     {"name": "unit", "type": "STRING", "mode": "REQUIRED"}
   ]
   EOF

   bq mk --table \
     --time_partitioning_field=timestamp \
     --time_partitioning_type=DAY \
     aquapulse_tutorial.sensor_readings \
     schema.json
   ```

**Verify:**
```bash
gcloud pubsub topics list
# Should show: sensor-data

bq ls aquapulse_tutorial
# Should show: sensor_readings
```

---

## Step 5: Deploy Cloud Function (30 min)

### Create Ingest Function

1. **Create function directory:**
   ```bash
   mkdir -p cloud-functions/ingest
   cd cloud-functions/ingest
   ```

2. **Create `main.py`:**
   ```python
   import base64
   import json
   import logging
   from datetime import datetime
   from google.cloud import bigquery

   # Initialize BigQuery client
   client = bigquery.Client()
   table_id = "aquapulse-tutorial.aquapulse_tutorial.sensor_readings"

   def ingest(event, context):
       """Triggered from a message on a Cloud Pub/Sub topic.
       
       Args:
            event (dict): Event payload.
            context (google.cloud.functions.Context): Metadata for the event.
       """
       # Decode Pub/Sub message
       pubsub_message = base64.b64decode(event['data']).decode('utf-8')
       data = json.loads(pubsub_message)
       
       logging.info(f"Received: {data}")
       
       # Prepare row for BigQuery
       row = {
           "timestamp": datetime.utcnow().isoformat(),
           "sensor_id": data.get("sensor_id", "unknown"),
           "value": float(data.get("value", 0)),
           "unit": data.get("unit", "unknown")
       }
       
       # Insert into BigQuery
       errors = client.insert_rows_json(table_id, [row])
       
       if errors:
           logging.error(f"BigQuery insert errors: {errors}")
           return ("Error", 500)
       
       logging.info(f"Inserted: {row}")
       return ("OK", 200)
   ```

3. **Create `requirements.txt`:**
   ```
   google-cloud-bigquery==3.11.4
   ```

4. **Deploy function:**
   ```bash
   gcloud functions deploy ingest \
     --runtime=python311 \
     --trigger-topic=sensor-data \
     --region=asia-northeast1 \
     --timeout=60s \
     --memory=256MB

   # This takes 2-5 minutes
   # Expected output:
   # Deploying function...done.
   # status: ACTIVE
   ```

### Test Function

```bash
# Publish test message
gcloud pubsub topics publish sensor-data \
  --message='{"sensor_id":"test_sensor","value":25.5,"unit":"celsius"}'

# Check logs
gcloud functions logs read ingest --region=asia-northeast1 --limit=10

# Expected log:
# Received: {'sensor_id': 'test_sensor', 'value': 25.5, 'unit': 'celsius'}
# Inserted: {'timestamp': '2026-07-06T...', ...}

# Verify in BigQuery
bq query --use_legacy_sql=false \
  'SELECT * FROM `aquapulse_tutorial.sensor_readings` ORDER BY timestamp DESC LIMIT 5'

# Should show 1 row with test data
```

---

## Step 6: Send Data from ESP32 (30 min)

### Install MQTT Library

1. **Download `umqtt.simple`:**
   - Visit: https://github.com/micropython/micropython-lib/blob/master/micropython/umqtt.simple/umqtt/simple.py
   - Save as `umqtt_simple.py` on your computer

2. **Upload to ESP32:**
   ```bash
   ampy --port /dev/tty.usbserial-XXX put umqtt_simple.py umqtt/simple.py
   ```

### Create Main Script

```python
# File: main.py

import network
import time
import machine
import onewire
import ds18x20
import json
from umqtt.simple import MQTTClient

# Configuration
WIFI_SSID = "YourWiFiSSID"
WIFI_PASSWORD = "YourWiFiPassword"
MQTT_BROKER = "mqtt.example.com"  # GCP IoT Core or MQTT bridge
MQTT_TOPIC = b"aquapulse/sensor-data"
SENSOR_ID = "esp32_water_temp"

# Initialize DS18B20
dat = machine.Pin(4)
ds = ds18x20.DS18X20(onewire.OneWire(dat))
roms = ds.scan()

# Connect to WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print(f"Connecting to WiFi: {WIFI_SSID}")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
    print(f"WiFi connected: {wlan.ifconfig()[0]}")
    return wlan

# Main loop
def main():
    connect_wifi()
    
    mqtt = MQTTClient("esp32", MQTT_BROKER)
    mqtt.connect()
    print("MQTT connected")
    
    while True:
        try:
            # Read temperature
            ds.convert_temp()
            time.sleep_ms(750)
            temp = ds.read_temp(roms[0])
            
            # Prepare message
            message = json.dumps({
                "sensor_id": SENSOR_ID,
                "value": temp,
                "unit": "celsius"
            })
            
            # Publish to MQTT (bridges to Pub/Sub)
            mqtt.publish(MQTT_TOPIC, message)
            print(f"Published: {message}")
            
            time.sleep(60)  # Every 60 seconds
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
```

**Note:** This tutorial uses a simplified MQTT approach. For production, use GCP IoT Core or MQTT→Pub/Sub bridge. See [deployment.md](../guides/deployment.md) for details.

---

## Step 7: View Data in Grafana (20 min)

### Create Grafana Cloud Account

1. Visit: https://grafana.com/

2. Sign up for free account (3 users, 10k metrics free)

3. Create workspace: "AquaPulse Tutorial"

### Connect BigQuery Data Source

1. **In Grafana:**
   - Configuration > Data sources > Add data source

2. **Select "Google BigQuery"**

3. **Configure:**
   - Project: `aquapulse-tutorial`
   - Dataset: `aquapulse_tutorial`
   - Authentication: Upload service account key JSON

4. **Test connection** → Should show "Data source is working"

### Create Dashboard

1. **Create new dashboard:**
   - Create > Dashboard > Add new panel

2. **Configure query:**
   ```sql
   SELECT 
     timestamp,
     value as temperature
   FROM `aquapulse_tutorial.sensor_readings`
   WHERE sensor_id = 'esp32_water_temp'
     AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
   ORDER BY timestamp ASC
   ```

3. **Configure panel:**
   - Visualization: Time series
   - Title: "Water Temperature"
   - Y-axis: "°C"

4. **Save dashboard:** "AquaPulse Tutorial"

**Result:** You should see a line graph showing temperature over time!

---

## Troubleshooting

### ESP32 Not Connecting to WiFi

**Symptoms:**
- "Connecting to WiFi..." stuck

**Solutions:**
- Check SSID and password (case-sensitive)
- Move ESP32 closer to router
- Check WiFi is 2.4GHz (ESP32 doesn't support 5GHz)
- Try different WiFi network

### No Data in BigQuery

**Symptoms:**
- Query returns empty results

**Solutions:**
1. Check Cloud Function logs:
   ```bash
   gcloud functions logs read ingest --limit=50
   ```

2. Check for Pub/Sub messages:
   ```bash
   gcloud pubsub subscriptions pull sensor-data-test --limit=5
   ```

3. Verify MQTT→Pub/Sub bridge is working

4. Test with manual publish:
   ```bash
   gcloud pubsub topics publish sensor-data \
     --message='{"sensor_id":"esp32_water_temp","value":25.5,"unit":"celsius"}'
   ```

### Grafana Shows "No Data"

**Symptoms:**
- Dashboard panels empty

**Solutions:**
- Check time range (default: last 6 hours)
- Verify BigQuery data source connection
- Check SQL query syntax
- Ensure data exists in BigQuery:
  ```bash
  bq query --use_legacy_sql=false \
    'SELECT COUNT(*) FROM `aquapulse_tutorial.sensor_readings`'
  ```

---

## Next Steps

Congratulations! You've built your first cloud-native aquarium monitoring system! 🎉

### What You Learned

- ✅ ESP32 hardware assembly
- ✅ MicroPython programming
- ✅ Sensor data reading
- ✅ GCP Pub/Sub messaging
- ✅ Cloud Functions deployment
- ✅ BigQuery data storage
- ✅ Grafana visualization

### Continue Learning

1. **Add more sensors:**
   - TDS sensor (water quality)
   - pH sensor
   - Light sensor

2. **Improve reliability:**
   - Add error handling
   - Implement retry logic
   - Monitor system health

3. **Automate deployment:**
   - Use GitHub Actions
   - Implement CI/CD
   - See: [deployment.md](../guides/deployment.md)

4. **Advanced features:**
   - Alerting (email/SMS on anomalies)
   - Predictive maintenance (ML models)
   - Multi-aquarium support

### Reference Documentation

- **Architecture details:** [architecture.md](../reference/architecture.md)
- **Hardware setup:** [hardware-setup.md](../guides/hardware-setup.md)
- **GCP setup:** [gcp-setup.md](../guides/gcp-setup.md)
- **Troubleshooting:** [troubleshooting.md](../guides/troubleshooting.md)

---

## Feedback

Found an issue or have suggestions? Open an issue on GitHub!

Happy monitoring! 🐠💧
