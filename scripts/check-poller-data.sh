#!/bin/bash
# BigQuery データ確認スクリプト（Mac poller）
# Usage: ./scripts/check-poller-data.sh [hours]

set -e

HOURS="${1:-24}"  # デフォルト24時間
PROJECT_ID="aquapulse-dev"
DATASET="aquapulse"
TABLE="sensor_readings"

echo "🔍 Checking Mac poller data (last ${HOURS} hours)..."
echo ""

# 最新20件
echo "📊 Latest 20 readings:"
bq query --use_legacy_sql=false --project_id="${PROJECT_ID}" \
  --format=prettyjson \
  "SELECT
    FORMAT_TIMESTAMP('%Y-%m-%d %H:%M:%S', timestamp, 'Asia/Tokyo') AS timestamp_jst,
    sensor_id,
    sensor_type,
    value,
    unit
  FROM \`${PROJECT_ID}.${DATASET}.${TABLE}\`
  WHERE device_id = 'mac_poller_v1'
  ORDER BY timestamp DESC
  LIMIT 20" | jq -r '.[] | "\(.timestamp_jst) | \(.sensor_id) | \(.sensor_type): \(.value) \(.unit)"'

echo ""
echo "📈 Data summary (last ${HOURS} hours):"
bq query --use_legacy_sql=false --project_id="${PROJECT_ID}" \
  --format=csv \
  "SELECT
    sensor_id,
    sensor_type,
    COUNT(*) AS count,
    ROUND(AVG(value), 2) AS avg_value,
    ROUND(MIN(value), 2) AS min_value,
    ROUND(MAX(value), 2) AS max_value,
    FORMAT_TIMESTAMP('%H:%M', MIN(timestamp), 'Asia/Tokyo') AS first_time,
    FORMAT_TIMESTAMP('%H:%M', MAX(timestamp), 'Asia/Tokyo') AS last_time
  FROM \`${PROJECT_ID}.${DATASET}.${TABLE}\`
  WHERE device_id = 'mac_poller_v1'
    AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL ${HOURS} HOUR)
  GROUP BY sensor_id, sensor_type
  ORDER BY sensor_id, sensor_type"

echo ""
echo "⏱️  Average polling interval:"
bq query --use_legacy_sql=false --project_id="${PROJECT_ID}" \
  --format=csv \
  "SELECT
    sensor_type,
    ROUND(TIMESTAMP_DIFF(MAX(timestamp), MIN(timestamp), MINUTE) / NULLIF(COUNT(*) - 1, 0), 1) AS avg_interval_minutes
  FROM \`${PROJECT_ID}.${DATASET}.${TABLE}\`
  WHERE device_id = 'mac_poller_v1'
    AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL ${HOURS} HOUR)
  GROUP BY sensor_type"

echo ""
echo "✅ Expected: ~15 minute intervals"
