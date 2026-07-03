# AquaPulse 再セットアップ手順

このドキュメントは、ラズパイのOSをリセットして最初から構築する際の完全な手順です。

## 前提条件

- Raspberry Pi 5 (8GB) + NVMe SSD
- Raspberry Pi OS Lite (Bookworm, 64-bit) を新規インストール済み
- SSH接続が可能な状態（初回セットアップでSSHを有効化）
- インターネット接続が利用可能

---

## 📝 **事前に控えておく必要がある情報**

以下の情報を**必ずメモしておいてください**（GitHubに入っていない秘密情報）：

### 1. データベース認証情報
- `POSTGRES_USER`: ______________ （通常は `postgres`）
- `POSTGRES_PASSWORD`: ______________ 
- `POSTGRES_DB`: ______________ （通常は `aquapulse`）

### 2. Tapo 認証情報
- `TAPO_USERNAME`: ______________ （Tapoアプリのメールアドレス）
- `TAPO_PASSWORD`: ______________ （Tapoアプリのパスワード）

### 3. Tapo デバイスIP
- `TAPO_HUB_IP`: ______________ （H100 ハブ、例: 192.168.3.6）
- `TAPO_LIGHTING_IP`: ______________ （P300 マルチタップ、例: 192.168.3.8）

> **ヒント**: TapoアプリでデバイスのIPアドレスを確認できます（デバイス詳細 > 端末情報）

### 4. 有効化するデータソース
- `SOURCES`: ______________ （例: `gpio_temp,tapo_sensors,tapo_lighting`）

---

## 🚀 **セットアップ手順**

### ステップ1: システムアップデート

```bash
sudo apt update
sudo apt upgrade -y
```

### ステップ2: 必要なパッケージのインストール

```bash
# Git
sudo apt install -y git

# Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Python（スクリプト用）
sudo apt install -y python3 python3-pip python3-smbus i2c-tools

# 1-Wire（DS18B20水温センサー用）
sudo raspi-config nonint do_onewire 0

# I2C（TDSセンサー用）
sudo raspi-config nonint do_i2c 0
```

**再起動が必要です：**
```bash
sudo reboot
```

### ステップ3: プロジェクトのクローン

SSH再接続後：

```bash
# プロジェクトディレクトリ作成
sudo mkdir -p /projects
sudo chown $USER:$USER /projects
cd /projects

# GitHubからクローン
git clone https://github.com/YOUR_USERNAME/aquapulse.git
cd aquapulse
```

> **注意**: `YOUR_USERNAME` を実際のGitHubユーザー名に置き換えてください

### ステップ4: 環境変数の設定

```bash
# .env.example をコピー
cp .env.example .env

# エディタで編集（nano または vim）
nano .env
```

**以下の値を実際の環境に合わせて設定：**

```bash
# データベース
POSTGRES_USER=postgres
POSTGRES_PASSWORD=【控えたパスワード】
POSTGRES_DB=aquapulse

# データソース
SOURCES=gpio_temp,tapo_sensors,tapo_lighting

# Tapo認証
TAPO_USERNAME=【Tapoのメールアドレス】
TAPO_PASSWORD=【Tapoのパスワード】

# TapoデバイスIP
TAPO_HUB_IP=【H100のIP】
TAPO_LIGHTING_IP=【P300のIP】
```

保存して終了（nano: `Ctrl+O` → `Enter` → `Ctrl+X`）

### ステップ5: Docker Composeで起動

```bash
# Docker Composeで全サービスを起動
docker compose up -d

# 起動確認
docker compose ps

# ログ確認
docker compose logs -f
```

**期待される状態：**
- `db` (TimescaleDB): `running (healthy)`
- `grafana`: `running`
- `collector`: `running`

### ステップ6: センサーの動作確認

#### DS18B20 水温センサー

```bash
# センサーが認識されているか確認
ls /sys/bus/w1/devices/

# 28-XXXXXXXXXXXX が表示されればOK
```

#### MCP3424 TDSセンサー

```bash
# I2Cデバイスの確認
i2cdetect -y 1

# 0x68 が表示されればOK
```

### ステップ7: Grafanaへのアクセス

ブラウザで `http://【ラズパイのIP】:3000` にアクセス

- 初回ログイン: `admin` / `admin`
- パスワード変更を求められたら変更

データソースの設定（初回のみ）：

1. Configuration > Data sources > Add data source
2. PostgreSQL を選択
3. 設定：
   - Host: `db:5432`
   - Database: `aquapulse`
   - User: `postgres`
   - Password: `.env`で設定したパスワード
   - TLS/SSL Mode: `disable`
4. Save & Test

### ステップ8: キオスクモード設定（オプション）

Pi Touch Display を使用する場合：

```bash
# 必要なパッケージのインストール
sudo apt install -y cage chromium seatd

# systemdサービスの有効化
sudo cp kiosk/grafana-kiosk.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable grafana-kiosk
sudo systemctl start grafana-kiosk
```

詳細: [docs/display/grafana-kiosk.md](docs/display/grafana-kiosk.md)

---

## ✅ **動作確認チェックリスト**

- [ ] `docker compose ps` で3つのサービスが `running`
- [ ] `docker compose logs collector` でエラーがない
- [ ] Grafanaにアクセスできる
- [ ] `sensor_readings` テーブルにデータが入っている
  ```bash
  docker compose exec db psql -U postgres -d aquapulse \
    -c "SELECT COUNT(*) FROM sensor_readings;"
  ```
- [ ] 水温センサーのデータが収集されている
  ```bash
  docker compose logs collector | grep gpio_temp
  ```
- [ ] Tapo センサーのデータが収集されている
  ```bash
  docker compose logs collector | grep tapo_sensors
  ```

---

## 🔧 **トラブルシューティング**

### collector が起動しない

```bash
# ログを確認
docker compose logs collector

# よくある原因:
# 1. .env の設定ミス → .env を再確認
# 2. センサーが未接続 → SOURCES=mock でテスト
# 3. I2C/1-Wireが無効 → raspi-config で有効化
```

### Tapo 接続エラー

```bash
# IPアドレスの確認
# Tapoアプリ > デバイス > 端末情報 でIPを確認

# 疎通確認
ping 【TAPO_HUB_IP】

# ローラー作戦を試す（.envに追加）
TAPO_IP_CANDIDATES=192.168.3.6,192.168.3.7,192.168.3.8
```

### データベース接続エラー

```bash
# データベースが起動しているか確認
docker compose ps db

# データベースに直接接続して確認
docker compose exec db psql -U postgres -d aquapulse -c "\dt"
```

---

## 📚 **参考ドキュメント**

- [README.ja.md](README.ja.md) - プロジェクト概要
- [docs/design/architecture.md](docs/design/architecture.md) - アーキテクチャ設計
- [docs/hardware/wiring/](docs/hardware/wiring/) - センサー配線図
- [docs/operations/daily-log.md](docs/operations/daily-log.md) - 運用ログ
- [docs/display/grafana-kiosk.md](docs/display/grafana-kiosk.md) - キオスク設定

---

## 💾 **バックアップ推奨項目**

今後のために、以下をバックアップしておくことを推奨します：

1. **`.env` ファイル**（別の安全な場所に）
2. **Grafanaダッシュボード**（JSON export）
3. **データベースダンプ**（定期的に）
   ```bash
   docker compose exec db pg_dump -U postgres aquapulse > backup.sql
   ```

---

## 🆘 **それでも復旧できない場合**

1. **モックモードで起動してみる**
   ```bash
   # .env を編集
   SOURCES=mock
   
   # 再起動
   docker compose restart collector
   ```
   
2. **段階的にセンサーを追加**
   ```bash
   # まず1つだけ
   SOURCES=gpio_temp
   
   # 動作確認後、徐々に追加
   SOURCES=gpio_temp,tapo_sensors
   ```

3. **Cloud Agent（私）に相談**
   - 具体的なエラーログを共有してください
   - 一緒にデバッグします！
