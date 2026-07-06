# 🤖 Phase 2: 自動化（GitHub Actions）

**git push だけでデプロイできるようにする**

---

## 🎯 **このフェーズの目的**

```
Phase 1:
  gcloud functions deploy ...  ← 毎回手動（面倒）

Phase 2:
  git push  ← これだけ！（自動デプロイ）

所要時間: 1-2日
```

---

## 📊 **全体フロー**

```
Cursor（ローカル）
  ↓ git push origin dev
GitHub Actions（自動実行）
  ↓
Dev環境にデプロイ
  ↓ テスト成功
  ↓ git push origin main
GitHub Actions（自動実行）
  ↓
Prod環境にデプロイ
```

---

## 🌿 **ステップ1: ブランチ戦略**

### **1-1. ブランチ作成**

```bash
# Cursorのターミナルで

cd /workspace/aquapulse

# mainブランチ確認
git branch
# 出力: * main

# devブランチ作成
git checkout -b dev

# 確認
git branch
# 出力:
#   main
# * dev
```

### **1-2. .gitignoreに追加**

```.gitignore
# 既存の .gitignore に追加

# GCP認証
.config/gcloud/
credentials.json

# Terraform
terraform/.terraform/
terraform/*.tfstate
terraform/*.tfstate.backup

# ESP32
esp32/config.py  # WiFiパスワード含むため
```

---

## 🔐 **ステップ2: GCP認証設定**

### **2-1. サービスアカウント作成**

```bash
# Dev環境
gcloud config set project aquapulse-dev-XXXXXX

# サービスアカウント作成
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions"

# 権限付与
gcloud projects add-iam-policy-binding aquapulse-dev-XXXXXX \
  --member="serviceAccount:github-actions@aquapulse-dev-XXXXXX.iam.gserviceaccount.com" \
  --role="roles/cloudfunctions.developer"

gcloud projects add-iam-policy-binding aquapulse-dev-XXXXXX \
  --member="serviceAccount:github-actions@aquapulse-dev-XXXXXX.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding aquapulse-dev-XXXXXX \
  --member="serviceAccount:github-actions@aquapulse-dev-XXXXXX.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"

# 鍵ファイル生成
gcloud iam service-accounts keys create ~/gcp-key-dev.json \
  --iam-account=github-actions@aquapulse-dev-XXXXXX.iam.gserviceaccount.com

# Prod環境も同様に
gcloud config set project aquapulse-prod-XXXXXX

gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions"

# 権限付与（同様）
gcloud projects add-iam-policy-binding aquapulse-prod-XXXXXX \
  --member="serviceAccount:github-actions@aquapulse-prod-XXXXXX.iam.gserviceaccount.com" \
  --role="roles/cloudfunctions.developer"

gcloud projects add-iam-policy-binding aquapulse-prod-XXXXXX \
  --member="serviceAccount:github-actions@aquapulse-prod-XXXXXX.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding aquapulse-prod-XXXXXX \
  --member="serviceAccount:github-actions@aquapulse-prod-XXXXXX.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"

# 鍵ファイル生成
gcloud iam service-accounts keys create ~/gcp-key-prod.json \
  --iam-account=github-actions@aquapulse-prod-XXXXXX.iam.gserviceaccount.com
```

### **2-2. GitHubシークレット登録**

```bash
# GitHub CLIで登録

# Dev環境
gh secret set GCP_SA_KEY_DEV < ~/gcp-key-dev.json
gh secret set GCP_PROJECT_ID_DEV --body "aquapulse-dev-XXXXXX"

# Prod環境
gh secret set GCP_SA_KEY_PROD < ~/gcp-key-prod.json
gh secret set GCP_PROJECT_ID_PROD --body "aquapulse-prod-XXXXXX"

# 確認
gh secret list

# 出力:
# GCP_SA_KEY_DEV       Updated 2026-07-03
# GCP_PROJECT_ID_DEV   Updated 2026-07-03
# GCP_SA_KEY_PROD      Updated 2026-07-03
# GCP_PROJECT_ID_PROD  Updated 2026-07-03

# 鍵ファイル削除（重要！）
rm ~/gcp-key-dev.json ~/gcp-key-prod.json
```

---

## 🤖 **ステップ3: GitHub Actions設定**

### **3-1. ワークフローファイル作成**

```bash
# ディレクトリ作成
mkdir -p .github/workflows
```

### **3-2. deploy.yml 作成**

```yaml
# .github/workflows/deploy.yml

name: Deploy to GCP

on:
  push:
    branches:
      - dev   # devブランチ → Dev環境
      - main  # mainブランチ → Prod環境

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      # 1. コードチェックアウト
      - name: Checkout code
        uses: actions/checkout@v3
      
      # 2. 環境判定
      - name: Set environment
        id: set-env
        run: |
          if [ "${{ github.ref }}" == "refs/heads/main" ]; then
            echo "env=prod" >> $GITHUB_OUTPUT
            echo "project_id=${{ secrets.GCP_PROJECT_ID_PROD }}" >> $GITHUB_OUTPUT
            echo "sa_key=${{ secrets.GCP_SA_KEY_PROD }}" >> $GITHUB_OUTPUT
          else
            echo "env=dev" >> $GITHUB_OUTPUT
            echo "project_id=${{ secrets.GCP_PROJECT_ID_DEV }}" >> $GITHUB_OUTPUT
            echo "sa_key=${{ secrets.GCP_SA_KEY_DEV }}" >> $GITHUB_OUTPUT
          fi
      
      # 3. GCP認証
      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ steps.set-env.outputs.sa_key }}
      
      # 4. gcloud CLI セットアップ
      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
      
      # 5. プロジェクト設定
      - name: Set GCP project
        run: |
          gcloud config set project ${{ steps.set-env.outputs.project_id }}
          echo "Deploying to: ${{ steps.set-env.outputs.env }}"
      
      # 6. Cloud Functions デプロイ
      - name: Deploy Cloud Function (ingest)
        run: |
          gcloud functions deploy ingest-sensor-data \
            --runtime python39 \
            --trigger-topic sensor-data \
            --entry-point ingest_sensor_data \
            --region asia-northeast1 \
            --memory 256MB \
            --timeout 60s \
            --source cloud-functions/ingest
      
      # 7. デプロイ成功通知
      - name: Deployment success
        run: |
          echo "✅ Deployment to ${{ steps.set-env.outputs.env }} completed!"
```

---

## 📤 **ステップ4: 初回デプロイ**

### **4-1. コミット・プッシュ（Dev）**

```bash
# devブランチ確認
git branch
# 出力: * dev

# 変更を追加
git add .github/workflows/deploy.yml
git add cloud-functions/
git add .gitignore

# コミット
git commit -m "feat: add GitHub Actions for auto-deployment"

# プッシュ（Dev環境へ）
git push origin dev
```

### **4-2. GitHub Actionsの確認**

```bash
# ブラウザでGitHubを開く
# または、CLI で確認

# ワークフロー実行確認
gh run list

# 出力:
# ✓  Deploy to GCP  feat: add GitHub Actions...  dev  1234567  1m ago

# 詳細ログ
gh run view 1234567 --log

# 出力:
# deploy
#   Checkout code              ✓
#   Set environment            ✓ env=dev
#   Authenticate to GCP        ✓
#   Set up Cloud SDK           ✓
#   Set GCP project            ✓ Deploying to: dev
#   Deploy Cloud Function      ✓ 
#     Deploying function...
#     ...
#     Done.
#   Deployment success         ✓ ✅ Deployment to dev completed!
```

---

## 🧪 **ステップ5: Dev環境テスト**

### **5-1. 動作確認**

```bash
# Dev環境に切り替え
gcloud config set project aquapulse-dev-XXXXXX

# テストメッセージ送信
gcloud pubsub topics publish sensor-data \
  --message='{"sensor_id":"github_actions_test","metric":"temperature","value":99.9,"unit":"celsius"}'

# ログ確認
gcloud functions logs read ingest-sensor-data --limit 5

# BigQuery確認
bq query --use_legacy_sql=false "
  SELECT * 
  FROM aquapulse.raw.sensor_readings 
  WHERE sensor_id = 'github_actions_test'
"

# 出力:
# +---------------------+---------------------+-------------+-------+---------+--------+
# | time                | sensor_id           | metric      | value | unit    | source |
# +---------------------+---------------------+-------------+-------+---------+--------+
# | 2026-07-03 09:00:00 | github_actions_test | temperature |  99.9 | celsius | esp32  |
# +---------------------+---------------------+-------------+-------+---------+--------+

# 成功！🎉
```

---

## 🚀 **ステップ6: Prod環境デプロイ**

### **6-1. mainにマージ**

```bash
# mainブランチに切り替え
git checkout main

# devをマージ
git merge dev

# コンフリクトがなければそのまま
# コンフリクトがあれば解消

# プッシュ（Prod環境へ）
git push origin main
```

### **6-2. デプロイ確認**

```bash
# GitHub Actions確認
gh run list

# 出力:
# ✓  Deploy to GCP  Merge branch 'dev'  main  7654321  30s ago

# ログ確認
gh run view 7654321 --log

# 出力:
# ...
# Set GCP project  ✓ Deploying to: prod
# ...
# ✅ Deployment to prod completed!
```

### **6-3. Prod環境動作確認**

```bash
# Prod環境に切り替え
gcloud config set project aquapulse-prod-XXXXXX

# テスト
gcloud pubsub topics publish sensor-data \
  --message='{"sensor_id":"prod_test","metric":"temperature","value":25.3,"unit":"celsius"}'

# 確認
bq query --use_legacy_sql=false "
  SELECT * FROM aquapulse.raw.sensor_readings 
  WHERE sensor_id = 'prod_test'
"

# 成功！Prod環境も動作🎉
```

---

## 🔄 **ステップ7: 日常の開発フロー**

### **7-1. 機能追加・修正**

```bash
# devブランチで作業
git checkout dev

# コード編集
code cloud-functions/ingest/main.py

# 例: ログ追加
# print(f"Processing: {data}")

# コミット
git add cloud-functions/ingest/main.py
git commit -m "feat: add debug logging"

# プッシュ（自動デプロイ）
git push origin dev

# GitHub Actionsが自動実行
# Dev環境にデプロイされる
```

### **7-2. テスト**

```bash
# Dev環境で確認
gcloud config set project aquapulse-dev-XXXXXX
gcloud functions logs read ingest-sensor-data --limit 10

# ログに "Processing: ..." が表示されることを確認

# OK なら本番へ
```

### **7-3. 本番リリース**

```bash
# mainにマージ
git checkout main
git merge dev
git push origin main

# GitHub Actionsが自動実行
# Prod環境にデプロイされる

# 完了！
```

---

## 🛡️ **ステップ8: ロールバック**

### **8-1. 問題発生時**

```
状況: mainにプッシュしたら本番でエラー

対策: 前のコミットに戻す
```

```bash
# Git履歴確認
git log --oneline -5

# 出力:
# abc1234 (HEAD -> main) feat: new feature (← 問題のコミット)
# def5678 fix: bug fix
# ghi9012 feat: add logging

# 1つ前に戻す
git revert abc1234

# プッシュ（自動で前の状態にデプロイされる）
git push origin main

# または、強制的に戻す（緊急時）
git reset --hard def5678
git push -f origin main
```

### **8-2. 手動ロールバック**

```bash
# Cloud Functionsの前のバージョンを確認
gcloud functions describe ingest-sensor-data \
  --region asia-northeast1 \
  --format="value(versionId)"

# 出力: 5（現在のバージョン）

# 前のバージョン（4）にロールバック
# ※ gcloud CLIではバージョン指定デプロイ非対応
# → GCPコンソールから手動でロールバック

# または、前のコミットから再デプロイ
git checkout def5678
gcloud functions deploy ingest-sensor-data ...
git checkout main
```

---

## 🎓 **ステップ9: Terraform導入（オプション）**

### **9-1. Terraformインストール**

```bash
# Mac
brew install terraform

# 確認
terraform version
# 出力: Terraform v1.6.0
```

### **9-2. Terraformファイル作成**

```bash
mkdir -p terraform
cd terraform
```

```hcl
# terraform/main.tf

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "asia-northeast1"
}
```

```hcl
# terraform/bigquery.tf

resource "google_bigquery_dataset" "raw" {
  dataset_id = "raw"
  location   = var.region
}

resource "google_bigquery_table" "sensor_readings" {
  dataset_id = google_bigquery_dataset.raw.dataset_id
  table_id   = "sensor_readings"
  
  time_partitioning {
    type  = "DAY"
    field = "time"
  }
  
  clustering = ["sensor_id"]
  
  schema = jsonencode([
    { name = "time", type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "sensor_id", type = "STRING", mode = "REQUIRED" },
    { name = "metric", type = "STRING", mode = "REQUIRED" },
    { name = "value", type = "FLOAT", mode = "NULLABLE" },
    { name = "unit", type = "STRING", mode = "NULLABLE" },
    { name = "source", type = "STRING", mode = "NULLABLE" }
  ])
}
```

```hcl
# terraform/pubsub.tf

resource "google_pubsub_topic" "sensor_data" {
  name = "sensor-data"
}
```

### **9-3. Terraform実行**

```bash
# 初期化
terraform init

# ドライラン
terraform plan -var="project_id=aquapulse-dev-XXXXXX"

# 適用
terraform apply -var="project_id=aquapulse-dev-XXXXXX"

# 出力:
# Plan: 3 to add, 0 to change, 0 to destroy.
# ...
# Apply complete! Resources: 3 added, 0 changed, 0 destroyed.
```

---

## ✅ **Phase 2完了チェックリスト**

### **GitHub Actions**
- [ ] サービスアカウント作成
- [ ] GitHubシークレット登録
- [ ] ワークフローファイル作成
- [ ] devブランチ push → Dev環境デプロイ成功
- [ ] mainブランチ push → Prod環境デプロイ成功

### **開発フロー**
- [ ] 機能追加 → dev push → 自動デプロイ確認
- [ ] テスト → main merge → 本番デプロイ確認
- [ ] ロールバック手順確認

### **オプション**
- [ ] Terraform導入
- [ ] IaCでインフラ管理

---

## 🎉 **Phase 2完了！**

```
これで:
  ✅ git push だけでデプロイ
  ✅ Dev/Prod環境分離
  ✅ 自動テスト可能
  ✅ ロールバック可能

次のステップ:
  - Grafana Cloud接続
  - モニタリング設定
  - 本番運用開始

→ 06_OPERATIONS.md
```

---

**次のステップ:** [06_OPERATIONS.md](06_OPERATIONS.md) で運用を始めよう！
