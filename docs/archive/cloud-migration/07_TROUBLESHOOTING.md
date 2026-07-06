# 🔍 トラブルシューティング

**よくある問題と解決策**

---

## 📋 **問題の切り分けフローチャート**

```
問題発生
  ↓
データが来ない？
  YES → セクション1へ
  NO  ↓
エラーログがある？
  YES → セクション2へ
  NO  ↓
パフォーマンス問題？
  YES → セクション3へ
  NO  ↓
その他 → セクション4へ
```

---

## 1️⃣ **データが来ない**

### **症状: BigQueryにデータが入らない**

#### **原因1: ESP32がWiFiに接続できていない**

```
確認:
  ESP32のシリアルモニタを見る
  
screen /dev/cu.usbserial-0001 115200

期待される出力:
  Connecting to WiFi...
  Connected: (192.168.x.x, ...)

エラー例:
  Failed to connect

対策:
  1. WiFi SSID/パスワード確認（config.py）
  2. WiFiルーターの電波強度確認
  3. ESP32をルーターに近づける
  4. 2.4GHz WiFiを使用（5GHzは非対応）
```

#### **原因2: Pub/Subにメッセージが届いていない**

```
確認:
  gcloud pubsub topics list
  gcloud pubsub subscriptions list
  
テスト:
  # テスト用サブスクリプション作成
  gcloud pubsub subscriptions create test-sub --topic=sensor-data
  
  # ESP32からデータ送信後、メッセージ確認
  gcloud pubsub subscriptions pull test-sub --auto-ack
  
  # メッセージが表示されればPub/Subまでは届いている
  
  # クリーンアップ
  gcloud pubsub subscriptions delete test-sub

対策:
  - メッセージが表示される → Cloud Functionsの問題（原因3へ）
  - メッセージが表示されない → ESP32の送信コード確認
```

#### **原因3: Cloud Functionsが動いていない**

```
確認:
  gcloud functions list --region asia-northeast1
  
  # STATUS が ACTIVE か確認
  
ログ確認:
  gcloud functions logs read ingest-sensor-data --limit 20
  
エラー例:
  "Function execution started"はあるが
  "Function execution finished"がない
  → 途中でエラー

対策:
  1. ログのエラーメッセージを確認
  2. requirements.txt の依存関係確認
  3. 再デプロイ
     gcloud functions deploy ingest-sensor-data ...
```

#### **原因4: BigQueryのテーブルが存在しない**

```
確認:
  bq ls aquapulse.raw
  
  # sensor_readings が表示されるか
  
対策:
  # テーブル作成
  bq query --use_legacy_sql=false < sql/schema.sql
```

---

## 2️⃣ **エラーログがある**

### **エラー: ImportError: No module named 'google.cloud'**

```
症状:
  Cloud Functionsのログに表示
  
原因:
  requirements.txtが正しくない
  
対策:
  # requirements.txt 確認
  cat cloud-functions/ingest/requirements.txt
  
  # 正しい内容:
  google-cloud-bigquery==3.11.0
  
  # 再デプロイ
  gcloud functions deploy ingest-sensor-data ...
```

### **エラー: Permission denied**

```
症状:
  BigQuery insert時にエラー
  
原因:
  サービスアカウントの権限不足
  
対策:
  # 権限確認
  gcloud projects get-iam-policy PROJECT_ID
  
  # 権限追加
  gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:SA_EMAIL" \
    --role="roles/bigquery.dataEditor"
```

### **エラー: Quota exceeded**

```
症状:
  Cloud Functions invocations exceeded
  
原因:
  無限ループでFunction呼び出し
  
確認:
  # 実行回数確認
  gcloud monitoring time-series list \
    --filter='metric.type="cloudfunctions.googleapis.com/function/execution_count"'
  
対策:
  1. 無限ループの原因特定
  2. 一時的にFunctionを無効化
     gcloud functions delete ingest-sensor-data
  3. 修正後、再デプロイ
```

---

## 3️⃣ **パフォーマンス問題**

### **症状: データ遅延が大きい（>10秒）**

```
確認:
  # Cloud Functionsの実行時間
  gcloud functions logs read ingest-sensor-data --limit 100 | grep "execution took"
  
期待値: 1000ms以下
  
原因と対策:
  1. BigQuery insert が遅い
     → streaming insert ではなく batch insert を検討
  
  2. ネットワーク遅延
     → リージョンを確認（asia-northeast1使用推奨）
  
  3. Cloud Functionsのコールドスタート
     → メモリ増量（256MB → 512MB）
```

### **症状: ESP32が頻繁に再起動する**

```
原因:
  1. 電源不足
  2. Watchdogタイムアウト
  3. メモリ不足
  
対策:
  1. USB電源を5V 1A以上に
  2. コードのsleep時間を確認
  3. 不要な変数を削除
```

---

## 4️⃣ **その他の問題**

### **GitHub Actionsが失敗する**

```
確認:
  gh run list
  gh run view RUN_ID --log
  
よくあるエラー:
  1. "Error: credentials.json not found"
     → GitHubシークレット未登録
     → gh secret set GCP_SA_KEY_DEV < key.json
  
  2. "Error: Permission denied"
     → サービスアカウントの権限不足
     → roles/cloudfunctions.developer 付与
  
  3. "Error: Function already exists"
     → 既存のFunctionと衝突
     → Function削除後、再デプロイ
```

### **Grafana Cloudに接続できない**

```
確認:
  1. BigQueryデータソース設定
     Project ID: aquapulse-prod-XXXXXX
     Dataset: raw
  
  2. 認証
     Service Account JSON キーをアップロード
  
  3. テストクエリ
     SELECT COUNT(*) FROM aquapulse.raw.sensor_readings
  
対策:
  - エラーメッセージを確認
  - サービスアカウントに bigquery.dataViewer 権限付与
```

---

## 🆘 **緊急時の対応**

### **システム全体がダウン**

```
1. ESP32停止
   USB抜く
   
2. Cloud Functions停止
   gcloud functions delete ingest-sensor-data
   
3. 原因調査
   - ログ確認
   - 請求確認（予算超過？）
   
4. 修正・再起動
   - コード修正
   - 再デプロイ
   - ESP32再接続
```

### **予算超過アラート**

```
確認:
  GCPコンソール → お支払い → 使用状況
  
原因:
  1. 無限ループ
  2. 意図しない大量リクエスト
  3. BigQueryの大量クエリ
  
対策:
  1. 該当サービスを停止
  2. 予算上限設定（自動停止）
     GCPコンソール → 予算とアラート
```

---

## 📊 **診断コマンド集**

### **全体ヘルスチェック**

```bash
#!/bin/bash
# health-check.sh

echo "=== AquaPulse Health Check ==="

# Pub/Sub
echo "\n[Pub/Sub]"
gcloud pubsub topics describe sensor-data

# Cloud Functions
echo "\n[Cloud Functions]"
gcloud functions describe ingest-sensor-data --region asia-northeast1

# BigQuery
echo "\n[BigQuery]"
bq query --use_legacy_sql=false "
  SELECT 
    COUNT(*) as total_records,
    MAX(time) as latest_data
  FROM aquapulse.raw.sensor_readings
  WHERE time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
"

# 最新エラー
echo "\n[Recent Errors]"
gcloud functions logs read ingest-sensor-data \
  --limit 10 \
  --filter="severity=ERROR"
```

実行:
```bash
chmod +x health-check.sh
./health-check.sh
```

---

## 📚 **参考リソース**

### **公式ドキュメント**

- [Cloud Functions トラブルシューティング](https://cloud.google.com/functions/docs/troubleshooting)
- [BigQuery エラーメッセージ](https://cloud.google.com/bigquery/docs/error-messages)
- [Pub/Sub トラブルシューティング](https://cloud.google.com/pubsub/docs/troubleshooting)

### **コミュニティ**

- [Stack Overflow - google-cloud-functions](https://stackoverflow.com/questions/tagged/google-cloud-functions)
- [GitHub Issues - AquaPulse](https://github.com/YOUR_USERNAME/aquapulse/issues)

---

## 💬 **サポート連絡先**

```
問題が解決しない場合:

1. GitHub Issue作成
   https://github.com/YOUR_USERNAME/aquapulse/issues
   
2. ログを添付
   - gcloud functions logs read ...
   - bq query ...
   - ESP32 シリアルログ
   
3. 環境情報
   - GCPプロジェクトID
   - リージョン
   - ESP32ファームウェアバージョン
```

---

**問題が解決したら、[06_OPERATIONS.md](06_OPERATIONS.md) で運用を再開しよう！**
