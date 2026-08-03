# Local Agent 引き継ぎ: Grafana 完了 → アラート + ESP32

## 1. メタ情報

- **送信元**: Local Agent（Mac セッション）
- **送信先**: Cloud Agent
- **作成日時**: 2026-08-04 00:50 JST
- **優先度**: 🔴 High
- **期限**: 2026-08-08（Phase 1a）
- **関連**: ADR-0008, `docs/guides/cloud-agent-handoff-2026-08.md`

## 2. 前提知識・参照ドキュメント

**必ず最初に読む:**

1. `docs/guides/cloud-agent-handoff-2026-08.md` — LIVE 状態・GCP・Phase 1a スコープ
2. `docs/operations/tapo-poller-mac-setup-log-2026-08-03.md` — Tapo LAN 試行錯誤（**再調査不要**）
3. `docs/operations/grafana-bigquery-setup-2026-08-03.md` — Grafana セットアップ手順
4. `docs/decisions/0008-phase1-split-monitoring-only.md` — 監視のみ・手動ファン

**コード参照:**

- `grafana/dashboards/aquapulse-mac-poller-bigquery.json` — ダッシュボード v3（未 push）
- `scripts/tapo_poller.py`, `scripts/run-tapo-poller.sh` — Mac poller（**Local のみ稼働**）
- `cloud-functions/ingest/main.py` — ingest エンドポイント
- `docs/tutorials/getting-started-esp32.md` — ESP32 チュートリアル

## 3. 現在の状況サマリー

### 達成済み ✅

- Mac Tapo poller → `ingest` → BigQuery（`device_id=mac_poller_v1`）**稼働中**
- Hub `192.168.10.110` / P300 `192.168.10.104` / WiFi `aterm-b88a47-2s`
- Grafana Cloud: BigQuery datasource **接続成功**
- ダッシュボード v3 Import 成功（スマホ UI、時系列・State timeline 修正済み）
- GCP: `grafana-bigquery@aquapulse-dev` SA 作成、Cloud Resource Manager API 有効化

### 未着手 🔲

- Grafana アラート（室温 ≥ 28°C → Email）— **ユーザー操作が必要**（Grafana Cloud ログイン）
- ESP32 + DS18B20 配線・WiFi・ingest POST
- ダッシュボードに水温パネル追加（ESP32 データ到着後）
- 3日連続監視テスト

### ブロッカー

- **なし**（Tapo LAN は解決済み。触らないこと）

## 4. 技術スタック

- **Local**: Mac cron, python-kasa, Tapo LAN
- **Cloud**: GCP `aquapulse-dev`, Cloud Functions Gen2 `ingest`, BigQuery `aquapulse.sensor_readings`
- **可視化**: Grafana Cloud Free（`microteal1944`）、BigQuery datasource plugin
- **Edge（次）**: ESP32 + MicroPython + DS18B20

## 5. 実装要件

### 5.1 Cloud Agent が担当できる

- [ ] ESP32 `main.py`（DS18B20 読取 → WiFi → POST ingest）
- [ ] `secrets.py.example` / ドキュメント更新
- [ ] ダッシュボード JSON に水温パネル追加
- [ ] Secret Manager `tapo-p300-ip` → `.104` 更新（ユーザー指示後）
- [ ] 未 push ファイルの PR 作成（dashboard JSON, handoff, cloud-agent-handoff 更新）

### 5.2 Local / ユーザーが担当（Cloud Agent 不可）

- [ ] Grafana Alert rule 作成（Grafana UI、メール Contact point）
- [ ] Mac poller 継続運用（cron、caffeinate）
- [ ] ESP32 USB 書き込み・実機テスト
- [ ] `~/grafana-bigquery-key.json` の管理（**git 禁止**）

## 6. 環境情報

| 項目 | 値 |
|------|-----|
| GCP プロジェクト | `aquapulse-dev` |
| ingest URL | `https://ingest-e4jnfqozuq-an.a.run.app` |
| BigQuery | `aquapulse-dev.aquapulse.sensor_readings` |
| Grafana SA | `grafana-bigquery@aquapulse-dev.iam.gserviceaccount.com` |
| Grafana ダッシュボード UID | `aquapulse-mac-poller-bq` |

**Local のみ（Cloud Agent はアクセス不可）:**

- Tapo `.env`（gitignored）
- `~/grafana-bigquery-key.json`
- Mac LAN `192.168.10.x`

## 7. 依存関係

- **事前完了**: Tapo poller ✅, Grafana datasource ✅
- **並行可能**: ESP32 コード作成 || ユーザーが Grafana アラート設定
- **後続**: ESP32 データ確認 → ダッシュボード水温パネル → 3日監視テスト

## 8. 詳細タスクリスト

### T1: リポジトリ同期（最優先）

```bash
git pull origin main
# 未 merge のローカル変更を PR に:
# - grafana/dashboards/aquapulse-mac-poller-bigquery.json
# - docs/guides/cloud-agent-handoff-2026-08.md（Grafana 完了反映）
# - docs/handoffs/（このファイル + INDEX 更新）
```

### T2: ESP32 ファームウェア

1. DS18B20 1-Wire 読取
2. WiFi 接続（`secrets.py`）
3. POST JSON to ingest（`device_id=esp32_001`, `sensor_type=temperature`）
4. ローカルテスト手順を README に記載

### T3: Grafana アラート（ユーザー向け手順書）

Cloud Agent は Grafana にログインできない。手順を doc に書きユーザーに依頼:

- Query: 直近5分 `room_temperature` MAX from BigQuery
- Condition: > 28
- Contact point: Email

### T4: ダッシュボード v3 マージ

`grafana/dashboards/aquapulse-mac-poller-bigquery.json` の要点:

- BigQuery エイリアスは ASCII のみ（`"室温"` は構文エラー）
- 時間フィルタ: `TIMESTAMP_MILLIS($__from/$__to)`
- State timeline: `CAST(ROUND(value) AS INT64) AS state`

## 9. 成功基準

| レベル | 基準 |
|--------|------|
| 最低限 | PR merge、ESP32 コード草案、handoff INDEX 更新 |
| 完全 | ESP32 が BigQuery に水温投稿 + アラート手順 doc + dashboard JSON on main |

## 10. テスト・検証

```bash
# BigQuery（Cloud Agent 可）
./scripts/check-poller-data.sh 24

# ingest テスト
curl -X POST "https://ingest-e4jnfqozuq-an.a.run.app" \
  -H "Content-Type: application/json" \
  -d '{"sensor_id":"ds18b20_001","sensor_type":"temperature","location":"aquarium","value":25.5,"unit":"celsius","device_id":"esp32_001","firmware_version":"v1.0.0"}'
```

## 11. トラブルシューティング

| 症状 | 対処 |
|------|------|
| Grafana No data | dashboard v3 SQL 確認（上記 T4） |
| poller 停止 | Local 問題。Cloud Agent は触らない |
| GCP→Tapo 不可 | 設計通り（ADR-0008） |
| P300 接続失敗 | setup log 参照。サードパーティ連携 ON |

## 12. ロールバック

- poller: cron 停止、`scripts/run-tapo-poller.sh` 無効化
- Grafana: 旧 dashboard Import で上書き
- ESP32: USB 再フラッシュ

## 13. 制約

- **Phase 1a**: ファン自動制御なし（Tapo アプリ手動）
- **commit/deploy**: ユーザー明示指示までしない（`.cursor/rules/20-version-control.mdc`）
- **Tapo LAN**: poller 壊れるまで再トラブルシュート禁止

## 14. セキュリティ

- `~/grafana-bigquery-key.json` — git 禁止
- Tapo 認証情報 — `.env` のみ
- Grafana Cloud パスワード — ユーザー管理

## 15. 完了報告フォーマット

- 実施タスクと PR URL
- ESP32 コードのパスとテスト手順
- 未完了（Grafana アラート等）とユーザーアクション
- 次の引き継ぎ先（Local へ ESP32 実機テストなど）

## 16. 次のアクション

**Cloud Agent 開始プロンプト:**

```
引き継ぎドキュメント読み込み。
docs/handoffs/INDEX.md → docs/handoffs/active/local-to-cloud-grafana-alert-esp32-20260804.md
続けて docs/guides/cloud-agent-handoff-2026-08.md。
Phase 1a 期限 2026-08-08。日本語。commit/deploy は指示まで不要。
```

---

**Local Agent セッション終了:** 2026-08-04 00:50 JST
