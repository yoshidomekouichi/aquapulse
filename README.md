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

## 🚀 現在のステータス: Phase 0 (Mock)
- [x] プロジェクトディレクトリ構成の確立
- [x] Remote SSH 環境の構築
- [x] Mockデータコレクター (`src/mock_collector.py`) の動作確認
- [ ] Dockerコンテナ化
- [ ] DB接続

## 💻 実行方法 (開発中)
```bash
# 仮想環境に入る
cd collector
source .venv/bin/activate

# Mockデータを流す
python src/mock_collector.py