# AquaPulse ドキュメント

ドキュメントのナビゲーション。

---

## 📁 フォルダ構成

| フォルダ | 内容 |
|----------|------|
| [**display/**](display/) | ディスプレイ・キオスクモード |
| [**hardware/**](hardware/) | ハードウェア（配線・センサー） |
| [**operations/**](operations/) | 運用ログ・復旧手順 |
| [**design/**](design/) | 設計・アーキテクチャ・評価指標 |
| [**archive/**](archive/) | 過去のドキュメント（参考用） |

---

## クイックリンク

### ディスプレイ

| ドキュメント | 説明 |
|--------------|------|
| [Grafana キオスク](display/grafana-kiosk.md) | Pi Touch Display に Grafana を全画面表示 |

### ハードウェア

| ドキュメント | 説明 |
|--------------|------|
| [配線記録（最新）](hardware/wiring/) | ラズパイピン配置・センサー接続 |
| [改善計画・試行ログ](hardware/improvement-plan.md) | ハードウェア改善の計画 |

### 設計

| ドキュメント | 説明 |
|--------------|------|
| [アーキテクチャ](design/architecture.md) | データ基盤・ML 設計方針 |
| [評価指標](design/metrics.md) | KGI/KPI・プロキシ指標の設計 |
| [Collector ソース一覧](design/collector-sources.md) | センサーソース・環境変数・sensor_id |

### 運用

| ドキュメント | 説明 |
|--------------|------|
| [日次ログ](operations/daily-log.md) | 作業記録・トラブル対応 |
| [復旧手順](operations/recovery-runbook.md) | OS 再インストール後・ネットワーク障害時の手順 |
| [SSD 移行レポート](operations/ssd-migration-report.md) | SSD 起動移行の問題と解決 |
| [SSD 移行ガイド](operations/SSD_MIGRATION_GUIDE.md) | SSD 起動への移行手順 |
| [Tapo ステータスレポート](operations/tapo-status-report.md) | Tapo デバイスの状態調査 |

---

## アーカイブ

| フォルダ | 内容 |
|----------|------|
| [archive/tui/](archive/tui/) | 旧 TUI ダッシュボード（Grafana キオスクに移行済み） |
