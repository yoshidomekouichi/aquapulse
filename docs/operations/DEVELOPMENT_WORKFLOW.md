# 開発ワークフロー管理マニュアル

**提案書 v1.1**  
**最終更新: 2026-07-03**

---

## 📋 目次

1. [はじめに](#はじめに)
2. [現状の問題と提案](#現状の問題と提案)
3. [SSOT（Single Source of Truth）の確立](#ssotingle-source-of-truthの確立)
4. [Git基本ワークフロー](#git基本ワークフロー)
5. [Cursor製品の使い分け](#cursor製品の使い分け)
6. [機密情報管理戦略](#機密情報管理戦略)
7. [実践ガイド](#実践ガイド)
8. [トラブルシューティング](#トラブルシューティング)
9. [今後の拡張計画](#今後の拡張計画)

---

## 🎯 はじめに

### このドキュメントの目的

```
目的:
  1. ローカルデバイス（ラズパイ等）への依存を脱却
  2. GitHubをコードのSSOTとして確立
  3. Cursor製品を効果的に使い分ける
  4. 機密情報を安全に管理する
  5. どこからでも開発できる環境を構築
```

### 対象読者

- 個人開発者（本プロジェクト管理者）
- 将来的なチームメンバー
- 自分自身の将来の参照用

### 前提知識

- Git/GitHubの基本操作
- 環境変数の概念
- Cursorアカウントの保有

---

## 🚨 現状の問題と提案

### 1. 現状の問題点

#### **問題A: ラズパイへの依存**

```
現状:
  ✗ ラズパイがSSoT（Single Source of Truth）
  ✗ SSH接続が切れると全てアクセス不可
  ✗ 物理アクセスも困難（水槽の裏）
  ✗ 復旧に高コスト

影響:
  - 開発停止リスク
  - データ喪失リスク
  - 再現性の低さ
```

#### **問題B: 機密情報の分散管理**

```
現状:
  ✗ .envファイルがローカルのみ
  ✗ バックアップが不完全
  ✗ 他のデバイスで開発困難

影響:
  - 環境再構築の困難さ
  - パスワード喪失リスク
  - チーム展開の困難さ
```

#### **問題C: Cursor製品の理解不足**

```
現状:
  ✗ Desktop IDEしか知らなかった
  ✗ Dashboardの存在を知らなかった
  ✗ Cloud Agentの活用ができていない

影響:
  - 非効率な開発フロー
  - Cloud Agentの未活用
  - モバイル開発の機会損失
```

---

### 2. 提案するアーキテクチャ

```
┌─────────────────────────────────────────────┐
│          新しいアーキテクチャ                 │
├─────────────────────────────────────────────┤
│                                              │
│  【コード】                                   │
│  GitHub = SSOT                               │
│    ├── コード                                 │
│    ├── .env.example（テンプレート）           │
│    ├── ドキュメント                           │
│    └── 設定ファイル                           │
│                                              │
│  【機密情報】                                 │
│  Cursor Dashboard = SSOT                     │
│    ├── API鍵                                 │
│    ├── データベースパスワード                 │
│    ├── 外部サービス認証情報                   │
│    └── 環境変数                               │
│                                              │
│  【開発環境】                                 │
│  デバイス非依存                               │
│    ├── ローカル（Mac）                        │
│    ├── Cloud Agent（VM）                     │
│    └── モバイル（監視・起動）                 │
│                                              │
└─────────────────────────────────────────────┘
```

### 3. 期待される効果

| 項目 | 現状 | 提案後 | 改善度 |
|------|------|--------|--------|
| **復旧時間** | 数時間〜数日 | 数分 | 🟢🟢🟢 |
| **デバイス依存** | 高（ラズパイ必須） | ゼロ | 🟢🟢🟢 |
| **機密情報管理** | ローカル分散 | 一元管理 | 🟢🟢 |
| **チーム展開** | 困難 | 容易 | 🟢🟢🟢 |
| **外出先開発** | 不可 | 可能 | 🟢🟢 |

---

## 📚 SSOT（Single Source of Truth）の確立

### 1. SSOTとは

```
Single Source of Truth = 唯一の信頼できる情報源

原則:
  - あらゆる情報は1箇所に集約
  - その他は全てコピーまたは派生
  - 矛盾が発生しない
```

### 2. AquaPulseにおけるSSoT定義

| 情報種別 | SSOT | 理由 |
|---------|------|------|
| **ソースコード** | GitHub | バージョン管理、どこからでもアクセス可 |
| **開発用機密情報** | Cursor Dashboard | 暗号化、チーム共有、デバイス非依存 |
| **本番機密情報**（移行後） | GCP Secret Manager | 本番環境専用、IAM連携 |
| **ドキュメント** | GitHub | コードと同一リポジトリで管理 |
| **設定ファイル** | GitHub | `.cursor/`等、IaC原則 |

### 3. 禁止事項

```
❌ やってはいけないこと:

1. ローカルのみに重要情報を保存
2. .envファイルをGitHubにコミット
3. ラズパイ等の物理デバイスをSSOTにする
4. 機密情報をドキュメントにベタ書き
5. 複数箇所に同じ情報を重複管理
```

---

## 🔄 Git基本ワークフロー

### 1. Gitの仕組み（超シンプル版）

```
Git = 差分管理システム

最初（1回だけ）:
  git clone → リポジトリ全体をダウンロード

2回目以降（毎回）:
  git pull → 変更分だけ取得して更新
```

---

### 2. 初回セットアップ

#### **ステップ1: リポジトリをclone（最初の1回だけ）**

```bash
# ターミナルで

# 1. 作業ディレクトリに移動
cd ~/Projects

# 2. リポジトリをクローン（全ファイルダウンロード）
git clone https://github.com/yoshidomekouichi/aquapulse.git

# 出力例:
# Cloning into 'aquapulse'...
# remote: Counting objects: 100% (234/234), done.
# ...

# 3. 移動
cd aquapulse

# 4. ファイル確認
ls -la
# README.md, docker-compose.yml, docs/ など
```

**重要**: `git clone`は**最初の1回だけ**実行します。

---

#### **ステップ2: .envファイルを作成（初回のみ）**

```bash
# .env.exampleをコピー
cp .env.example .env

# .envを編集して実際の値を入力
# （エディタまたはCursor IDEで開く）
cursor .
```

---

### 3. 日常的な作業フロー

#### **A. 作業開始時（毎回必須）**

```bash
# 最新の変更を取得
cd aquapulse
git pull

# 出力例1（変更なし）:
# Already up to date.

# 出力例2（更新あり）:
# Updating a1b2c3d..e4f5g6h
# Fast-forward
#  main.py | 10 +++++++---
#  1 file changed, 7 insertions(+), 3 deletions(-)
```

**ポイント**: `git pull`は**差分だけ**を取得して更新します。

---

#### **B. 開発作業**

```bash
# コード編集...

# 変更を確認
git status

# 出力例:
# modified:   collector/src/main.py
# modified:   README.md
```

---

#### **C. 変更を保存（GitHubにpush）**

```bash
# 1. 変更をステージング
git add .

# 2. コミット（ローカルに記録）
git commit -m "fix: センサー読み取りロジックを修正"

# 3. GitHubにpush（アップロード）
git push

# 出力:
# To https://github.com/yoshidomekouichi/aquapulse
#   a1b2c3d..e4f5g6h  main -> main
```

---

### 4. pullの仕組み（詳細）

```
GitHub:
  README.md（昨日変更）
  main.py（今日変更）
  config.py（1週間前のまま）

あなたのMac:
  README.md（古い）
  main.py（古い）
  config.py（1週間前のまま）

↓ git pull 実行

あなたのMac:
  README.md（更新！）
  main.py（更新！）
  config.py（変更なし、そのまま）

ダウンロードするのは差分だけ！
```

---

### 5. 各環境での最新版取得方法

| 環境 | 最新版の取得方法 | 手動操作 | タイミング |
|------|-----------------|---------|-----------|
| **Desktop（ローカル）** | `git pull` | ✅ 必要 | 作業開始時 |
| **Cloud Agent** | 自動clone | ❌ 不要 | 起動時 |
| **Mobile App** | 自動（Cloud Agent経由） | ❌ 不要 | Agent起動時 |
| **cursor.com/agents** | 自動clone | ❌ 不要 | 起動時 |

**重要**: ローカル開発時のみ`git pull`が必要です。Cloud Agentは自動で最新版を使います。

---

### 6. よくある質問

#### **Q1: 毎回git cloneする？**

```
A: NO

初回だけ:
  git clone（全部ダウンロード）

2回目以降:
  git pull（差分だけ）
```

#### **Q2: ファイルを選んで取得できる？**

```
A: 基本的にNO

Gitは「リポジトリ全体」を管理します。

でも心配不要:
  - 小さいリポジトリなら一瞬
  - AquaPulseは数MB程度
  - ネットワーク負荷も低い
```

#### **Q3: ローカルの編集は消える？**

```
A: NO、守られる

git pullは:
  - 変更があったファイルだけ更新
  - あなたの編集は保持される
  - 競合（conflict）は稀
```

---

### 7. Git操作チートシート

```bash
# === 日常的に使うコマンド ===

# 最新版を取得
git pull

# 変更を確認
git status

# 変更を保存
git add .
git commit -m "メッセージ"
git push

# === トラブル時 ===

# ローカルの変更を全て破棄
git reset --hard
git pull

# 最近の履歴を確認
git log --oneline -5
```

---

## 🛠️ Cursor製品の使い分け

### 1. 製品一覧と役割

#### **重要: Cloud Agentは1つ、操作場所は3つ**

```
┌─────────────────────────────────────────┐
│      Cloud Agent（実体 = GCPのVM）       │
│      AIが作業する場所                     │
│      あなたは直接触れない                 │
└─────────────────────────────────────────┘
         ↑                ↑              ↑
         │                │              │
    指示を送る         指示を送る      指示を送る
         │                │              │
┌────────────┐   ┌────────────┐   ┌─────────┐
│ Desktop    │   │cursor.com/ │   │ Mobile  │
│ IDE        │   │  agents    │   │ App     │
│            │   │  (Web)     │   │ (iOS)   │
│ 起動ボタン │   │ 起動ボタン │   │起動ボタン│
└────────────┘   └────────────┘   └─────────┘

どこから起動しても同じCloud Agent
```

---

#### **A. Cursor Desktop（IDE）**

```
種類: ローカルアプリケーション

できること:
  ✅ コードを直接編集（キーボードでタイプ）
  ✅ ファイルを直接作成・削除
  ✅ ターミナルで直接コマンド実行
  ✅ ローカルAgentを起動（リアルタイム対話）
  ✅ Cloud Agentを起動（指示を出す）

用途:
  - 日常的なコーディング
  - リアルタイム対話
  - 短時間の作業（〜30分）

不向き:
  ❌ 長時間の作業（デバイス閉じると停止）
  ❌ 外出先からの操作
```

---

#### **B. Cursor Dashboard（Web管理画面）**

```
URL: cursor.com/dashboard
種類: Webブラウザでアクセス

できること:
  ✅ Secrets管理（環境変数、API鍵）
  ✅ 課金・プラン管理
  ✅ チームメンバー管理
  ✅ Cloud Agents環境設定
  ✅ 使用量の確認

できないこと:
  ❌ コード編集
  ❌ Agent起動

頻度:
  - 初期設定時: 必須
  - 運用中: 月1回程度（確認用）
  - 新しいSecrets追加時: 随時
```

---

#### **C. cursor.com/agents（Cloud Agent実行画面）**

```
URL: cursor.com/agents
種類: Webブラウザでアクセス

できること:
  ✅ Cloud Agentの起動・管理
  ✅ Cloud Agentに指示
  ✅ 実行結果を見る（差分確認）
  ✅ PRの作成・レビュー

できないこと:
  ❌ コードを直接編集（見るだけ）

用途:
  - 長時間タスクの実行
  - ブラウザでの動作確認

特徴:
  - デバイス閉じても継続
  - 複数タスク同時実行可能
```

---

#### **D. Cursor Mobile App（iOS）**

```
種類: iPhoneアプリ

できること:
  ✅ 外出先からCloud Agent起動
  ✅ 実行中のAgent監視
  ✅ PRレビュー・マージ
  ✅ 通知受信

できないこと:
  ❌ コード編集（見るだけ）
  ❌ 複雑な操作
  ❌ 長文の入力

用途:
  - 外出先からAgent起動
  - 進捗確認
```

---

### 2. ローカルAgent vs Cloud Agent

#### **比較表**

| 項目 | ローカルAgent | Cloud Agent |
|------|--------------|-------------|
| **実行場所** | あなたのMac | クラウドのVM |
| **起動方法** | Desktop IDEから | Desktop/Web/Mobile どこからでも |
| **ファイル** | ローカル（Mac内） | クラウド（VM内） |
| **あなたの編集** | ✅ できる | ❌ できない（見るだけ） |
| **AIの編集** | ✅ できる | ✅ できる |
| **デバイス閉じたら** | ❌ 停止 | ✅ 継続 |
| **git操作** | あなたが手動 | AIが自動 |
| **用途** | 短時間・対話的 | 長時間・放置OK |

---

#### **詳細: ローカルAgent**

```
【実行環境】
あなたのMac内

【ファイルの場所】
~/Projects/aquapulse/
  ├ main.py ← AIが編集
  │         ← あなたも編集できる
  │         （同じファイルを共有）

【作業フロー】
1. Desktop IDEでローカルAgent起動
2. 「main.py に関数追加して」
3. AIが編集（ローカルファイル）
4. すぐ確認できる
5. 自分で修正もできる
6. 手動でgit commit & push

【メリット】
✅ リアルタイム確認
✅ すぐ修正できる
✅ ローカル環境使用

【デメリット】
❌ Mac閉じると停止
❌ 長時間作業に不向き
```

---

#### **詳細: Cloud Agent**

```
【実行環境】
クラウドのVM（GCP）

【ファイルの場所】
クラウドVM内（触れない場所）
  ├ main.py ← AIが編集
  │         ← あなたは見るだけ

【作業フロー】
1. Desktop/Web/Mobile から起動
2. 「main.py に関数追加して」
3. AIが編集（クラウドで）
4. 自動でテスト
5. 自動でgit push
6. あなたはgit pullで取得

【メリット】
✅ デバイス閉じてもOK
✅ 長時間作業向き
✅ 外出先から起動可能

【デメリット】
❌ 直接編集できない
❌ 結果を見るまで待つ
```

---

### 3. 直接コード編集ができる場所

```
Q: 直接コードを書きたい

A: Desktop IDE（ローカル）のみ

手順:
  1. cd aquapulse
  2. git pull
  3. cursor .
  4. ファイルを開いて編集
  5. 保存

他の場所（Web/Mobile）:
  → 直接編集はできない
  → Cloud Agentに指示するだけ
```

---

### 4. 使い分けフローチャート

```
┌─────────────────────────┐
│ 作業を開始する           │
└────────┬────────────────┘
         │
         ↓
    ┌─────────────────┐
    │ 作業時間は？     │
    └────┬────────┬───┘
         │        │
    短時間      長時間
    （〜30分）  （数時間）
         │        │
         ↓        ↓
    ┌─────────┐  ┌──────────────┐
    │ローカル  │  │ Cloud Agent  │
    │Desktop  │  │ cursor.com/  │
    │IDE      │  │ agents       │
    └─────────┘  └──────────────┘
         │              │
         ↓              ↓
    その場で作業    外出OK
                   スマホで監視
```

---

### 5. シナリオ別推奨

#### **シナリオ1: 通常の機能開発（ローカルAgent）**

```
使用: Desktop IDE + ローカルAgent

手順:
  1. cd aquapulse
  2. git pull
  3. cursor .
  4. IDE内でローカルAgent起動
  5. 「〇〇機能を実装して」
  6. リアルタイムで確認・修正
  7. 自分でも編集できる
  8. git add . && git commit && push

特徴:
  - あなたもAIも同じファイルを触る
  - すぐ確認・修正できる
```

---

#### **シナリオ2: 大規模リファクタリング（Cloud Agent）**

```
使用: Cloud Agent（Desktop/Web/Mobile どこからでも）

手順:
  1. cursor.com/agents または Desktop IDEから起動
  2. リポジトリ選択
  3. 「〇〇をリファクタリングしてPR作成」
  4. （外出してOK、Mac閉じてOK）
  5. 数時間後、通知でPR完成を確認
  6. git pull で取得
  7. レビュー・マージ

特徴:
  - AIだけがファイルを触る
  - あなたは結果を見る
  - 長時間でもOK
```

---

#### **シナリオ3: 外出先での緊急対応**

```
使用: Mobile App → Cloud Agent

手順:
  1. iPhoneでCursor Mobile App起動
  2. 「本番バグを修正」
  3. 通知待ち
  4. Mobile AppでPRレビュー
  5. マージ
```

---

#### **シナリオ4: ドキュメント作成**

```
使用: Cloud Agent（今回のケース）

手順:
  1. Mobile AppまたはWeb経由でAgent起動
  2. 「〇〇ドキュメントを作成」
  3. デバイス閉じてOK
  4. 完成したらgit pull
  5. デスクトップで確認
```

---

## 🔐 機密情報管理戦略

### 1. 情報分類

| 分類 | 例 | 保存先 | GitHub |
|------|---|--------|--------|
| **公開情報** | リポジトリURL、ドキュメント | GitHub | ✅ コミット |
| **非機密設定** | デフォルトポート、フラグ | GitHub（`.env.example`） | ✅ コミット |
| **機密情報（開発）** | API鍵、DBパスワード | Cursor Dashboard | ❌ gitignore |
| **機密情報（本番）** | 本番API鍵、証明書 | GCP Secret Manager | ❌ gitignore |

---

### 2. Cursor Dashboard での管理

#### **A. アクセス方法**

```bash
# ブラウザで
cursor.com/dashboard

# ログイン後
→ 左メニュー「Cloud Agents」
→ 「Secrets」タブ
```

#### **B. Secret の種類**

| タイプ | 用途 | Agentから見える？ | 推奨度 |
|--------|------|------------------|--------|
| **Environment Variables** | 非機密設定 | ✅ 見える | 低 |
| **Runtime Secrets** | API鍵、パスワード | ❌ `[REDACTED]` | 🟢 高 |
| **Build Secrets** | Dockerビルド時のみ | ❌ ビルド時のみ | 中 |

**推奨: Runtime Secrets を使用**

#### **C. AquaPulseで管理すべきSecrets**

```
必須:
  - POSTGRES_PASSWORD（データベースパスワード）
  - TAPO_USERNAME（Tapoアカウント）
  - TAPO_PASSWORD（Tapoパスワード）
  - TAPO_HUB_IP（Tapoハブのアドレス）
  - TAPO_LIGHTING_IP（Tapo照明のアドレス）
  
将来（GCP移行後）:
  - GCP_PROJECT_ID
  - GCP_SERVICE_ACCOUNT_KEY
  - BIGQUERY_DATASET
  - GRAFANA_API_KEY
```

---

### 3. リポジトリ構成

#### **A. ディレクトリ構成**

```
aquapulse/
├── .env.example          # ✅ GitHub: テンプレート
├── .env                  # ❌ gitignore: ローカル開発用
├── .gitignore            # ✅ .env* を除外
├── .cursor/
│   └── environment.json  # ✅ GitHub: Cloud Agent設定
├── docs/
│   └── operations/
│       └── DEVELOPMENT_WORKFLOW.md  # ✅ このファイル
└── README.md
```

#### **B. `.env.example` のフォーマット**

```.env
# Database Configuration
POSTGRES_USER=aquapulse
POSTGRES_PASSWORD=          # ← Cursor Dashboardで設定
POSTGRES_DB=aquapulse
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Tapo API Configuration
TAPO_USERNAME=              # ← Cursor Dashboardで設定
TAPO_PASSWORD=              # ← Cursor Dashboardで設定
TAPO_HUB_IP=                # ← Cursor Dashboardで設定
TAPO_LIGHTING_IP=           # ← Cursor Dashboardで設定

# Sensor Configuration
SOURCES=tapo_hub,tapo_lighting,ds18b20,mcp3424
GPIO_TEMP_INTERVAL=60
TDS_SENSOR_ID=mcp3424_tds_0
```

#### **C. `.gitignore` の設定**

```.gitignore
# Environment files
.env*
!.env.example

# Local data
db_data/
grafana_data/

# IDE
.cursor/settings.json
.vscode/
```

---

### 4. 実装チェックリスト

#### **初期設定**

- [ ] `.env.example` を作成（値は空）
- [ ] `.gitignore` に `.env*` を追加
- [ ] `!.env.example` を追加（例外）
- [ ] 既存の `.env` を削除（gitから）
- [ ] `cursor.com/dashboard` にアクセス
- [ ] Runtime Secrets を全て登録
- [ ] `.cursor/environment.json` を作成

#### **運用中**

- [ ] 新しいSecretは必ずDashboardに登録
- [ ] `.env.example` を同期（値は空にする）
- [ ] 定期的にSecretsの棚卸し（四半期ごと）
- [ ] 使わなくなったSecretsは削除
- [ ] パスワード変更時はDashboardを更新

---

## 🚀 実践ガイド

### Phase 1: 現状からの移行（1日）

#### **ステップ1: 機密情報の抽出**

```bash
# ラズパイまたはローカル環境で
cat .env

# または
env | grep -E "POSTGRES|TAPO|API|KEY|SECRET|TOKEN"

# 結果をメモ（次のステップで使用）
```

#### **ステップ2: GitHubリポジトリの整理**

```bash
# 1. .env.example作成
cp .env .env.example

# 2. .env.exampleから値を削除（テンプレート化）
# エディタで開いて、=の右側を全て削除

# 3. .gitignoreに追加
echo ".env*" >> .gitignore
echo "!.env.example" >> .gitignore

# 4. 既存の.envをgitから削除（ファイルは残す）
git rm --cached .env 2>/dev/null || true

# 5. コミット
git add .env.example .gitignore
git commit -m "chore: .env.exampleを追加、.envを除外"
git push
```

#### **ステップ3: Cursor Dashboardに登録**

```
1. ブラウザで cursor.com/dashboard を開く
2. ログイン
3. 左メニュー → Cloud Agents
4. Secrets タブ
5. 「Add Secret」
6. Type: Runtime Secrets
7. Name: POSTGRES_PASSWORD
8. Value: （ステップ1で抽出した値）
9. Scope: User/Team（またはEnvironment）
10. Save

# 全てのSecretsについて繰り返す
```

#### **ステップ4: 動作確認**

```bash
# Cloud Agentで確認

# cursor.com/agents にアクセス
# → リポジトリ選択
# → "環境変数が正しく設定されているか確認して"

# または Desktop IDEから
# → Cloud Agent起動
# → "echo $POSTGRES_PASSWORD を実行して"
```

---

### Phase 2: 日常的な運用

#### **A. ローカル開発時**

```bash
# 1. リポジトリをclone
git clone https://github.com/yoshidomekouichi/aquapulse.git
cd aquapulse

# 2. .envを作成（ローカル開発用）
cp .env.example .env

# 3. Cursor Dashboardから値をコピー
# または、ローカル用の値を設定

# 4. 開発開始
cursor .
```

#### **B. Cloud Agentでの開発**

```bash
# 1. cursor.com/agents にアクセス
# 2. リポジトリ選択
# 3. タスクを指示
# 4. （Secretsは自動で注入される）

# .envファイルは不要！
```

#### **C. 新しいSecretの追加**

```bash
# 1. .env.exampleに追加（値は空）
echo "NEW_API_KEY=" >> .env.example

# 2. コミット
git add .env.example
git commit -m "docs: NEW_API_KEYを追加"
git push

# 3. Cursor Dashboardに実際の値を登録
# cursor.com/dashboard → Secrets → Add
```

---

### Phase 3: チーム展開（将来）

#### **新メンバーのオンボーディング**

```
1. GitHubリポジトリへのアクセス権付与
2. Cursorアカウント作成
3. チームに招待（Dashboard経由）
4. Secretsは自動で共有される
5. ローカル開発の場合は.envを個別作成

所要時間: 10分
```

---

## 🔧 トラブルシューティング

### 1. Cloud Agentで環境変数が見つからない

#### **症状**

```bash
Error: POSTGRES_PASSWORD not found in environment
```

#### **原因と対策**

| 原因 | 確認方法 | 対策 |
|------|---------|------|
| Dashboardに未登録 | `cursor.com/dashboard` → Secrets | 登録する |
| 名前の不一致 | Secret名と`.env.example`を比較 | 修正する |
| Scopeが間違っている | Secret設定のScope確認 | 正しいScopeに変更 |
| Public リポジトリで無効 | リポジトリ設定確認 | Secret注入を許可 |

---

### 2. ローカル開発で環境変数が見つからない

#### **症状**

```bash
# ローカルで実行時
Error: TAPO_USERNAME not found
```

#### **原因と対策**

```bash
# 原因: .envファイルが存在しない

# 対策1: .envを作成
cp .env.example .env

# 対策2: Cursor Dashboardから値をコピー
# cursor.com/dashboard → Secrets
# → 各値を.envに手動でコピー

# または、direnvなどのツール使用も検討
```

---

### 3. .envをうっかりコミットしてしまった

#### **症状**

```bash
git status
# On branch main
# Changes to be committed:
#   modified:   .env
```

#### **対策**

```bash
# まだpushしていない場合
git reset HEAD .env
git restore .env

# 既にpushしてしまった場合
git rm --cached .env
git commit -m "chore: .envを除外"
git push

# GitHub上の履歴から完全削除（必要な場合）
# https://docs.github.com/ja/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository

# Secretsの値を全て変更（漏洩対策）
```

---

### 4. Cursor Dashboardにアクセスできない

#### **症状**

```
cursor.com/dashboard → ログイン画面でループ
```

#### **対策**

```
1. ブラウザのキャッシュをクリア
2. シークレットモードで試す
3. 別のブラウザで試す
4. Cursorサポートに連絡
   support@cursor.com
```

---

## 📈 今後の拡張計画

### v1.1: GCP移行後の管理（計画中）

```
追加予定:
  - GCP Secret Managerとの連携
  - 本番環境用のSecret管理フロー
  - Terraform経由のインフラ管理
  - 環境別（dev/prod）のSecret分離
```

### v1.2: 自動化（計画中）

```
追加予定:
  - GitHub Actionsでの自動デプロイ
  - Secret Rotationの自動化
  - 定期的なSecrets監査スクリプト
  - .env.exampleとDashboardの整合性チェック
```

### v1.3: チーム展開（計画中）

```
追加予定:
  - チームメンバー用のオンボーディングガイド
  - ロール別のSecret管理ポリシー
  - 監査ログの確認方法
  - インシデント対応フロー
```

---

## 📚 参考リンク

### Cursor公式ドキュメント

- [Cursor Dashboard](https://cursor.com/dashboard)
- [Cloud Agents](https://docs.cursor.com/context/cloud-agents)
- [Secrets管理](https://docs.cursor.com/context/cloud-agents#secrets)

### AquaPulse プロジェクト

- [緊急復旧手順](./EMERGENCY_BACKUP_CHECKLIST.md)
- [クラウド移行ガイド](../cloud-migration/README.md)
- [トラブルシューティング](../cloud-migration/07_TROUBLESHOOTING.md)

### 外部リソース

- [12 Factor App - Config](https://12factor.net/config)
- [GitHub Secrets管理](https://docs.github.com/ja/actions/security-guides/encrypted-secrets)
- [GCP Secret Manager](https://cloud.google.com/secret-manager/docs)

---

## 📝 変更履歴

| 日付 | バージョン | 変更内容 | 作成者 |
|------|-----------|---------|--------|
| 2026-07-03 | 1.1.0 | Git基本ワークフロー追加、Cursor製品の使い分け拡充（ローカルAgent vs Cloud Agent詳細、直接編集可能な場所の明確化） | Cloud Agent |
| 2026-07-03 | 1.0.0 | 初版作成（ラズパイ死亡事件からの学び） | Cloud Agent |

---

## ✅ レビューチェックリスト

このドキュメントを実装する際の最終確認：

### 技術面

- [ ] `.env.example` が最新か
- [ ] `.gitignore` に `.env*` があるか
- [ ] Cursor Dashboardに全Secretsを登録したか
- [ ] Cloud Agentで動作確認したか
- [ ] ローカルでも動作確認したか

### セキュリティ面

- [ ] `.env` がGitHubにコミットされていないか
- [ ] Runtime Secretsを使用しているか
- [ ] Secretsのバックアップを取ったか（安全な場所に）
- [ ] 古いSecretsを削除したか

### ドキュメント面

- [ ] `.env.example` のコメントが充実しているか
- [ ] READMEに環境構築手順があるか
- [ ] このドキュメントをチーム（または将来の自分）が理解できるか

---

**このドキュメントは生きています。プロジェクトの進化に合わせて随時更新してください。**

**次のアクション**: Phase 1の実装を開始 → [実践ガイド](#実践ガイド)
