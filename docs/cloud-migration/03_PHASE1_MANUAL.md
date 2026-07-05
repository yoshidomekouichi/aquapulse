# 🛠️ Phase 1: 手動デプロイ

**gcloud CLIで手を動かして仕組みを理解する**

---

## ⚠️ **初期開発の物理的制約（重要）**

### **ESP32開発の現実**

```
IPアドレス問題から完全に解放される？
  → いいえ、初期開発時はUSB物理接続が必須です
```

### **あなたのケースでの制約**

```
🔴 センサーが水槽に固定されている
  → ESP32も水槽近くに配置せざるを得ない
  → デスクでの開発が不可能

💡 現実的な作業環境:
  1. 3mのUSB延長ケーブル購入（必須）
  2. ノートパソコンを水槽近く（コーヒーテーブル）に常設
  3. 初期開発期間（2-3日）はこの環境で作業
```

### **モックテストの限界**

| テスト可能な要素 | デスクでモック | 水槽側で実機 |
|----------------|------------|------------|
| **WiFi接続** | ✅ 可能 | ✅ 可能 |
| **Pub/Sub送信** | ✅ 可能 | ✅ 可能 |
| **DS18B20読み取り** | ❌ センサー必須 | ✅ 可能 |
| **MCP3424読み取り** | ❌ センサー必須 | ✅ 可能 |
| **配線確認** | ❌ センサー必須 | ✅ 可能 |

**モックテストで減らせるのは通信系バグのみ（全体の40-50%）**

---

### **書き換え回数の現実的な見積もり**

```
初期統合時の書き換え回数: 3-5回

よくあるトラブル:
  1回目: 配線ミス（ピン番号間違い等）
  2回目: プルアップ抵抗値の調整
  3回目: I2Cアドレス設定ミス
  4回目: センサー値の妥当性確認
  5回目: 微調整

→ 水槽側（コーヒーテーブル）での試行錯誤は避けられない
```

### **IP問題の再評価**

```
ESP32のメリット:
  ✅ 稼働後はSSH不要（電源ON/OFFのみ）
  ✅ 長期的な管理が楽
  ✅ スケーラブル

ただし:
  ⚠️ 初期開発時はUSB物理接続必須
  ⚠️ センサー固定の場合、水槽近くでの作業が必要
  ⚠️ Raspberry Piを一時的に取り外してDHCP予約設定する方が早い可能性も

ESP32を選ぶ理由:
  → 「長期的な管理の楽さ」「スケーラビリティ」「停電に強い」
  → 初期の物理接続の手間は、将来のメンテナンスフリーで回収
```

### **推奨準備**

```
必須:
  □ 3mのUSB延長ケーブル
  □ 書き換え3-5回を覚悟
  □ 初期開発期間中（2-3日）はノートパソコンを水槽近くに常設

推奨:
  □ 2台目のESP32（デスク用テスト、バックアップ）
  □ ブレッドボードで事前配線確認
  □ 詳細なログ出力（問題箇所の特定を早める）
```

---

## 🎯 **このフェーズの目的**

```
仕組みの理解 > 自動化

まず手動でデプロイして:
  1. 何が起きているか理解する
  2. エラーに遭遇して対処する
  3. ログの見方を覚える
  4. トラブルシュートできるようになる

所要時間: 1-2日
```

---

## 📚 **全体フロー**

```
1. Pub/Sub トピック作成
   ↓
2. BigQuery データセット・テーブル作成
   ↓
3. Cloud Functions デプロイ
   ↓
4. ESP32 セットアップ
   ↓
5. データフロー確認
   ↓
6. 24時間稼働テスト
```

---

## 🚀 **ステップ1: Pub/Sub トピック作成**

### **1-1. トピック作成**

```bash
# Cursorのターミナルで

# Dev環境で作業
gcloud config set project aquapulse-dev-XXXXXX

# トピック作成
gcloud pubsub topics create sensor-data

# 確認
gcloud pubsub topics list

# 出力例:
# name: projects/aquapulse-dev-XXXXXX/topics/sensor-data
```

### **1-2. テストメッセージ送信**

```bash
# メッセージ送信（テスト）
gcloud pubsub topics publish sensor-data \
  --message='{"sensor_id":"test","value":25.3}'

# 出力:
# messageIds:
# - '1234567890'

# サブスクリプション作成（テスト用）
gcloud pubsub subscriptions create sensor-data-test \
  --topic=sensor-data

# メッセージ受信
gcloud pubsub subscriptions pull sensor-data-test --auto-ack

# 出力:
# ┌───────────────────────────────┬────────────┬──────────────┐
# │ DATA                          │ MESSAGE_ID │ PUBLISH_TIME │
# ├───────────────────────────────┼────────────┼──────────────┤
# │ {"sensor_id":"test",...}      │ 1234567890 │ ...          │
# └───────────────────────────────┴────────────┴──────────────┘

# テスト用サブスクリプション削除
gcloud pubsub subscriptions delete sensor-data-test
```

---

## 💾 **ステップ2: BigQuery セットアップ**

### **2-1. データセット作成**

```bash
# データセット作成
bq mk --location=asia-northeast1 aquapulse

# 確認
bq ls

# 出力:
#   datasetId  
#  ------------
#   aquapulse  
```

### **2-2. テーブル作成**

```bash
# スキーマファイル作成
mkdir -p sql
cat > sql/schema.sql << 'EOF'
CREATE TABLE IF NOT EXISTS `aquapulse.raw.sensor_readings` (
  time TIMESTAMP NOT NULL,
  sensor_id STRING NOT NULL,
  metric STRING NOT NULL,
  value FLOAT64,
  unit STRING,
  source STRING
)
PARTITION BY DATE(time)
CLUSTER BY sensor_id;
EOF

# データセット「raw」作成
bq mk aquapulse.raw

# テーブル作成
bq query --use_legacy_sql=false < sql/schema.sql

# 確認
bq ls aquapulse.raw

# 出力:
#       tableId       
#  --------------------
#   sensor_readings   

# スキーマ確認
bq show --schema aquapulse.raw.sensor_readings

# 出力: JSON形式のスキーマ
```

### **2-3. テストデータ挿入**

```bash
# テストデータ挿入
bq query --use_legacy_sql=false "
INSERT INTO aquapulse.raw.sensor_readings 
VALUES 
  (CURRENT_TIMESTAMP(), 'test_sensor', 'temperature', 25.3, 'celsius', 'test')
"

# 確認
bq query --use_legacy_sql=false "
SELECT * FROM aquapulse.raw.sensor_readings
"

# 出力:
# +---------------------+-------------+-------------+-------+---------+--------+
# | time                | sensor_id   | metric      | value | unit    | source |
# +---------------------+-------------+-------------+-------+---------+--------+
# | 2026-07-03 08:00:00 | test_sensor | temperature |  25.3 | celsius | test   |
# +---------------------+-------------+-------------+-------+---------+--------+
```

---

## ☁️ **ステップ3: Cloud Functions 作成**

### **3-1. コードディレクトリ作成**

```bash
# プロジェクトルート
cd /workspace/aquapulse

# Cloud Functionsディレクトリ作成
mkdir -p cloud-functions/ingest
cd cloud-functions/ingest
```

### **3-2. main.py 作成**

```bash
cat > main.py << 'EOF'
import base64
import json
from google.cloud import bigquery
from datetime import datetime

client = bigquery.Client()
table_id = "aquapulse.raw.sensor_readings"

def ingest_sensor_data(event, context):
    """
    Pub/Sub triggered function
    ESP32からのセンサーデータをBigQueryに保存
    """
    try:
        # Pub/Subメッセージをデコード
        pubsub_message = base64.b64decode(event['data']).decode('utf-8')
        data = json.loads(pubsub_message)
        
        print(f"Received: {data}")
        
        # タイムスタンプ処理
        timestamp = data.get('timestamp')
        if timestamp:
            time_str = datetime.fromtimestamp(timestamp).isoformat()
        else:
            time_str = datetime.utcnow().isoformat()
        
        # BigQueryに挿入
        row = {
            "time": time_str,
            "sensor_id": data["sensor_id"],
            "metric": data["metric"],
            "value": float(data["value"]),
            "unit": data.get("unit"),
            "source": "esp32"
        }
        
        errors = client.insert_rows_json(table_id, [row])
        
        if errors:
            print(f"BigQuery insert errors: {errors}")
            return f"Error: {errors}", 500
        else:
            print(f"Inserted: {row['sensor_id']} = {row['value']}")
            return "OK", 200
            
    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {e}", 500
EOF
```

### **3-3. requirements.txt 作成**

```bash
cat > requirements.txt << 'EOF'
google-cloud-bigquery==3.11.0
EOF
```

### **3-4. デプロイ**

```bash
# Dev環境確認
gcloud config get-value project
# 出力: aquapulse-dev-XXXXXX

# デプロイ
gcloud functions deploy ingest-sensor-data \
  --runtime python39 \
  --trigger-topic sensor-data \
  --entry-point ingest_sensor_data \
  --region asia-northeast1 \
  --memory 256MB \
  --timeout 60s

# 進行状況が表示される...
# Deploying function (may take a while - up to 2 minutes)...
# ...
# availableMemoryMb: 256
# buildId: ...
# entryPoint: ingest_sensor_data
# ...
# status: ACTIVE

# デプロイ完了！
```

### **3-5. デプロイ確認**

```bash
# Cloud Functions 一覧
gcloud functions list

# 出力:
# NAME                  STATUS  TRIGGER       REGION
# ingest-sensor-data    ACTIVE  Event Trigger asia-northeast1

# 詳細確認
gcloud functions describe ingest-sensor-data \
  --region asia-northeast1
```

---

## 🧪 **ステップ4: 動作確認**

### **4-1. テストメッセージ送信**

```bash
# Pub/Subにメッセージ送信
gcloud pubsub topics publish sensor-data \
  --message='{"sensor_id":"test_esp32","metric":"temperature","value":25.3,"unit":"celsius"}'

# メッセージID返却
# messageIds:
# - '1234567890'
```

### **4-2. Cloud Functionsログ確認**

```bash
# ログ確認（リアルタイム）
gcloud functions logs read ingest-sensor-data \
  --region asia-northeast1 \
  --limit 10

# 出力例:
# LEVEL  NAME                  EXECUTION_ID  TIME_UTC    LOG
# I      ingest-sensor-data    xyz123        08:00:01    Function execution started
# I      ingest-sensor-data    xyz123        08:00:01    Received: {'sensor_id': 'test_esp32', ...}
# I      ingest-sensor-data    xyz123        08:00:02    Inserted: test_esp32 = 25.3
# I      ingest-sensor-data    xyz123        08:00:02    Function execution took 1234 ms
```

### **4-3. BigQuery確認**

```bash
# データ確認
bq query --use_legacy_sql=false "
SELECT * 
FROM aquapulse.raw.sensor_readings 
WHERE source = 'esp32'
ORDER BY time DESC 
LIMIT 5
"

# 出力:
# +---------------------+-------------+-------------+-------+---------+--------+
# | time                | sensor_id   | metric      | value | unit    | source |
# +---------------------+-------------+-------------+-------+---------+--------+
# | 2026-07-03 08:00:01 | test_esp32  | temperature |  25.3 | celsius | esp32  |
# +---------------------+-------------+-------------+-------+---------+--------+

# 成功！データが入っている🎉
```

---

## 🔌 **ステップ5: ESP32セットアップ**

### **5-1. MicroPythonファームウェア書き込み**

```bash
# esptoolインストール
pip3 install esptool

# ESP32をUSB接続

# ポート確認（Mac）
ls /dev/cu.usbserial*
# 出力: /dev/cu.usbserial-0001

# ポート確認（Linux）
ls /dev/ttyUSB*
# 出力: /dev/ttyUSB0

# フラッシュ消去
esptool.py --chip esp32 --port /dev/cu.usbserial-0001 erase_flash

# MicroPythonダウンロード
cd ~/Downloads
curl -O https://micropython.org/resources/firmware/esp32-20231005-v1.21.0.bin

# ファームウェア書き込み
esptool.py --chip esp32 --port /dev/cu.usbserial-0001 \
  write_flash -z 0x1000 esp32-20231005-v1.21.0.bin

# 完了！
```

### **5-2. ampyインストール**

```bash
# ampyインストール（ファイル転送用）
pip3 install adafruit-ampy
```

### **5-3. ESP32コード作成**

```bash
# プロジェクトルート
cd /workspace/aquapulse

# ESP32ディレクトリ作成
mkdir -p esp32
cd esp32
```

```python
# config.py 作成
cat > config.py << 'EOF'
# WiFi設定
WIFI_SSID = "your-wifi-ssid"
WIFI_PASSWORD = "your-wifi-password"

# MQTT設定（GCP Pub/Sub）
# ※ Phase 1では直接HTTPで送信（簡易版）
GCP_PROJECT = "aquapulse-dev-XXXXXX"
GCP_REGION = "asia-northeast1"
FUNCTION_NAME = "ingest-sensor-data"

# センサー設定
DS18B20_PIN = 4
MCP3424_SDA_PIN = 21
MCP3424_SCL_PIN = 22
SAMPLE_INTERVAL = 60  # 秒
EOF
```

```python
# main.py 作成
cat > main.py << 'EOF'
import network
import time
import ujson
import urequests
from machine import Pin, I2C
import onewire, ds18x20
from config import *

# WiFi接続
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        timeout = 20
        while not wlan.isconnected() and timeout > 0:
            print('.', end='')
            time.sleep(1)
            timeout -= 1
        
        if wlan.isconnected():
            print('\nConnected:', wlan.ifconfig())
        else:
            print('\nFailed to connect')
            return False
    
    return True

# センサー初期化
def init_sensors():
    # DS18B20
    ds_pin = Pin(DS18B20_PIN)
    ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
    ds_roms = ds_sensor.scan()
    print(f'DS18B20 found: {len(ds_roms)} devices')
    
    # MCP3424
    i2c = I2C(0, scl=Pin(MCP3424_SCL_PIN), sda=Pin(MCP3424_SDA_PIN))
    devices = i2c.scan()
    print(f'I2C devices: {[hex(d) for d in devices]}')
    
    return ds_sensor, ds_roms, i2c

# データ送信
def send_data(sensor_id, metric, value, unit=None):
    url = f"https://{GCP_REGION}-{GCP_PROJECT}.cloudfunctions.net/{FUNCTION_NAME}"
    
    payload = {
        "sensor_id": sensor_id,
        "metric": metric,
        "value": value,
        "timestamp": time.time()
    }
    if unit:
        payload["unit"] = unit
    
    try:
        # Pub/Sub形式にエンコード
        import ubinascii
        message = ujson.dumps(payload)
        encoded = ubinascii.b2a_base64(message.encode()).decode().strip()
        
        # Cloud Functionsに送信（HTTPトリガー版）
        response = urequests.post(
            url,
            json={"data": encoded},
            headers={"Content-Type": "application/json"}
        )
        
        print(f'Sent: {sensor_id}={value} (status: {response.status_code})')
        response.close()
        
    except Exception as e:
        print(f'Send error: {e}')

# メインループ
def main():
    print('=== AquaPulse ESP32 Starting ===')
    
    # WiFi接続
    if not connect_wifi():
        print('ERROR: WiFi connection failed')
        return
    
    # センサー初期化
    ds_sensor, ds_roms, i2c = init_sensors()
    
    # メインループ
    while True:
        try:
            print(f'\n[{time.localtime()}] Reading sensors...')
            
            # 水温（DS18B20）
            ds_sensor.convert_temp()
            time.sleep_ms(750)
            
            for i, rom in enumerate(ds_roms):
                temp = ds_sensor.read_temp(rom)
                print(f'  Water temp: {temp}°C')
                send_data(f'ds18b20_water_{i}', 'temperature', temp, 'celsius')
            
            # TDS（MCP3424）
            # ※ 実装は省略、同様の流れ
            
            print(f'Sleeping {SAMPLE_INTERVAL}s...')
            time.sleep(SAMPLE_INTERVAL)
            
        except Exception as e:
            print(f'Error: {e}')
            time.sleep(10)

if __name__ == '__main__':
    main()
EOF
```

### **5-4. ESP32にアップロード**

```bash
# ポート設定（環境変数）
export AMPY_PORT=/dev/cu.usbserial-0001

# config.py アップロード
ampy put config.py

# main.py アップロード
ampy put main.py

# 確認
ampy ls
# 出力:
# /config.py
# /main.py

# 実行（シリアルモニタで確認）
screen /dev/cu.usbserial-0001 115200

# ESP32リセット（ENボタン or 再接続）
# 出力:
# === AquaPulse ESP32 Starting ===
# Connecting to WiFi...
# Connected: ('192.168.x.x', '255.255.255.0', '192.168.x.1', '8.8.8.8')
# DS18B20 found: 1 devices
# I2C devices: ['0x68']
# 
# [...] Reading sensors...
#   Water temp: 25.3°C
#   Sent: ds18b20_water_0=25.3 (status: 200)
# Sleeping 60s...

# Ctrl+A → K で終了
```

---

## ✅ **ステップ6: 統合テスト**

### **6-1. データフロー確認**

```bash
# 別ターミナルで監視

# Cloud Functionsログ
watch -n 5 "gcloud functions logs read ingest-sensor-data --limit 3"

# BigQuery最新データ
watch -n 10 "bq query --use_legacy_sql=false \"SELECT * FROM aquapulse.raw.sensor_readings WHERE source='esp32' ORDER BY time DESC LIMIT 3\""
```

### **6-2. 24時間稼働テスト**

```
⚠️  重要: ラズパイが動いていないため、比較対象なし
    → データの妥当性は「想定値」「過去の記憶」で判断

目標:
  - データ欠損率 < 1%
  - エラー率 < 0.1%
  - 平均遅延 < 5秒
  - センサー値が妥当（水温20-28℃、TDS 100-300ppm等）

確認:
  翌日、データが連続して入っているか確認

$ bq query --use_legacy_sql=false "
  SELECT 
    DATE(time) as date,
    COUNT(*) as count,
    MIN(time) as first,
    MAX(time) as last
  FROM aquapulse.raw.sensor_readings
  WHERE source = 'esp32'
  GROUP BY date
  ORDER BY date
"

# 出力:
# +------------+-------+---------------------+---------------------+
# | date       | count | first               | last                |
# +------------+-------+---------------------+---------------------+
# | 2026-07-03 |  1440 | 2026-07-03 00:00:01 | 2026-07-03 23:59:01 |
# +------------+-------+---------------------+---------------------+

# 1440 = 24時間 × 60分 → 完璧！

# センサー値の妥当性確認
$ bq query --use_legacy_sql=false "
  SELECT 
    sensor_id,
    AVG(value) as avg,
    MIN(value) as min,
    MAX(value) as max,
    STDDEV(value) as stddev
  FROM aquapulse.raw.sensor_readings
  WHERE source = 'esp32'
  GROUP BY sensor_id
"

# 期待値（例）:
# - 水温: 24-26℃（季節・室温に依存）
# - TDS: 150-250ppm（最近の換水状況に依存）
#
# 異常値なら配線やセンサーを再確認
```

---

## 🎓 **学習ポイント**

### **理解できたこと（チェック）**

- [ ] Pub/Subの役割（バッファリング）
- [ ] Cloud Functionsの仕組み（イベントトリガー）
- [ ] BigQueryのスキーマ設計
- [ ] ESP32からのデータ送信
- [ ] gcloud CLIの使い方
- [ ] ログの見方・デバッグ方法

### **次のステップ**

```
Phase 1完了 🎉

次は自動化:
  - GitHub Actions設定
  - Dev/Prod環境分離
  - Terraform導入

→ 04_PHASE2_AUTOMATION.md
```

---

## 📋 **Phase 1完了チェックリスト**

- [ ] Pub/Subトピック作成
- [ ] BigQueryテーブル作成
- [ ] Cloud Functionsデプロイ
- [ ] テストメッセージ送信成功
- [ ] ESP32ファームウェア書き込み
- [ ] ESP32コードアップロード
- [ ] WiFi接続成功
- [ ] センサーデータ送信成功
- [ ] BigQueryにデータ保存確認
- [ ] 24時間稼働テスト成功

**完了したら、Phase 2へ！** 🚀
