# Grafana Cloud + BigQuery Datasource セットアップ

**日時**: 2026-08-03  
**目的**: Phase 1a監視システム — BigQueryデータをGrafana Cloudで可視化

---

## Step 1: GCP Service Account作成（5分）

### 1-1. Cloud Consoleでサービスアカウント作成

1. **GCP Console > IAM と管理 > サービスアカウント**  
   https://console.cloud.google.com/iam-admin/serviceaccounts?project=aquapulse-dev

2. **「+ サービスアカウントを作成」**

3. **サービスアカウントの詳細**:
   - 名前: `grafana-bigquery-reader`
   - ID: `grafana-bigquery-reader@aquapulse-dev.iam.gserviceaccount.com`
   - 説明: `Grafana Cloud read-only access to BigQuery sensor_readings`
   - **作成して続行**

4. **ロール付与**（2つ追加）:
   - ロール1: `BigQuery データ閲覧者` (BigQuery Data Viewer)
   - ロール2: `BigQuery ジョブユーザー` (BigQuery Job User)
   - **続行** → **完了**

### 1-2. JSONキー作成

1. 作成したサービスアカウント行の **︙（縦3点）** → **鍵を管理**

2. **鍵を追加** → **新しい鍵を作成**

3. **キーのタイプ**: `JSON` → **作成**

4. JSONファイルが自動ダウンロードされる:
   - ファイル名: `aquapulse-dev-xxxxxxxxxxxx.json`
   - **保存場所を覚えておく**（次のStepで使用）

**⚠️ 注意**: このJSONキーは**GCP全権限**ではなく、BigQuery読み取り専用です。

---

## Step 2: Grafana Cloudアカウント作成（5分）

### 2-1. アカウント作成

1. **Grafana Cloud サインアップ**  
   https://grafana.com/auth/sign-up/create-user

2. **Free Tier** を選択（月間10,000シリーズ無料）

3. 必要情報を入力:
   - Email
   - Username
   - Organization name: `aquapulse`（または任意）

4. メール認証を完了

### 2-2. Stack作成

1. ログイン後、**Create a stack** または **Launch**

2. Stack URL: `https://あなたのorg名.grafana.net`（後で使用）

3. **Go to instance** でダッシュボードにアクセス

---

## Step 3: BigQuery Datasource設定（10-15分）

### 3-1. BigQueryプラグイン確認

1. Grafana画面左メニュー: **☰ (ハンバーガー) > Connections > Data sources**

2. **Add new data source**

3. 検索欄に `BigQuery` と入力 → **Google BigQuery** を選択

### 3-2. Datasource設定

#### Authentication

- **Authentication Type**: `Google JWT File`
- **Upload JWT File**: Step 1-2でダウンロードしたJSONキーをアップロード

#### Settings

- **Default Project**: `aquapulse-dev`
- **Processing Location**: `asia-northeast1`（Tokyo）

**Save & Test** → ✅ "Data source is working" が表示されればOK

---

## Step 4: 接続テスト（5分）

### 4-1. Exploreでクエリ実行

1. Grafana画面左メニュー: **☰ > Explore**

2. Datasource: `Google BigQuery` を選択

3. **Query editor**（SQLモード）:

```sql
SELECT
  TIMESTAMP_TRUNC(timestamp, MINUTE) AS time,
  sensor_id,
  sensor_type,
  value,
  unit
FROM `aquapulse-dev.aquapulse.sensor_readings`
WHERE device_id = 'mac_poller_v1'
  AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 3 HOUR)
ORDER BY timestamp DESC
LIMIT 100
```

4. **Run query** → データが表示されればOK

### 4-2. 確認項目

- ✅ `sensor_id`: `tapo_xxxxxxxxx`
- ✅ `sensor_type`: `room_temperature`, `room_humidity`, `power_state`
- ✅ `value`: 温度（25-30°C）、湿度（50-80%）、電源状態（0/1）

---

## Step 5: ダッシュボード作成（次のステップ）

このステップは別途実施します（`grafana-dashboard-setup.md`参照予定）。

---

## トラブルシューティング

### BigQuery接続エラー

| エラー | 原因 | 対処 |
|--------|------|------|
| `Permission denied` | サービスアカウント権限不足 | Step 1-1のロール付与を再確認 |
| `Dataset not found` | プロジェクトID誤り | `aquapulse-dev`を確認 |
| `Invalid JWT` | JSONキーが古い/誤り | Step 1-2でキー再作成 |

### Grafana Cloudログインできない

- メール認証を完了していない → 受信箱確認
- パスワードリセット: https://grafana.com/auth/reset-password

---

## 次のステップ

- [ ] Step 1-2: JSONキーをダウンロード
- [ ] Step 2: Grafana Cloudアカウント作成
- [ ] Step 3: BigQuery datasource設定
- [ ] Step 4: 接続テスト実行

完了したら、次は**ダッシュボード作成**（室温/湿度/ファン状態パネル）に進みます。

---

**作成日**: 2026-08-03  
**Phase 1a Priority**: P1（Critical Path）
