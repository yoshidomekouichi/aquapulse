# ADR-0001: Raspberry PiからESP32+GCPへの移行

## ステータス

承認済み（2026-07-05）

## コンテキスト

AquaPulseプロジェクトは、当初Raspberry Pi上でDocker Compose（TimescaleDB、Grafana）を使用して稼働していました。しかし、以下の問題が発生:

- **SSH接続が不安定**: IPアドレス固定、Tailscale使用でも接続不可
- **復旧が困難**: ヘッドレス構成のため、SSH不可 = 完全にアクセス不可
- **物理的制約**: センサーが水槽に固定されており、Raspberry Piを机で開発できない
- **ネットワーク依存**: 日常的な運用でIPアドレスに依存

Raspberry Piが「死んだ」（SSH不可、復旧不可）状態で、新しいアーキテクチャへの移行を検討。

## 検討した選択肢

### 1. Raspberry Piの修復・再セットアップ

- pros: 既存コードを流用できる
- cons: 同じSSH問題が再発する可能性、根本的な解決にならない

### 2. DFRobotなど中間デバイスの使用

- pros: Raspberry Piを机で操作可能
- cons: Raspberry Pi ↔ DFRobot間の通信がIP依存、問題が1段階増える

### 3. ESP32 + GCP Cloud-Native アーキテクチャ（採用）

- pros: 
  - SSH不要（初回セットアップのみUSB接続）
  - IPアドレス依存なし（日常運用）
  - センサー固定の物理制約に対応
  - クラウドネイティブで拡張性が高い
- cons: 
  - 既存コードの完全書き換え
  - GCP費用（月$5-10予想）
  - 新しい技術スタックの学習

## 決定

**ESP32 + GCP Cloud-Native アーキテクチャ** を採用

技術スタック:
- **ハードウェア**: ESP32（MicroPython）
- **センサー**: DS18B20（温度）、Tapo T310/P300
- **クラウド**: GCP（Pub/Sub、Cloud Functions、BigQuery、Cloud Scheduler）
- **可視化**: Grafana Cloud
- **IaC**: Terraform
- **CI/CD**: GitHub Actions

## 影響

### ポジティブ
- SSH問題からの完全解放
- 電源ON/OFF だけで運用可能
- 安全な電源断（スクリプト停止不要）
- クラウドネイティブのメリット（スケーラビリティ、可用性）

### ネガティブ
- 既存コード（Python、Docker Compose）のアーカイブ化
- GCP費用（従来: $0 → 新: 月$5-10）
- MicroPython、GCPの学習コスト

### リスク
- ESP32書き換えは物理接続必須（USB 2m以上のケーブル必要）
- モックテストの限界（センサー読み取りは実機必須）
- 初期開発での試行錯誤（3-5回の書き換え想定）

## 関連資料

- [docs/cloud-migration/](../cloud-migration/)（移行ガイド全体）
- [docs/cloud-migration/00_OVERVIEW.md](../cloud-migration/00_OVERVIEW.md)（システム概要）
- [docs/cloud-migration/01_HARDWARE_SETUP.md](../cloud-migration/01_HARDWARE_SETUP.md)（ESP32の動作モデル）
- [ADR-0002](2026-07-05-archive-directory-structure.md)（既存コードのアーカイブ）
