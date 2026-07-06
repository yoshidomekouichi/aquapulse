# Hardware Setup Guide

**Complete guide from ESP32 purchase to sensor wiring**

---

## Shopping List

### Required Items

| Item | Price | Notes |
|------|-------|-------|
| **ESP32-DevKitC** | $15 | 38-pin recommended |
| **Breadboard (830-point)** | $5 | Half-size |
| **Jumper wires (M-M, M-F)** | $3 | 20-40 pieces |
| **USB Type-C cable** | $5 | Data capable |
| **4.7kΩ resistor** | $1 | For DS18B20 pull-up |

**Total: ~$29**

### Reusable Sensors (from Raspberry Pi)

| Sensor | Status | Purpose |
|--------|--------|---------|
| **DS18B20 (waterproof probe)** | ✅ Reuse | Water temperature |
| **MCP3424 (I2C ADC)** | ✅ Reuse | TDS sensor interface |
| **TDS probe** | ✅ Reuse | Water quality |

### Optional (Recommended)

| Item | Price | Purpose |
|------|-------|---------|
| **Spare ESP32** | $15 | Backup for failures |
| **USB power adapter (5V 1A)** | $8 | Stable power supply |
| **Breadboard power module** | $4 | 3.3V/5V rail power |

---

## ESP32 Selection Guide

### What to Look For

```
Search: "ESP32 development board"

✅ Recommended features:
  - ESP-WROOM-32 module
  - 38-pin (19×2)
  - USB Type-C or Micro USB
  - WiFi + Bluetooth built-in
  - FCC/CE certified

❌ Avoid:
  - ESP8266 (WiFi only, older)
  - <26 pins (insufficient GPIO)
  - No certifications (legal issues)
```

### Specific Product Examples

- HiLetgo ESP32-DevKitC
- KKHMF ESP32 Development Board
- AZDelivery ESP32 Dev Kit C

**Price range:** $12-20

**Memory:** 16MB flash recommended (8MB minimum)

---

## Wiring Diagram

### Overview

```
┌──────────────────────────────────────────────┐
│              Breadboard (830-point)          │
│                                              │
│  Power Rails                                 │
│  ┌────────────────────────────────┐          │
│  │ + (red)                        │          │
│  │ - (blue/black)                 │          │
│  └────────────────────────────────┘          │
│                                              │
│  ┌──────────────────┐                        │
│  │  ESP32-DevKitC   │                        │
│  │                  │                        │
│  │ 3V3 ○────┬───────○ + rail                │
│  │          │       │                        │
│  │ GND ○────┴───────○ - rail                │
│  │                  │                        │
│  │ GPIO4 ○──────────○ DS18B20 DATA          │
│  │ GPIO21 ○─────────○ MCP3424 SDA           │
│  │ GPIO22 ○─────────○ MCP3424 SCL           │
│  └──────────────────┘                        │
│                                              │
│  ┌──────────────────┐                        │
│  │   DS18B20        │  Waterproof probe     │
│  │                  │                        │
│  │ VDD ○────────────○ + rail                │
│  │ GND ○────────────○ - rail                │
│  │ DATA ○───────────○ GPIO4                 │
│  │      │           │  (+ 4.7kΩ → 3V3)      │
│  └──────────────────┘                        │
│                                              │
│  ┌──────────────────┐                        │
│  │   MCP3424        │  I2C ADC              │
│  │                  │                        │
│  │ VDD ○────────────○ + rail                │
│  │ GND ○────────────○ - rail                │
│  │ SDA ○────────────○ GPIO21                │
│  │ SCL ○────────────○ GPIO22                │
│  │                  │                        │
│  │ CH1+ ○───────────○ TDS probe +           │
│  │ CH1- ○───────────○ TDS probe - (GND)     │
│  └──────────────────┘                        │
│                                              │
└──────────────────────────────────────────────┘
```

### Pin Assignments

| Pin | Connection | Purpose |
|-----|------------|---------|
| **3V3** | Power rail (+) | 3.3V supply |
| **GND** | Power rail (-) | Ground |
| **GPIO4** | DS18B20 DATA | 1-Wire temperature |
| **GPIO21** | MCP3424 SDA | I2C data |
| **GPIO22** | MCP3424 SCL | I2C clock |

---

## Step-by-Step Wiring

### Step 1: Insert ESP32 into Breadboard

1. Locate the center gap on the breadboard
2. Insert ESP32 straddling the gap
3. Ensure all pins are fully inserted
4. Verify both sides of pins are accessible

**Notes:**
- USB port should face up or down
- Don't bend pins
- Apply gentle, even pressure

### Step 2: Connect Power Rails

1. **Red jumper wire:**
   - From: ESP32 `3V3` pin
   - To: Breadboard `+` rail

2. **Black jumper wire:**
   - From: ESP32 `GND` pin
   - To: Breadboard `-` rail

**Verification:**
- Red connects to `+` rail (usually marked with red line)
- Black connects to `-` rail (usually marked with blue/black line)

### Step 3: Connect DS18B20 (Water Temperature)

1. **Identify DS18B20 wires (3 wires):**
   - Red: VDD (power)
   - Black: GND (ground)
   - Yellow/White: DATA (signal)

2. **Connections:**
   - Red (VDD) → `+` rail
   - Black (GND) → `-` rail
   - Yellow (DATA) → ESP32 `GPIO4`

3. **Pull-up resistor (4.7kΩ):**
   - One leg → DS18B20 DATA line (or GPIO4)
   - Other leg → `+` rail (3V3)

**Why pull-up resistor?**
- DS18B20 uses 1-Wire protocol
- Requires pull-up resistor on DATA line
- 4.7kΩ is standard value

### Step 4: Connect MCP3424 (TDS Sensor Interface)

1. **Power connections:**
   - VDD → `+` rail
   - GND → `-` rail

2. **I2C connections:**
   - SDA → ESP32 `GPIO21`
   - SCL → ESP32 `GPIO22`

3. **TDS probe connections:**
   - CH1+ → TDS probe `+`
   - CH1- → TDS probe `-` (ground)

**I2C address:**
- Default: `0x68` (factory setting)
- No address jumpers needed if using single MCP3424

### Step 5: Final Checks

**Visual inspection:**
- [ ] All connections firm and secure
- [ ] No loose wires
- [ ] No short circuits (wires touching)
- [ ] Power (`+` and `-`) not reversed

**Power test (no sensors yet):**
1. Connect ESP32 to computer via USB
2. Check for:
   - Blue LED on ESP32 lights up
   - ESP32 feels slightly warm (normal)
   - No smoke or burning smell

**If power test fails:**
- Immediately disconnect USB
- Check for reversed polarity
- Check for short circuits

---

## Sensor Testing

### DS18B20 Quick Test

```python
# esp32/test_ds18b20.py

import machine
import onewire
import ds18x20
import time

# Initialize
dat = machine.Pin(4)
ds = ds18x20.DS18X20(onewire.OneWire(dat))

# Scan for sensors
roms = ds.scan()
print('Found DS18B20:', [rom.hex() for rom in roms])

# Read temperature
if roms:
    ds.convert_temp()
    time.sleep_ms(750)
    for rom in roms:
        temp = ds.read_temp(rom)
        print(f'Temperature: {temp}°C')
```

**Expected output:**
```
Found DS18B20: ['28abcd1234567890']
Temperature: 25.3°C
```

### MCP3424 Quick Test

```python
# esp32/test_mcp3424.py

from machine import I2C, Pin
import struct

# Initialize I2C
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)

# Scan for devices
devices = i2c.scan()
print('I2C devices found:', [hex(d) for d in devices])

# Expected: [0x68] for MCP3424
```

**Expected output:**
```
I2C devices found: ['0x68']
```

---

## Troubleshooting

### DS18B20 Not Detected

**Symptoms:**
- `ds.scan()` returns empty list `[]`

**Solutions:**
1. Check DATA wire connection (yellow → GPIO4)
2. Verify pull-up resistor (4.7kΩ) is installed
3. Check power connections (red → 3V3, black → GND)
4. Try different GPIO pin (e.g., GPIO5)

### MCP3424 Not Detected

**Symptoms:**
- `i2c.scan()` doesn't show `0x68`

**Solutions:**
1. Check I2C wiring:
   - SDA (data) → GPIO21
   - SCL (clock) → GPIO22
2. Verify power connections
3. Check for loose connections
4. Try lower I2C frequency: `freq=50000`

### ESP32 Won't Boot

**Symptoms:**
- No LED
- Computer doesn't recognize device
- "Brownout detector" error

**Solutions:**
1. Check USB cable (must support data, not just charging)
2. Try different USB port
3. Use external 5V power supply (not computer USB)
4. Check for short circuits on breadboard

### Unstable Readings

**Symptoms:**
- Temperature jumps wildly
- TDS readings fluctuate excessively

**Solutions:**
1. Check for loose connections
2. Keep wires away from noise sources (motors, relays)
3. Add decoupling capacitors (0.1µF near sensors)
4. Use twisted pair for long sensor cables
5. Software averaging (read 10 times, take median)

---

## Physical Placement

### Development Phase (USB connected)

```
Aquarium
   ↑
   | (Sensors stay in water)
   |
   ├─ DS18B20 probe (long cable, ~2m)
   └─ TDS probe (long cable, ~2m)
        ↓
ESP32 on breadboard
   (Near coffee table, USB to laptop)
```

**Requirements:**
- 2m sensor cables (extend if needed)
- Laptop/desktop near aquarium
- Stable work surface for breadboard

### Production Phase (WiFi only)

```
Aquarium
   ↑
   | (Sensors stay in water)
   |
   ├─ DS18B20 probe (short cable)
   └─ TDS probe (short cable)
        ↓
ESP32 on breadboard
   (Behind aquarium, USB power only)
```

**Requirements:**
- 5V USB power adapter (not laptop)
- Stable WiFi signal
- Accessible for power cycling

---

## Safety Notes

### Electrical Safety

```
⚠️  IMPORTANT:
  - ESP32 is 3.3V logic (NOT 5V tolerant on most pins)
  - Don't connect 5V sensors directly to GPIO
  - Always double-check polarity before powering on
  - Use proper USB power supply (≥500mA)
```

### Water Safety

```
⚠️  IMPORTANT:
  - Waterproof probes only for submerged sensors
  - ESP32 and breadboard must stay dry
  - Keep electronics above aquarium level
  - Use drip loops on cables
```

### Aquarium Safety

```
⚠️  IMPORTANT:
  - Unplug all aquarium equipment before wiring
  - Test sensors in tap water first, not aquarium
  - Monitor fish behavior after sensor installation
  - Remove sensors immediately if fish show stress
```

---

## Next Steps

Once hardware is set up and tested:

1. **Install MicroPython:** [micropython-setup.md](micropython-setup.md)
2. **Configure WiFi:** [wifi-configuration.md](wifi-configuration.md)
3. **Deploy sensor code:** [deployment.md](deployment.md)

---

## Reference

- **Architecture details:** [architecture.md](../reference/architecture.md)
- **Troubleshooting:** [troubleshooting.md](troubleshooting.md)
- **ESP32 pinout:** [ESP32-DevKitC Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32_datasheet_en.pdf)
