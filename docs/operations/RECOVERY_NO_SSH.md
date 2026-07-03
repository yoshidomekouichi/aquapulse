# SSH接続不可時の復旧手順

**前提条件**: ラズパイにSSH接続できなくなり、モニター・キーボードも接続できない状況での復旧方法

---

## 🎯 **結論：復旧可能です！**

- ✅ システムは完全に復旧できる
- ✅ 必要な秘密情報は少ない（主にTapo認証のみ）
- ❌ 過去のセンサーデータは諦める必要がある

---

## 📊 **復旧可能性マトリックス**

### ✅ **完全に復旧できるもの（GitHubにある）**

| 項目 | 保存場所 | 復旧方法 |
|------|----------|----------|
| プロジェクトコード | GitHub | `git clone` |
| センサードライバ | GitHub | 含まれている |
| データベーススキーマ | `db/init/*.sql` | 初回起動時に自動作成 |
| Grafanaダッシュボード | `grafana/dashboards/*.json` | 自動読み込み |
| ドキュメント | GitHub | 含まれている |
| Docker設定 | `docker-compose.yml` | 含まれている |
| センサー配線図 | `docs/hardware/wiring/` | 含まれている |

**→ コードと設定は全て復旧可能**

---

### 🗑️ **捨ててやり直すもの（諦める）**

| 項目 | 影響 | 対処 |
|------|------|------|
| **過去のセンサーデータ** | 2026年3月から蓄積されたデータが消える | 再起動後から新規に収集し直す |
| データベースの中身 | sensor_readings テーブルが空になる | 新しいデータが蓄積される |
| Grafanaログイン履歴 | 特に問題なし | 初回ログイン時に設定 |
| 旧データベースパスワード | 古いパスワードは不要 | 新しいパスワードを設定 |

**影響の評価:**
- Phase 1（データ収集・可視化）: 影響なし。すぐに再開できる
- Phase 2（イベント記録）: まだ本格運用していないので影響なし
- Phase 3（因果推論）: 未着手なので影響なし
- **結論**: 現時点でのデータ喪失は許容範囲内

---

### ⚠️ **取得が必要な秘密情報**

#### 🔑 **1. Tapo認証情報（必須）**

| 項目 | 環境変数名 | 取得方法 |
|------|-----------|----------|
| メールアドレス | `TAPO_USERNAME` | **Tapoアプリ > プロフィール** で確認 |
| パスワード | `TAPO_PASSWORD` | Tapoアプリにログインできているパスワード |

**取得手順（詳細）:**

1. **Tapoアプリを開く**
2. **右下「プロフィール」タブをタップ**
3. **画面上部にメールアドレスが表示される** → これが `TAPO_USERNAME`
4. **パスワードはアプリログイン時のもの** → これが `TAPO_PASSWORD`
   - パスワードを忘れた場合: Tapoアプリでパスワードリセット可能

**メモ例:**
```
TAPO_USERNAME: your_email@example.com
TAPO_PASSWORD: YourTapoPassword123
```

#### 📍 **2. Tapo デバイスのIP（推奨だが必須ではない）**

| デバイス | 環境変数名 | 取得方法 | 必須度 |
|----------|-----------|----------|--------|
| H100 ハブ | `TAPO_HUB_IP` | Tapoアプリ > H100 > 設定 > 端末情報 | ⚠️ 推奨 |
| P300 マルチタップ | `TAPO_LIGHTING_IP` | Tapoアプリ > P300 > 設定 > 端末情報 | ⚠️ 推奨 |

**取得手順（詳細）:**

1. Tapoアプリを開く
2. デバイス（H100 または P300）を選択
3. 右上の⚙️（設定）アイコンをタップ
4. 「端末情報」または「デバイス情報」を選択
5. IPアドレスが表示される（例: 192.168.3.6）

**IPが分からない場合の代替策:**

IPを指定しなくても、collector は**ローラー作戦**で自動検出します：
- デフォルトで `192.168.3.2` ~ `192.168.3.12` を順に試行
- H100 か P300 かはデバイスの応答で自動判定
- 多少時間がかかるが、最終的には見つかる

**メモ例（IPが分かる場合）:**
```
TAPO_HUB_IP: 192.168.3.6
TAPO_LIGHTING_IP: 192.168.3.8
```

#### 🔒 **3. データベースパスワード（新規設定）**

| 環境変数名 | 対処方法 |
|-----------|----------|
| `POSTGRES_PASSWORD` | **新しく決める**（過去のパスワードは不要） |

**推奨:**
- 16文字以上のランダムな文字列
- 英数字 + 記号を含める
- パスワード生成ツール使用推奨

**例:**
```
POSTGRES_PASSWORD: A7$mP9zX!kQ2vL4w
```

---

## 📋 **今すぐやるべきこと（チェックリスト）**

### **ステップ1: Tapo情報の確認**

- [ ] Tapoアプリを開く
- [ ] プロフィールタブでメールアドレスを確認
- [ ] ログインパスワードを思い出す（またはリセット）
- [ ] H100 の端末情報からIPを確認（オプション）
- [ ] P300 の端末情報からIPを確認（オプション）

### **ステップ2: 情報のメモ**

以下をスマホのメモアプリ、紙、または安全な場所に記録：

```
=== AquaPulse 復旧情報 ===

【Tapo認証】
TAPO_USERNAME: __________________
TAPO_PASSWORD: __________________

【TapoデバイスIP（分かれば）】
TAPO_HUB_IP: __________________
TAPO_LIGHTING_IP: __________________

【データベースパスワード（新規）】
POSTGRES_PASSWORD: __________________

【有効化するセンサー】
SOURCES: gpio_temp,tapo_sensors,tapo_lighting
```

**重要**: このメモは絶対にGitHubにプッシュしないこと！

---

## 🚀 **OS再インストール後の復旧手順**

### **Phase 1: OS準備**

1. **Raspberry Pi OS Lite（Bookworm, 64-bit）を新規インストール**
   - Raspberry Pi Imager 使用
   - **SSH を必ず有効化**（重要！）
   - ホスト名: `aquapulse`（推奨）
   - ユーザー: 任意（例: `pi`）

2. **初回起動後、SSH接続確認**
   ```bash
   # Mac/PCから
   ssh pi@aquapulse.local
   # または
   ssh pi@【ラズパイのIP】
   ```

### **Phase 2: システムセットアップ**

詳細手順: [`RECOVERY_SETUP.md`](RECOVERY_SETUP.md) を参照

**概要:**
```bash
# システムアップデート
sudo apt update && sudo apt upgrade -y

# 必要なパッケージ
sudo apt install -y git docker.io docker-compose
sudo apt install -y python3 python3-pip i2c-tools

# 1-Wire, I2C の有効化
sudo raspi-config nonint do_onewire 0
sudo raspi-config nonint do_i2c 0

# 再起動
sudo reboot
```

### **Phase 3: プロジェクトのクローン**

```bash
# プロジェクトディレクトリ作成
sudo mkdir -p /projects
sudo chown $USER:$USER /projects
cd /projects

# GitHubからクローン
git clone https://github.com/yoshidomekouichi/aquapulse.git
cd aquapulse
```

### **Phase 4: 環境変数の設定**

```bash
# .env.example をコピー
cp .env.example .env

# エディタで編集
nano .env
```

**設定内容（メモした情報を使用）:**

```bash
# ========================================
# データベース設定
# ========================================
POSTGRES_USER=postgres
POSTGRES_PASSWORD=【新しく決めたパスワード】
POSTGRES_DB=aquapulse

# ========================================
# データソース設定
# ========================================
SOURCES=gpio_temp,tapo_sensors,tapo_lighting

# ========================================
# Tapo認証（メモから）
# ========================================
TAPO_USERNAME=【メモしたメールアドレス】
TAPO_PASSWORD=【メモしたパスワード】

# ========================================
# TapoデバイスIP（分かれば）
# ========================================
TAPO_HUB_IP=【H100のIP】
TAPO_LIGHTING_IP=【P300のIP】

# IP不明の場合は上記2行をコメントアウトまたは削除
# ローラー作戦で自動検出されます
```

保存: `Ctrl+O` → `Enter` → `Ctrl+X`

### **Phase 5: 起動**

```bash
# Docker Compose で全サービス起動
docker compose up -d

# 起動確認
docker compose ps
# → db, grafana, collector が全て "running"

# ログ確認
docker compose logs -f collector
# → センサーデータの収集が始まる
```

### **Phase 6: 動作確認**

#### **センサー収集の確認**

```bash
# 水温センサー
docker compose logs collector | grep gpio_temp

# Tapoセンサー
docker compose logs collector | grep tapo_sensors

# 照明
docker compose logs collector | grep tapo_lighting
```

**期待される出力:**
```
collector  | [gpio_temp] Read: {"sensor_id": "ds18b20_water_...", "value": 25.3}
collector  | [tapo_sensors] Read: {"sensor_id": "tapo_temp_...", "value": 23.8}
collector  | [tapo_lighting] Read: {"sensor_id": "tapo_lighting_...", "value": 1}
```

#### **データベース確認**

```bash
# テーブルの確認
docker compose exec db psql -U postgres -d aquapulse -c "\dt"

# データ件数
docker compose exec db psql -U postgres -d aquapulse \
  -c "SELECT COUNT(*) FROM sensor_readings;"

# 最新データ
docker compose exec db psql -U postgres -d aquapulse \
  -c "SELECT * FROM sensor_readings ORDER BY time DESC LIMIT 10;"
```

#### **Grafana確認**

1. ブラウザで `http://【ラズパイのIP】:3000` にアクセス
2. 初回ログイン: `admin` / `admin`
3. パスワード変更を求められたら変更
4. データソース設定（初回のみ）:
   - Configuration > Data sources > Add data source
   - PostgreSQL を選択
   - Host: `db:5432`
   - Database: `aquapulse`
   - User: `postgres`
   - Password: `.env` で設定したパスワード
   - TLS/SSL Mode: `disable`
   - Save & Test
5. ダッシュボードでグラフが表示されることを確認

### **Phase 7: キオスクモード（オプション）**

Pi Touch Display を使用する場合:

```bash
sudo apt install -y cage chromium seatd
sudo cp kiosk/grafana-kiosk.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable grafana-kiosk
sudo systemctl start grafana-kiosk
```

詳細: [`docs/display/grafana-kiosk.md`](../display/grafana-kiosk.md)

---

## 🔧 **トラブルシューティング**

### **Tapo接続エラー**

**症状**: `collector` ログに `[tapo_sensors] Failed:` や `[tapo_lighting] Failed:`

**原因と対処:**

1. **認証エラー**
   ```bash
   # .env の TAPO_USERNAME, TAPO_PASSWORD を再確認
   # スペースや改行が混入していないか確認
   ```

2. **IP不明エラー**
   ```bash
   # .env から TAPO_HUB_IP, TAPO_LIGHTING_IP を削除
   # ローラー作戦に任せる
   nano .env
   # ↓ コメントアウト
   # TAPO_HUB_IP=192.168.3.6
   # TAPO_LIGHTING_IP=192.168.3.8
   
   # 再起動
   docker compose restart collector
   ```

3. **ネットワーク疎通確認**
   ```bash
   # ラズパイからデバイスにpingできるか
   ping 192.168.3.6
   ```

### **水温センサー未検出**

**症状**: `[gpio_temp] Failed to read sensor`

**対処:**

```bash
# センサーの認識確認
ls /sys/bus/w1/devices/
# → 28-XXXXXXXXXXXX が表示されるか？

# 表示されない場合
sudo raspi-config nonint do_onewire 0
sudo reboot

# 配線確認
# docs/hardware/wiring/v2.0.md を参照
```

### **TDSセンサー未検出**

**症状**: `[gpio_tds] Failed to read MCP3424`

**対処:**

```bash
# I2Cデバイスの確認
i2cdetect -y 1
# → 0x68 が表示されるか？

# 表示されない場合
sudo raspi-config nonint do_i2c 0
sudo reboot
```

### **collector が起動しない**

**症状**: `docker compose ps` で collector が `Exited`

**対処:**

```bash
# ログ確認
docker compose logs collector

# よくある原因:
# 1. .env の設定ミス → nano .env で再確認
# 2. I2C/1-Wireが無効 → sudo raspi-config で有効化

# テストとして mock で起動
nano .env
# SOURCES=mock に変更
docker compose restart collector
```

---

## 📊 **復旧後の状態**

### ✅ **動作するもの**

- 水温センサー（DS18B20）のリアルタイム収集
- Tapo温湿度センサー（T310）の収集
- Tapo照明（P300）の状態収集
- TimescaleDBへのデータ蓄積
- Grafanaでのリアルタイム可視化
- キオスクモード（Display表示）

### ❌ **失われたもの**

- 2026年3月〜再インストール直前までのセンサーデータ
  - 水温の推移
  - 室温・湿度の推移
  - 照明ON/OFF履歴

### 📈 **今後について**

- **データ再蓄積**: 再起動後から新しいデータが蓄積される
- **Phase 2**: イベント記録（餌やり、水換え）は未着手なので影響なし
- **Phase 3**: 因果推論モデルは数ヶ月のデータ蓄積後に実装予定
- **結論**: 現時点でのデータ喪失は許容範囲内

---

## 💡 **今後のためのバックアップ推奨**

復旧後、定期的なバックアップを推奨します：

### **1. データベースバックアップ（週1回）**

```bash
# cron で自動化推奨
docker compose exec db pg_dump -U postgres aquapulse > \
  ~/backups/aquapulse_$(date +\%Y\%m\%d).sql
```

### **2. .env ファイルのバックアップ**

```bash
# 安全な場所（外部ストレージ）に保存
# ただしGitHubには絶対にプッシュしない
```

### **3. SSH公開鍵認証の設定**

パスワード認証よりも安全で、接続が安定します：

```bash
# Mac/PC で鍵生成
ssh-keygen -t ed25519 -C "aquapulse"

# 公開鍵をラズパイにコピー
ssh-copy-id pi@aquapulse.local
```

---

## 📚 **関連ドキュメント**

- [RECOVERY_SETUP.md](RECOVERY_SETUP.md) - 詳細なセットアップ手順
- [EMERGENCY_BACKUP_CHECKLIST.md](EMERGENCY_BACKUP_CHECKLIST.md) - SSH接続可能時のバックアップ手順
- [README.ja.md](../../README.ja.md) - プロジェクト概要
- [docs/hardware/wiring/](../hardware/wiring/) - センサー配線図
- [docs/display/grafana-kiosk.md](../display/grafana-kiosk.md) - キオスク設定

---

## 🆘 **それでも困った場合**

1. **段階的にセンサーを追加**
   ```bash
   # まず mock で動作確認
   SOURCES=mock
   
   # 次に1つずつ追加
   SOURCES=gpio_temp
   SOURCES=gpio_temp,tapo_sensors
   SOURCES=gpio_temp,tapo_sensors,tapo_lighting
   ```

2. **Cloud Agentに相談**
   - エラーログを共有
   - `.env` の内容（パスワード部分は伏せて）
   - 一緒にデバッグします！

---

**最終更新**: 2026-07-03
