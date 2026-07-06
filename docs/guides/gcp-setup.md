# GCP Setup Guide

**From account creation to deployment-ready environment**

---

## Goals

```
GCP account
  ↓
Create project
  ↓
Install gcloud CLI
  ↓
Enable required APIs
  ↓
Authentication setup
  ↓
Ready for Phase 1 (manual deployment)
```

**Time required:** 1-2 hours

---

## Prerequisites

- [ ] Google account
- [ ] Credit card (required even for free tier)
- [ ] Terminal (Cursor built-in)
- [ ] Stable internet connection

### Important Notes

```
⚠️ About credit card registration

- Free trial: $300 credit (90 days)
- Free tier: Monthly reset free quotas
- No auto-billing: Stops when free tier exceeded (configurable)

This project stays within free tier
```

---

## Step 1: Create GCP Account

### 1-1. Access Google Cloud

```
https://console.cloud.google.com/
```

### 1-2. Initial Setup

1. Log in with Google account

2. Accept terms of service

3. Select country and currency
   - Country: (Your country)
   - Currency: (Your currency)

4. Register credit card
   - For free trial (no auto-billing)

5. Complete registration
   - $300 credit granted

---

## Step 2: Create Projects

### 2-1. Create Production Project

```
GCP Console
  ↓
Project selector (top bar)
  ↓
"New Project"
  ↓
Project name: aquapulse
Project ID: aquapulse-prod-XXXXXX
  ↑ Note the auto-generated ID
  
Click "Create"
```

### 2-2. Create Development Project (Recommended)

```
Similarly:
  Project name: aquapulse-dev
  Project ID: aquapulse-dev-XXXXXX
  
Notes:
  Production: aquapulse-prod-XXXXXX
  Development: aquapulse-dev-XXXXXX
```

**Why separate projects?**
- Test changes safely in dev
- Avoid accidental prod modifications
- Clear cost separation

---

## Step 3: Install gcloud CLI

### Mac

```bash
# In Cursor terminal

# Install via Homebrew
brew install google-cloud-sdk

# Verify installation
gcloud version

# Expected output:
# Google Cloud SDK 450.0.0
# bq 2.0.97
# core 2023.11.10
```

### Linux

```bash
# Via Snap (Ubuntu/Debian)
sudo snap install google-cloud-sdk --classic

# Or, official script
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Verify
gcloud version
```

### Windows

```powershell
# In PowerShell

# Download installer from:
# https://cloud.google.com/sdk/docs/install

# Or, via Chocolatey
choco install gcloudsdk

# Verify
gcloud version
```

---

## Step 4: Authentication

### 4-1. Initialize gcloud

```bash
# In Cursor terminal

gcloud init

# Interactive prompts:

# 1. Select account
Choose the account you would like to use:
  [1] example@gmail.com
  [2] Log in with a new account
→ Select 1 (or log in with new account)

# Browser opens → Log in with Google account

# 2. Select project
Pick cloud project to use:
  [1] aquapulse-prod-XXXXXX
  [2] aquapulse-dev-XXXXXX
  [3] Create a new project
→ Select 1 (production project)

# 3. Set default region
Do you want to configure a default Compute Region?
→ Y

→ Select your region:
  - asia-northeast1 (Tokyo)
  - us-central1 (Iowa)
  - europe-west1 (Belgium)

# Complete!
Your Google Cloud SDK is configured!
```

### 4-2. Verify Configuration

```bash
# Check current project
gcloud config get-value project

# Expected output:
# aquapulse-prod-XXXXXX

# Check account
gcloud config get-value account

# Expected output:
# example@gmail.com

# List all configurations
gcloud config list
```

### 4-3. Switch Between Projects (Optional)

```bash
# Switch to dev project
gcloud config set project aquapulse-dev-XXXXXX

# Switch back to prod
gcloud config set project aquapulse-prod-XXXXXX

# Or, create named configurations
gcloud config configurations create dev
gcloud config set project aquapulse-dev-XXXXXX

gcloud config configurations create prod
gcloud config set project aquapulse-prod-XXXXXX

# Activate configuration
gcloud config configurations activate dev
gcloud config configurations activate prod
```

---

## Step 5: Enable Required APIs

### 5-1. Enable APIs via CLI

```bash
# Enable all required APIs at once
gcloud services enable \
  pubsub.googleapis.com \
  cloudfunctions.googleapis.com \
  cloudbuild.googleapis.com \
  cloudscheduler.googleapis.com \
  bigquery.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com

# This takes ~2-3 minutes

# Verify enabled APIs
gcloud services list --enabled

# Expected output includes:
# pubsub.googleapis.com
# cloudfunctions.googleapis.com
# bigquery.googleapis.com
# ...
```

### 5-2. Alternative: Enable via Console

If CLI fails, use GCP Console:

1. Navigate to: **APIs & Services > Library**

2. Search and enable each:
   - **Cloud Pub/Sub API**
   - **Cloud Functions API**
   - **Cloud Build API**
   - **Cloud Scheduler API**
   - **BigQuery API**
   - **Cloud Logging API**
   - **Cloud Monitoring API**

3. Click "Enable" for each

---

## Step 6: Create Service Account

### 6-1. Create Service Account

```bash
# Create service account
gcloud iam service-accounts create aquapulse-sa \
  --display-name="AquaPulse Service Account" \
  --description="For Cloud Functions and BigQuery access"

# Grant necessary roles
gcloud projects add-iam-policy-binding aquapulse-prod-XXXXXX \
  --member="serviceAccount:aquapulse-sa@aquapulse-prod-XXXXXX.iam.gserviceaccount.com" \
  --role="roles/pubsub.publisher"

gcloud projects add-iam-policy-binding aquapulse-prod-XXXXXX \
  --member="serviceAccount:aquapulse-sa@aquapulse-prod-XXXXXX.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding aquapulse-prod-XXXXXX \
  --member="serviceAccount:aquapulse-sa@aquapulse-prod-XXXXXX.iam.gserviceaccount.com" \
  --role="roles/cloudfunctions.developer"
```

### 6-2. Generate Key (for ESP32)

```bash
# Generate JSON key
gcloud iam service-accounts keys create ~/aquapulse-sa-key.json \
  --iam-account=aquapulse-sa@aquapulse-prod-XXXXXX.iam.gserviceaccount.com

# Store securely
# This file contains credentials - never commit to Git!
```

---

## Step 7: Create BigQuery Resources

### 7-1. Create Dataset

```bash
# Create dataset
bq mk --dataset \
  --location=asia-northeast1 \
  --description="AquaPulse sensor data" \
  aquapulse_prod

# Verify
bq ls

# Expected output:
# aquapulse_prod
```

### 7-2. Create Table

```bash
# Create schema file
cat > /tmp/sensor_readings_schema.json << 'EOF'
[
  {"name": "timestamp", "type": "TIMESTAMP", "mode": "REQUIRED"},
  {"name": "sensor_id", "type": "STRING", "mode": "REQUIRED"},
  {"name": "sensor_type", "type": "STRING", "mode": "REQUIRED"},
  {"name": "value", "type": "FLOAT", "mode": "REQUIRED"},
  {"name": "unit", "type": "STRING", "mode": "REQUIRED"},
  {"name": "location", "type": "STRING", "mode": "NULLABLE"}
]
EOF

# Create table with partitioning
bq mk --table \
  --time_partitioning_field=timestamp \
  --time_partitioning_type=DAY \
  --clustering_fields=sensor_id,location \
  --description="Sensor readings time-series data" \
  aquapulse_prod.sensor_readings \
  /tmp/sensor_readings_schema.json

# Verify
bq show aquapulse_prod.sensor_readings
```

---

## Step 8: Create Pub/Sub Resources

### 8-1. Create Topic

```bash
# Create topic
gcloud pubsub topics create sensor-data \
  --message-retention-duration=7d

# Verify
gcloud pubsub topics list

# Expected output:
# projects/aquapulse-prod-XXXXXX/topics/sensor-data
```

### 8-2. Create Subscription (for testing)

```bash
# Create pull subscription
gcloud pubsub subscriptions create sensor-data-test \
  --topic=sensor-data \
  --ack-deadline=60

# Verify
gcloud pubsub subscriptions list

# Expected output:
# projects/aquapulse-prod-XXXXXX/subscriptions/sensor-data-test
```

---

## Step 9: Set Up Cloud Functions Environment

### 9-1. Create Storage Bucket (for Cloud Functions code)

```bash
# Create bucket (auto-created by Cloud Functions on first deploy)
# No manual action needed

# But verify region
gsutil ls -p aquapulse-prod-XXXXXX

# Expected: gcf-sources-* buckets may not exist yet (normal)
```

### 9-2. Test Cloud Functions Deployment (Simple)

```bash
# Create test function directory
mkdir -p /tmp/test-function
cd /tmp/test-function

# Create main.py
cat > main.py << 'EOF'
def hello(request):
    return "Hello from AquaPulse!"
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
# No dependencies
EOF

# Deploy test function
gcloud functions deploy hello \
  --runtime=python311 \
  --trigger-http \
  --allow-unauthenticated \
  --region=asia-northeast1

# This takes 2-5 minutes on first deployment

# Test
gcloud functions call hello --region=asia-northeast1

# Expected output:
# Hello from AquaPulse!

# Clean up test function
gcloud functions delete hello --region=asia-northeast1 --quiet
```

---

## Step 10: Set Up Monitoring & Alerts

### 10-1. Enable Budget Alerts

```bash
# Set budget alert at $5/month
gcloud billing budgets create \
  --billing-account=$(gcloud billing accounts list --format="value(name)") \
  --display-name="AquaPulse Monthly Budget" \
  --budget-amount=5USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100

# Alerts sent to your email when 50%, 90%, 100% of budget
```

### 10-2. Create Log-Based Metrics (Optional)

```bash
# Create metric for Cloud Functions errors
gcloud logging metrics create function_errors \
  --description="Count of Cloud Functions errors" \
  --log-filter='resource.type="cloud_function"
    severity>=ERROR'

# View metrics
gcloud logging metrics list
```

---

## Step 11: Verify Setup

### Checklist

Run these commands to verify everything is set up:

```bash
# 1. Check project
gcloud config get-value project
# Should show: aquapulse-prod-XXXXXX

# 2. Check enabled APIs
gcloud services list --enabled | grep -E 'pubsub|functions|bigquery'
# Should show all three

# 3. Check BigQuery dataset
bq ls
# Should show: aquapulse_prod

# 4. Check BigQuery table
bq show aquapulse_prod.sensor_readings
# Should show table schema

# 5. Check Pub/Sub topic
gcloud pubsub topics list
# Should show: sensor-data

# 6. Check service account
gcloud iam service-accounts list | grep aquapulse-sa
# Should show: aquapulse-sa@...

# 7. Check service account key
ls ~/aquapulse-sa-key.json
# Should exist
```

### Expected Results

```
✅ Project: aquapulse-prod-XXXXXX
✅ APIs enabled: pubsub, functions, bigquery, etc.
✅ BigQuery dataset: aquapulse_prod
✅ BigQuery table: sensor_readings (partitioned)
✅ Pub/Sub topic: sensor-data
✅ Service account: aquapulse-sa
✅ Service account key: ~/aquapulse-sa-key.json
```

---

## Troubleshooting

### gcloud init fails

**Symptoms:**
- Browser doesn't open
- Authentication fails

**Solutions:**
1. Manually authenticate:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

2. Check firewall/proxy settings

3. Use different browser

### API enable fails

**Symptoms:**
- "Permission denied" errors
- APIs not showing as enabled

**Solutions:**
1. Ensure billing is enabled on project
2. Check IAM permissions (need Owner or Editor role)
3. Wait 2-3 minutes and retry
4. Enable via Console instead

### BigQuery table creation fails

**Symptoms:**
- "Dataset not found" errors
- Schema validation fails

**Solutions:**
1. Verify dataset exists: `bq ls`
2. Check region matches: `asia-northeast1`
3. Verify schema JSON syntax
4. Try creating via Console

### Service account key not working

**Symptoms:**
- ESP32 authentication fails
- "Invalid credentials" errors

**Solutions:**
1. Regenerate key:
   ```bash
   gcloud iam service-accounts keys create ~/aquapulse-sa-key-new.json \
     --iam-account=aquapulse-sa@aquapulse-prod-XXXXXX.iam.gserviceaccount.com
   ```

2. Verify key file format (must be JSON)

3. Check service account has necessary roles

---

## Security Best Practices

### Service Account Key

```
⚠️  IMPORTANT:

- Never commit key file to Git
- Store in secure location (e.g., ~/.gcp/)
- Use Cursor Dashboard Runtime Secrets for Cloud Agent
- Rotate keys periodically (every 90 days)
- Delete unused keys
```

### IAM Permissions

```
Principle of least privilege:

✅ Use service accounts (not personal accounts)
✅ Grant minimum necessary roles
✅ Separate dev and prod environments
❌ Don't use Owner role for automation
❌ Don't share keys via email/Slack
```

### Budget Protection

```
Set up alerts:
- 50% of budget: Warning
- 90% of budget: Urgent
- 100% of budget: Auto-disable (optional)

Monitor daily:
- GCP Billing dashboard
- Usage reports
- Cost trends
```

---

## Cost Management

### Free Tier Limits (Monthly)

| Service | Free Tier | Our Usage | Status |
|---------|-----------|-----------|--------|
| **Pub/Sub** | 10GB | 11MB | ✅ Safe |
| **Cloud Functions** | 2M invocations | 110K | ✅ Safe |
| **BigQuery Storage** | 10GB | 134MB/year | ✅ Safe |
| **BigQuery Query** | 1TB | 1GB | ✅ Safe |
| **Cloud Scheduler** | 3 jobs | 1 | ✅ Safe |

### Monitoring Costs

```bash
# Check current month cost
gcloud billing accounts list
gcloud billing projects describe aquapulse-prod-XXXXXX

# View detailed billing
# Navigate to: Billing > Reports in GCP Console
```

---

## Next Steps

GCP environment is now ready! Proceed to:

1. **Manual deployment (Phase 1):** [manual-deployment.md](manual-deployment.md)
2. **ESP32 setup:** [hardware-setup.md](hardware-setup.md)
3. **Deployment automation:** [deployment.md](deployment.md)

---

## Reference

- **Architecture:** [architecture.md](../reference/architecture.md)
- **Why cloud migration:** [why-cloud-migration.md](../explanation/why-cloud-migration.md)
- **Troubleshooting:** [troubleshooting.md](troubleshooting.md)
- **GCP Documentation:** https://cloud.google.com/docs
