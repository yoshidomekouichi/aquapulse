# AquaPulse v1.0 🌊

**Codename:** Living Market Sandbox  
**Concept:** 淡水アクアリウムにおける環境データの収集・可視化・因果推論基盤

## 📌 プロジェクト概要
Raspberry Pi 5 をエッジデバイスとして使用し、水温・pHなどのセンサーデータを収集。
「制御不能な外部要因（気温など）」と「介入（換水など）」がOEC（生態系の健全性）に与える影響を分析するためのデータパイプラインを構築するプロジェクトです。

## 🛠 技術スタック (Planned)
- **Device:** Raspberry Pi 5 (8GB) + NVMe SSD
- **OS:** Raspberry Pi OS Lite (64-bit)
- **Language:** Python 3.11+
- **Database:** TimescaleDB (PostgreSQL)
- **Visualization:** Grafana
- **Infrastructure:** Docker / Docker Compose

## 📂 ディレクトリ構成
- `collector/`: センサーデータ収集モジュール (Python)
- `db/`: データベース初期化スクリプト
- `grafana/`: 可視化設定 (Provisioning)
- `docs/`: ドキュメント（[配線](docs/hardware/wiring/)・[運用ログ](docs/operations/daily-log.md)・[設計](docs/design/)）

## 🚀 現在のステータス: Phase 1 (実センサー)
- [x] プロジェクトディレクトリ構成の確立
- [x] Remote SSH 環境の構築
- [x] Dockerコンテナ化・DB接続
- [x] DS18B20 水温センサー（gpio_temp）
- [x] TDS センサー（gpio_tds / MCP3424 CH1）
- [ ] pH センサー（gpio_ph / MCP3424 CH2）
- [ ] Tapo 温湿度・照明（要 Third-Party 設定）

## 💻 実行方法
```bash
# Docker Compose で起動
docker compose up -d

# SOURCES に gpio_temp,gpio_tds 等を指定（.env で設定）
```