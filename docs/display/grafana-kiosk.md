# Grafana キオスクモード

Pi Touch Display 1 (800x480) に Grafana ダッシュボードを全画面表示する。

## 概要

| 項目 | 設定 |
|------|------|
| コンポジタ | cage (Wayland) |
| ブラウザ | Chromium |
| 自動起動 | systemd |
| 座席管理 | seatd |
| 環境 | Raspberry Pi OS Lite (Bookworm/Trixie, 64-bit) |

---

## クイックリファレンス

### サービス操作

```bash
# 状態確認
sudo systemctl status grafana-kiosk

# 再起動
sudo systemctl restart grafana-kiosk

# ログ確認
journalctl -u grafana-kiosk -f
```

### 輝度調整

```bash
# 手動で変更
/projects/aquapulse/kiosk/brightness.sh day    # 255 (最大)
/projects/aquapulse/kiosk/brightness.sh night  # 150
/projects/aquapulse/kiosk/brightness.sh dim    # 50
/projects/aquapulse/kiosk/brightness.sh 100    # 任意の値 (0-255)

# 現在値確認
/projects/aquapulse/kiosk/brightness.sh status
```

### ダッシュボードURL変更

```bash
sudo sed -i 's|GRAFANA_URL=.*|GRAFANA_URL=http://localhost:3000/d/NEW_UID?kiosk|' \
    /etc/systemd/system/grafana-kiosk.service
sudo systemctl daemon-reload
sudo systemctl restart grafana-kiosk
```

---

## セットアップ手順

### 1. インストール

```bash
cd /projects/aquapulse/kiosk
sudo ./install.sh
```

インストールスクリプトが以下を実行:
- cage, chromium, seatd のインストール
- systemd サービスの登録
- getty@tty1 の無効化

### 2. サービス有効化

```bash
sudo systemctl enable grafana-kiosk
sudo systemctl start grafana-kiosk
```

### 3. 画面スリープ防止（オプション）

```bash
sudo nano /boot/firmware/cmdline.txt
# 末尾に追加: consoleblank=0
```

---

## 設定ファイル

### systemd サービス

`/etc/systemd/system/grafana-kiosk.service`:

```ini
[Unit]
Description=Grafana Kiosk Display (Wayland/Cage + Chromium)
After=network-online.target docker.service seatd.service
Wants=network-online.target
Requires=seatd.service

[Service]
Type=simple
User=koichi
Group=koichi
Environment=XDG_RUNTIME_DIR=/run/user/1000
Environment=GRAFANA_URL=http://localhost:3000/d/aquapulse-display/aquapulse-display?orgId=1&kiosk&refresh=30s
ExecStart=/usr/bin/cage -s -- /projects/aquapulse/kiosk/start-kiosk.sh
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 起動スクリプト

`/projects/aquapulse/kiosk/start-kiosk.sh` - Grafana の起動を待ってから Chromium を起動

---

## 輝度スケジュール

時間帯に応じて自動で輝度を調整（cron で毎時実行）:

| 時間帯 | 輝度 | 用途 |
|--------|------|------|
| 07:00-17:59 | 255 (day) | 日中、太陽光下でも見える |
| 18:00-21:59 | 150 (night) | 夜、室内照明 |
| 22:00-00:59 | 50 (dim) | 就寝前 |
| 01:00-06:59 | 10 (off) | 深夜、最小限 |

設定変更は `/projects/aquapulse/kiosk/brightness-schedule.sh` を編集。

---

## Grafana 設定

### 匿名アクセス（認証スキップ）

`docker-compose.yml` で設定済み:

```yaml
grafana:
  environment:
    GF_AUTH_ANONYMOUS_ENABLED: "true"
    GF_AUTH_ANONYMOUS_ORG_ROLE: "Viewer"
```

### kiosk URL パラメータ

| パラメータ | 効果 |
|------------|------|
| `?kiosk` | ヘッダー・サイドメニュー非表示 |
| `?kiosk=tv` | 上記 + パネルタイトルも非表示 |
| `&refresh=1m` | 1分ごとに自動更新 |

### ダッシュボードデザイン（800x480向け）

- パネル数: 3-4個まで
- フォント: 大きめに設定
- 閾値: 色分けで異常を視覚化

---

## トラブルシューティング

### 画面が真っ暗

```bash
# ログ確認
journalctl -u grafana-kiosk -n 50

# seatd 確認
sudo systemctl status seatd

# 手動テスト
export XDG_RUNTIME_DIR=/run/user/1000
cage -s -- chromium --kiosk --ozone-platform=wayland http://localhost:3000
```

### Grafana に接続できない

```bash
# Grafana 稼働確認
curl http://localhost:3000/api/health

# Docker 確認
docker compose ps
```

### タッチが効かない / 輝度調整できない

現在、ディスプレイの I2C 通信に問題があり、以下の機能が使用不可:

| 機能 | I2C アドレス | 状態 |
|------|-------------|------|
| タッチ | 0x38 (FT5x06) | ❌ probe failed (-121) |
| 輝度制御 | 0x45 (ATtiny88) | ❌ write failed (-121) |
| 映像 (DSI) | - | ✅ 正常 |

**回避策**: PC からダッシュボードを編集すると、ディスプレイ側にも自動反映される。

**今後の確認事項** → [既知の問題](#既知の問題) を参照

### 新しいダッシュボードで "Failed to load dashboard forbidden"

匿名アクセスが有効（`GF_AUTH_ANONYMOUS_ENABLED=true`）でも、**ダッシュボード個別のパーミッション**が設定されていないと forbidden になる。

**診断**:

```bash
# 匿名でアクセス（forbidden になる）
curl -s http://localhost:3000/api/dashboards/uid/YOUR_UID | head -c 100

# 認証ありでパーミッション確認
curl -s -u admin:admin "http://localhost:3000/api/dashboards/uid/YOUR_UID/permissions"
# → [] が返ってきたらパーミッション未設定
```

**解決方法**:

```bash
# Viewer ロールに閲覧権限を追加
curl -X POST -u admin:admin \
  -H "Content-Type: application/json" \
  "http://localhost:3000/api/dashboards/uid/YOUR_UID/permissions" \
  -d '{"items":[{"role":"Viewer","permission":1},{"role":"Editor","permission":2}]}'

# 確認
curl -s http://localhost:3000/api/dashboards/uid/YOUR_UID | head -c 100
# → {"meta": ... が返ってくれば成功

# kiosk 再起動
sudo systemctl restart grafana-kiosk
```

**補足**: GUI で設定する場合は、ダッシュボード設定 → Permissions → Add a permission for → Role: Viewer → View

---

### サービスが停止している

```bash
# 再起動
sudo systemctl restart grafana-kiosk

# 失敗理由の確認
sudo systemctl status grafana-kiosk
journalctl -u grafana-kiosk --no-pager | tail -30
```

---

## ファイル構成

```
/projects/aquapulse/kiosk/
├── install.sh              # インストールスクリプト
├── start-kiosk.sh          # Chromium 起動スクリプト
├── grafana-kiosk.service   # systemd サービス（テンプレート）
├── brightness.sh           # 輝度手動制御
└── brightness-schedule.sh  # 輝度スケジュール（cron用）
```

---

## 関連ドキュメント

| ファイル | 内容 |
|----------|------|
| `docs/ssd-migration-report.md` | SSD 移行後のパス変更 |
| `docs/archive/tui/` | 旧 TUI ダッシュボード（参考用） |

---

## 既知の問題

### I2C 通信エラー（タッチ・輝度）

**症状**:
- タッチ操作が効かない
- 輝度調整ができない（常に最大輝度）

**原因**:
I2C バス 11 でディスプレイのコントローラーと通信できない（エラー -121: EREMOTEIO）

```
dmesg:
  edt_ft5x06 11-0038: touchscreen probe failed
  panel-simple: failed to enable backlight: -121
```

**確認済み事項**:
- DSI（映像）は正常に動作
- I2C デバイス自体は認識されている（`/sys/bus/i2c/devices/11-0038`, `11-0045`）
- 書き込みは sysfs 上では成功するが、実際のハードウェアに反映されない

**今後の対処（TODO）**:
- [ ] リボンケーブルの抜き差し（電源OFF状態で）
- [ ] ケーブルのロックが完全に閉じているか確認
- [ ] 別のリボンケーブルで試す
- [ ] Pi 5 の別の MIPI ポート（CAM0/CAM1）で試す

**現状の運用**:
- 輝度: 常に最大（255）で運用
- 操作: PC から Grafana を編集（自動反映される）

---

*更新日: 2026-03-18*
