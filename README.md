# AquaPulse 🌊

**Concept:** 淡水アクアリウムにおける環境データの収集・可視化基盤

## 📌 プロジェクト概要

Raspberry Pi 5 をエッジデバイスとして使用し、水温・湿度・照明状態などのセンサーデータを収集。
Pi Touch Display に Grafana ダッシュボードをキオスク表示し、リアルタイムで水槽の状態を監視する。

## 🛠 技術スタック

| 項目 | 技術 |
|------|------|
| Device | Raspberry Pi 5 (8GB) + NVMe SSD |
| OS | Raspberry Pi OS Lite (Bookworm, 64-bit) |
| Display | Pi Touch Display 1 (800x480) |
| Language | Python 3.11+ |
| Database | TimescaleDB (PostgreSQL) |
| Visualization | Grafana (キオスクモード) |
| Infrastructure | Docker / Docker Compose |

## 📂 ディレクトリ構成

```
aquapulse/
├── collector/       # センサーデータ収集モジュール
├── db/              # データベース初期化・マイグレーション
├── grafana/         # Grafana 設定
├── kiosk/           # キオスクモード設定スクリプト
├── tui/             # TUI ダッシュボード（アーカイブ）
└── docs/            # ドキュメント
    ├── display/     # ディスプレイ・キオスク設定
    ├── hardware/    # 配線・センサー
    ├── operations/  # 運用ログ
    └── design/      # 設計・アーキテクチャ
```

## 🚀 現在のステータス

### センサー

| センサー | 状態 | ソース |
|----------|------|--------|
| DS18B20 水温 | ✅ 稼働中 | `gpio_temp` |
| Tapo 温湿度 (T310) | ✅ 稼働中 | `tapo_sensors` |
| Tapo P300 照明状態 | ✅ 稼働中 | `tapo_lighting` |
| TDS センサー | ⚠️ 瓶測定運用 | `gpio_tds` |
| pH センサー | 🔜 未実装 | - |

### ディスプレイ

| 機能 | 状態 |
|------|------|
| Grafana キオスク表示 | ✅ 稼働中 |
| タッチ操作 | ❌ I2C エラー |
| 輝度調整 | ❌ I2C エラー |

## 💻 実行方法

```bash
# Docker Compose で起動
cd /projects/aquapulse
docker compose up -d

# キオスクモードを有効化
sudo systemctl enable grafana-kiosk
sudo systemctl start grafana-kiosk
```

## 📖 ドキュメント

- [Grafana キオスク設定](docs/display/grafana-kiosk.md)
- [配線記録](docs/hardware/wiring/)
- [作業ログ](docs/operations/daily-log.md)
- [アーキテクチャ設計](docs/design/architecture.md)
