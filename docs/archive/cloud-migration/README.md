# 🌊 AquaPulse Cloud Migration Guide

**Complete Migration from Raspberry Pi → ESP32 + GCP**

---

## 🚨 **Why Migrate to Cloud Now**

### **Current Situation**

```
❌ Cannot SSH to Raspberry Pi
❌ No physical access (behind aquarium, cannot connect monitor/keyboard)
❌ Tailscale also fails to connect
❌ DHCP reservation not working
```

### **Comparison of Options**

| Option | Effort | Future-proof | Root Solution |
|--------|--------|--------------|---------------|
| **A. OS Reset → Raspberry Pi Recovery** | Medium (recovery guide exists) | Low (same problem may recur) | ❌ |
| **B. Cloud Migration (this guide)** | Medium (new construction) | High (IP issue resolved) | ✅ |

**Conclusion**: **If both require similar effort to build from scratch**, **cloud migration that solves root cause is wise**.

### **Why Now is Optimal Timing**

```
✅ OS reset needed anyway = no attachment to existing environment
✅ Data loss unavoidable = low migration barrier
✅ Same effort → choose high future value
✅ Raspberry Pi recovery has recurrence risk
```

**This document assumes "Raspberry Pi is dead now."**

---

## 📋 **About This Documentation**

### **Purpose**

Fundamentally solve Raspberry Pi's **IP address problem** and **physical access problem** by migrating to ESP32 + GCP architecture.

### **Architecture After Migration**

```
【Current】
Raspberry Pi (behind aquarium, inaccessible)
  - Sensor reading
  - DB & Grafana
  - SSH connection (disconnects)

【After Migration】
ESP32 (behind aquarium)
  - Sensor reading only
  ↓ WiFi
GCP (Cloud)
  - BigQuery (data storage)
  - Grafana Cloud (visualization)
  - Fully remote managed
```

---

## 🎯 **Benefits**

| Item | Current (Raspberry Pi🔴dead) | After Migration (ESP32+GCP) |
|------|----------------------------|---------------------------|
| **Physical Access** | Required but impossible (stuck) | Unnecessary (fully cloud) |
| **IP Address** | Fixed but cannot connect | No need to worry |
| **Device Cost** | Raspberry Pi: $100 (unusable) | ESP32: $20 |
| **Monthly Cost** | Electricity: $2 (waste) | GCP free tier: $0 |
| **Scalability** | Limited (not even working) | Nearly infinite |
| **Phase 3 Prep** | Impossible (no access) | BigQuery+Databricks ready |
| **During Trouble** | Stuck (current state) | Remote response possible |

---

## 📚 **Documentation Structure**

### **1. [00_OVERVIEW.md](00_OVERVIEW.md)** - Overview
- System architecture diagram
- Tech stack
- Cost estimation
- Migration schedule

### **2. [01_HARDWARE_SETUP.md](01_HARDWARE_SETUP.md)** - Hardware Preparation
- ESP32 purchase guide (Amazon links)
- Parts list
- Wiring diagram
- Sensor connection

### **3. [02_GCP_SETUP.md](02_GCP_SETUP.md)** - GCP Environment Setup
- Project creation
- Authentication setup
- Enable required APIs
- gcloud CLI setup

### **4. [03_PHASE1_MANUAL.md](03_PHASE1_MANUAL.md)** - Phase 1: Manual Deployment
- Manual deployment with gcloud CLI
- Operation check
- Troubleshooting
- Learning points

### **5. [04_PHASE2_AUTOMATION.md](04_PHASE2_AUTOMATION.md)** - Phase 2: Automation
- GitHub Actions configuration
- Dev/Prod environment separation
- CI/CD pipeline
- Rollback method

### **6. [05_TESTING.md](05_TESTING.md)** - Testing & Validation
- Local testing (Functions Framework)
- Dev environment testing
- Pre-production deployment checklist
- Performance testing

### **7. [06_OPERATIONS.md](06_OPERATIONS.md)** - Operations Guide
- Daily operations flow
- Monitoring
- Alert configuration
- Backup & Restore

### **8. [07_TROUBLESHOOTING.md](07_TROUBLESHOOTING.md)** - Troubleshooting
- Common issues and solutions
- Error message collection
- Debugging methods
- Support contacts

### **9. [08_REFERENCES.md](08_REFERENCES.md)** - References
- ESP32 aquarium monitoring implementations
- Technical articles
- Similar projects

---

## 🚀 **Quick Start (3 Steps)**

### **Step 1: Hardware Preparation (1-2 days)**
```bash
# Purchase ESP32 → Wait for arrival → Wiring
```
Details: [01_HARDWARE_SETUP.md](01_HARDWARE_SETUP.md)

### **Step 2: GCP Environment Setup (1 day)**
```bash
# Create project → Authentication → Manual deployment
```
Details: [02_GCP_SETUP.md](02_GCP_SETUP.md) + [03_PHASE1_MANUAL.md](03_PHASE1_MANUAL.md)

### **Step 3: Automation (1 day)**
```bash
# GitHub Actions configuration → Deploy with just git push
```
Details: [04_PHASE2_AUTOMATION.md](04_PHASE2_AUTOMATION.md)

---

## 📊 **Progress Checklist**

### **Phase 0: Preparation**
- [ ] Read this documentation
- [ ] Purchase ESP32
- [ ] Create GCP account
- [ ] Create Grafana Cloud account
- [ ] ⚠️ Leave Raspberry Pi alone (don't touch)

### **Phase 1: Development Environment (Manual)**
- [ ] ESP32 setup
- [ ] GCP project creation
- [ ] Manual deployment success
- [ ] Dev environment test (24-hour operation)

### **Phase 2: Automation**
- [ ] GitHub Actions configuration
- [ ] Dev environment auto-deployment
- [ ] Prod environment auto-deployment
- [ ] Operation check

### **Phase 3: Production Operation**
- [ ] ESP32 production operation start
- [ ] Confirm data collection rate ≥95%
- [ ] Confirm sensor value validity
- [ ] Confirm Grafana dashboard display
- [ ] 1 week stable operation
- [ ] ⚠️ Leave Raspberry Pi completely alone (or physically remove later)

---

## 🎓 **Learning Approach**

### **Recommended Order**

```
1. Understand big picture
   └ Read 00_OVERVIEW.md
   
2. Hardware preparation
   └ 01_HARDWARE_SETUP.md
   
3. GCP basics
   └ 02_GCP_SETUP.md
   
4. Hands-on (Phase 1)
   └ 03_PHASE1_MANUAL.md
   └ Understand mechanism here!
   
5. Automation (Phase 2)
   └ 04_PHASE2_AUTOMATION.md
   
6. Testing
   └ 05_TESTING.md
   
7. Production operation
   └ 06_OPERATIONS.md
```

### **Time Allocation Guide**

| Phase | Time | Content |
|-------|------|---------|
| Preparation | 1-2 days | ESP32 purchase & arrival |
| Phase 1 | 1 day | Learn through manual deployment |
| Phase 2 | 1 day | GitHub Actions configuration |
| Testing | 2-3 days | Parallel operation & verification |
| **Total** | **5-7 days** | - |

---

## 💡 **Important Concepts**

### **1. Pub/Sub Role**

```
ESP32 → Pub/Sub → Cloud Functions → BigQuery
        ↑ Buffering here
        
Benefits:
  - Data guarantee (7-day retention)
  - Automatic retry
  - High availability (SLA 99.95%)
```

Details: [00_OVERVIEW.md](00_OVERVIEW.md#pubsub)

### **2. Dev/Prod Separation**

```
Development: aquapulse-dev
  ↓ Test success
Production: aquapulse
```

Details: [04_PHASE2_AUTOMATION.md](04_PHASE2_AUTOMATION.md#devprod)

### **3. IaC (Infrastructure as Code)**

```
Manage infrastructure with terraform/
  - Version control
  - Environment replication
  - Change history
```

Details: [04_PHASE2_AUTOMATION.md](04_PHASE2_AUTOMATION.md#terraform)

---

## 🆘 **If Stuck**

### **Troubleshooting**
See [07_TROUBLESHOOTING.md](07_TROUBLESHOOTING.md)

### **Don't Understand Terms**
See glossary in [08_REFERENCES.md](08_REFERENCES.md)

### **GCP Service Details**
See [00_OVERVIEW.md](00_OVERVIEW.md)

---

## 🔗 **External Links**

- [GCP Official Documentation](https://cloud.google.com/docs)
- [ESP32 Official](https://www.espressif.com/en/products/socs/esp32)
- [MicroPython](https://micropython.org/)
- [GitHub Actions](https://docs.github.com/actions)

---

## 📝 **Change Log**

| Date | Version | Changes |
|------|---------|---------|
| 2026-07-03 | 1.1.0 | **Fully revised assuming dead Raspberry Pi** (no SSH, no parallel operation) |
| 2026-07-03 | 1.0.0 | Initial version |

---

**Next Step:** Read [00_OVERVIEW.md](00_OVERVIEW.md) to understand the big picture!
