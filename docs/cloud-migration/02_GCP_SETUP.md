# ☁️ GCP環境構築

**プロジェクト作成からデプロイまで**

---

## 🎯 **このフェーズのゴール**

```
GCPアカウント
  ↓
プロジェクト作成
  ↓
gcloud CLI セットアップ
  ↓
必要なAPI有効化
  ↓
認証設定
  ↓
Phase 1（手動デプロイ）の準備完了
```

所要時間: 1-2時間

---

## 📝 **事前準備**

### **必要なもの**

- [ ] Googleアカウント
- [ ] クレジットカード（無料枠でも登録必須）
- [ ] ターミナル（Cursor内蔵）
- [ ] 安定したインターネット接続

### **注意事項**

```
⚠️ クレジットカード登録について

- 無料トライアル: $300分のクレジット（90日間）
- 無料枠: 毎月リセットされる無料枠あり
- 自動課金なし: 無料枠超過で止まる（設定可）

このプロジェクトでは無料枠内で完結します
```

---

## 🚀 **ステップ1: GCPアカウント作成**

### **1-1. Google Cloudにアクセス**

```
https://console.cloud.google.com/
```

### **1-2. 初回セットアップ**

```
1. Googleアカウントでログイン

2. 利用規約に同意

3. 国・通貨を選択
   国: 日本
   通貨: JPY（日本円）

4. クレジットカード登録
   ※ 無料トライアル用（自動課金なし）

5. 登録完了
   → $300分のクレジット付与
```

---

## 🏗️ **ステップ2: プロジェクト作成**

### **2-1. 本番プロジェクト作成**

```
GCPコンソール
  ↓
プロジェクトセレクタ（上部）
  ↓
「新しいプロジェクト」
  ↓
プロジェクト名: aquapulse
プロジェクトID: aquapulse-prod-XXXXXX
  ↑ 自動生成されたIDをメモ
  
「作成」をクリック
```

### **2-2. 開発プロジェクト作成（推奨）**

```
同様に:
  プロジェクト名: aquapulse-dev
  プロジェクトID: aquapulse-dev-XXXXXX
  
メモ:
  本番: aquapulse-prod-XXXXXX
  開発: aquapulse-dev-XXXXXX
```

---

## 💻 **ステップ3: gcloud CLI インストール**

### **3-1. インストール（Mac）**

```bash
# Cursorのターミナルで実行

# Homebrewでインストール
brew install google-cloud-sdk

# インストール確認
gcloud version

# 出力例:
# Google Cloud SDK 450.0.0
# bq 2.0.97
# core 2023.11.10
```

### **3-2. インストール（Linux）**

```bash
# Snap経由（Ubuntu/Debian）
sudo snap install google-cloud-sdk --classic

# または、公式スクリプト
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# 確認
gcloud version
```

### **3-3. インストール（Windows）**

```powershell
# PowerShellで実行

# インストーラーダウンロード
# https://cloud.google.com/sdk/docs/install

# または、Chocolatey
choco install gcloudsdk

# 確認
gcloud version
```

---

## 🔐 **ステップ4: 認証設定**

### **4-1. gcloud 初期化**

```bash
# Cursorのターミナルで

gcloud init

# 対話形式で進む:

# 1. ログイン選択
Choose the account you would like to use:
  [1] example@gmail.com
  [2] Log in with a new account
→ 1 を選択（または新規ログイン）

# ブラウザが開く → Googleアカウントでログイン

# 2. プロジェクト選択
Pick cloud project to use:
  [1] aquapulse-prod-XXXXXX
  [2] aquapulse-dev-XXXXXX
  [3] Create a new project
→ 1 を選択（本番プロジェクト）

# 3. デフォルトリージョン設定
Do you want to configure a default Compute Region?
→ Y

→ asia-northeast1 を選択（東京リージョン）

# 完了！
Your Google Cloud SDK is configured!
```

### **4-2. プロジェクト確認**

```bash
# 現在のプロジェクト確認
gcloud config get-value project

# 出力: aquapulse-prod-XXXXXX

# プロジェクト切り替え（Dev環境）
gcloud config set project aquapulse-dev-XXXXXX

# 再確認
gcloud config get-value project
# 出力: aquapulse-dev-XXXXXX

# 本番に戻す
gcloud config set project aquapulse-prod-XXXXXX
```

---

## 🔧 **ステップ5: 必要なAPI有効化**

### **5-1. API一括有効化**

```bash
# Cursorのターミナルで

# 本番プロジェクト
gcloud config set project aquapulse-prod-XXXXXX

# API有効化
gcloud services enable \
  pubsub.googleapis.com \
  cloudfunctions.googleapis.com \
  bigquery.googleapis.com \
  cloudscheduler.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com

# 進行状況が表示される
Operation "operations/..." finished successfully.

# 確認
gcloud services list --enabled

# 出力例:
# NAME                              TITLE
# pubsub.googleapis.com             Cloud Pub/Sub API
# cloudfunctions.googleapis.com     Cloud Functions API
# bigquery.googleapis.com           BigQuery API
# ...
```

### **5-2. Dev環境も同様に**

```bash
# Devプロジェクト
gcloud config set project aquapulse-dev-XXXXXX

# API有効化（同じコマンド）
gcloud services enable \
  pubsub.googleapis.com \
  cloudfunctions.googleapis.com \
  bigquery.googleapis.com \
  cloudscheduler.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com
```

---

## 💳 **ステップ6: 請求アカウント設定**

### **6-1. 請求アカウントリンク**

```bash
# 請求アカウント一覧
gcloud billing accounts list

# 出力例:
# ACCOUNT_ID          NAME            OPEN
# 012345-ABCDEF-67890 My Billing      True

# プロジェクトにリンク
gcloud billing projects link aquapulse-prod-XXXXXX \
  --billing-account=012345-ABCDEF-67890

gcloud billing projects link aquapulse-dev-XXXXXX \
  --billing-account=012345-ABCDEF-67890
```

### **6-2. 予算アラート設定（推奨）**

```
GCPコンソール
  ↓
「お支払い」
  ↓
「予算とアラート」
  ↓
「予算を作成」

設定:
  名前: aquapulse-budget
  プロジェクト: aquapulse-prod
  予算額: $10/月
  
  アラート:
    50%: メール通知
    100%: メール通知
```

---

## 🧪 **ステップ7: 動作確認**

### **7-1. Pub/Sub テスト**

```bash
# トピック作成
gcloud pubsub topics create test-topic

# サブスクリプション作成
gcloud pubsub subscriptions create test-sub --topic=test-topic

# メッセージ送信
gcloud pubsub topics publish test-topic --message="Hello GCP!"

# メッセージ受信
gcloud pubsub subscriptions pull test-sub --auto-ack

# 出力例:
# ┌──────────┬─────────────┬──────────────┐
# │   DATA   │ MESSAGE_ID  │ PUBLISH_TIME │
# ├──────────┼─────────────┼──────────────┤
# │ Hello... │ 1234567890  │ ...          │
# └──────────┴─────────────┴──────────────┘

# クリーンアップ
gcloud pubsub subscriptions delete test-sub
gcloud pubsub topics delete test-topic
```

### **7-2. BigQuery テスト**

```bash
# データセット作成
bq mk test_dataset

# 確認
bq ls

# 出力例:
#   datasetId    
#  --------------
#   test_dataset 

# テーブル作成
bq query --use_legacy_sql=false \
  "CREATE TABLE test_dataset.test_table (id INT64, name STRING)"

# データ挿入
bq query --use_legacy_sql=false \
  "INSERT INTO test_dataset.test_table VALUES (1, 'test')"

# データ取得
bq query --use_legacy_sql=false \
  "SELECT * FROM test_dataset.test_table"

# 出力例:
# +----+------+
# | id | name |
# +----+------+
# |  1 | test |
# +----+------+

# クリーンアップ
bq rm -f -r test_dataset
```

---

## 📋 **ステップ8: GitHub CLI セットアップ（Phase 2用）**

### **8-1. インストール**

```bash
# Mac
brew install gh

# Linux
sudo snap install gh

# Windows
choco install gh
```

### **8-2. 認証**

```bash
# GitHub認証
gh auth login

# 対話形式:
? What account do you want to log into? 
  → GitHub.com

? What is your preferred protocol for Git operations? 
  → HTTPS

? Authenticate Git with your GitHub credentials? 
  → Yes

? How would you like to authenticate GitHub CLI? 
  → Login with a web browser

# ブラウザが開く → GitHubでログイン

# 完了
✓ Logged in as YOUR_USERNAME
```

---

## ✅ **GCPセットアップ完了チェックリスト**

### **アカウント・プロジェクト**
- [ ] GCPアカウント作成
- [ ] クレジットカード登録（無料トライアル）
- [ ] 本番プロジェクト作成（aquapulse-prod）
- [ ] 開発プロジェクト作成（aquapulse-dev）
- [ ] 請求アカウントリンク

### **gcloud CLI**
- [ ] gcloud CLI インストール
- [ ] gcloud init 実行
- [ ] 認証成功
- [ ] プロジェクト切り替え確認

### **API有効化**
- [ ] Pub/Sub API
- [ ] Cloud Functions API
- [ ] BigQuery API
- [ ] Cloud Scheduler API
- [ ] Logging API
- [ ] Monitoring API

### **動作確認**
- [ ] Pub/Sub メッセージ送受信成功
- [ ] BigQuery テーブル作成成功
- [ ] 予算アラート設定
- [ ] GitHub CLI 認証成功

---

## 🎓 **知っておくと便利なコマンド**

### **プロジェクト管理**

```bash
# プロジェクト一覧
gcloud projects list

# 現在のプロジェクト
gcloud config get-value project

# プロジェクト切り替え
gcloud config set project PROJECT_ID

# プロジェクト削除（注意！）
gcloud projects delete PROJECT_ID
```

### **認証情報**

```bash
# 現在の認証情報
gcloud auth list

# 認証情報を追加
gcloud auth login

# アプリケーションデフォルト認証
gcloud auth application-default login
```

### **API管理**

```bash
# 有効なAPI一覧
gcloud services list --enabled

# 利用可能なAPI一覧
gcloud services list --available

# API無効化
gcloud services disable SERVICE_NAME
```

---

## 🔍 **トラブルシューティング**

### **認証エラー**

```
症状: gcloud コマンドで認証エラー

対策:
  gcloud auth login
  gcloud auth application-default login
```

### **プロジェクトが見つからない**

```
症状: ERROR: (gcloud...) Project [XXX] not found

対策:
  # プロジェクトIDを確認
  gcloud projects list
  
  # 正しいIDを設定
  gcloud config set project CORRECT_PROJECT_ID
```

### **API未有効化エラー**

```
症状: API [xxx.googleapis.com] not enabled

対策:
  # API有効化
  gcloud services enable xxx.googleapis.com
  
  # または、GCPコンソールから有効化
```

---

## 💡 **次のステップ**

GCP環境が整いました！次は実際にデプロイしてみましょう。

**Phase 1（手動デプロイ）:** [03_PHASE1_MANUAL.md](03_PHASE1_MANUAL.md)

---

## 📚 **参考リンク**

- [gcloud CLI リファレンス](https://cloud.google.com/sdk/gcloud/reference)
- [GCP無料枠](https://cloud.google.com/free)
- [BigQuery クイックスタート](https://cloud.google.com/bigquery/docs/quickstarts)
- [Pub/Sub クイックスタート](https://cloud.google.com/pubsub/docs/quickstarts)
