# Mac Tapo Poller セットアップログ（2026-08-02〜03）

**目的:** 試行・エラー・成功を時系列で残し、Cloud Agent / 将来の自分が再調査しないようにする。

**最終状態（2026-08-03 01:05 JST）:** ✅ Hub + P300 → ingest → BigQuery 動作。cron 15分 + caffeinate スリープ防止。

---

## 現在の LAN / .env（正）

| 機器 | SSID | IP | .env |
|------|------|-----|------|
| Mac | `aterm-b88a47-2s` (2.4GHz) | DHCP | — |
| H100 + T310 | `-2s` | **192.168.10.110** | `TAPO_HUB_IP` |
| P300 | `-2s` | **192.168.10.104** | `TAPO_P300_IP` |

**ルーター:** Aterm 3000D4AX — メッシュWi-Fi **OFF**、セカンダリ `-2s` **ネットワーク分離 OFF**（2.4GHz）

**Tapo:** 私 → **音声アシスタント** → **サードパーティ連携 ON**（OFF→10秒→ON で P300 が python-kasa 可に）

---

## 時系列（try → error → fix）

### 1. GCP thermostat → Tapo（事前検証）

| Try | Error | Fix / 結論 |
|-----|-------|------------|
| Cloud Function `thermostat` → P300 `.101` | `TimeoutError` | GCP から LAN 不可 → Phase 1a は手動ファン（ADR-0008） |

### 2. Mac poller — SSID 隔離（Mac `-5p`, P300 `-5s`）

| Try | Error | Fix / 結論 |
|-----|-------|------------|
| poller dry-run | Hub OK, P300 timeout | `-5p` ↔ `-5s` 間 LAN 不通（セカンダリ分離 or バンドステアリング） |
| ping / kasa `.101` | ARP incomplete | P300 はクラウドオンラインでも LAN 未到達 |
| ネットワーク分離 OFF 確認 | 既に OFF 表示 | 単体では不十分 |

### 3. Mac を `-5s` に変更

| Try | Error | Fix / 結論 |
|-----|-------|------------|
| Mac → `-5s` | Hub + P300 両方 timeout | Mac は **5GHz ch36** の `-5s`、P300 は **2.4GHz** — 帯域が違う |
| broadcast discover | H100 `.103` のみ | P300 LAN 上に見えない |

### 4. P300 を `-5s` 再セットアップ

| Try | Error | Fix / 結論 |
|-----|-------|------------|
| Tapo セットアップ | `-5p` が一覧に出ない | P300 は 2.4GHz 専用 → `-5s` のみ表示は正常 |
| 接続成功 `.101` | poller 仍 timeout | IP 変更 + 分離 ON のまま等 |
| LAN scan | MAC at **`.104`** | `.env` `TAPO_P300_IP=192.168.10.104` |

### 5. ルーター管理画面が開けない（`-2s` 接続時）

| Try | Error | Fix / 結論 |
|-----|-------|------------|
| `aterm.me` / `192.168.10.1` | `ERR_CONNECTION_TIMED_OUT` | ping OK, TCP 80 timeout → **セカンダリ分離 ON** |
| Mac → `-5p` | 管理画面 OPEN | プライマリから設定変更 |

### 6. メッシュ OFF + `-2s` 分離 OFF

| Try | Error | Fix / 結論 |
|-----|-------|------------|
| Wi-Fi基本設定 メッシュ OFF → 再起動 | SSID `-2p`/`-2s` に分離 | 正しい方向 |
| `-2s` 分離 ON（スクショ） | poller 全滅 | **分離 → OFF → 再起動** で LAN 開通 |
| `-2p` パスワード | シールの `-5p` キーでは不可 | 2.4GHz プライマリは別キー（管理画面で確認） |

### 7. H100 を `-2s` 接続

| Try | Error | Fix / 結論 |
|-----|-------|------------|
| ユーザー報告 IP `.119` | kasa timeout at `.119` | discover で H100+T310 は **`.110`** |
| `.env` → `.110` | Hub 2 readings OK | 室温・湿度 ingest OK |

### 8. P300 — TPAP 暗号

| Try | Error | Fix / 結論 |
|-----|-------|------------|
| poller P300 | `encrypt_type='TPAP'` Unsupported | python-kasa 0.10.2 は TPAP 非対応 |
| サードパーティ連携 | メニューが公式画像と違う | **私 → 音声アシスタント → サードパーティ連携**（日本版） |
| 既に ON | 仍 TPAP | **OFF → 10秒 → ON**（`-2s` 接続中） |
| 再 poller | ✅ P300 5 outlets + Hub 2 | **7件 ingest OK** |

---

## 運用（Mac）

```bash
# poller 手動
cd ~/Projects/aquapulse && ./scripts/run-tapo-poller.sh

# cron（済）
*/15 * * * * .../run-tapo-poller.sh >> /tmp/aquapulse-tapo-poller.log 2>&1

# スリープ防止
./scripts/keep-mac-awake.sh start   # caffeinate -dimss
# 恒久（電源接続時）: sudo pmset -c sleep 0
```

**注意:** Mac スリープ / フタ閉じ / Wi-Fi 切断で poller 停止。`-2s` 維持。

---

## BigQuery 確認

```bash
bq query --use_legacy_sql=false --project_id=aquapulse-dev \
'SELECT timestamp, sensor_id, sensor_type, value, unit
 FROM `aquapulse-dev.aquapulse.sensor_readings`
 WHERE device_id="mac_poller_v1"
 ORDER BY timestamp DESC LIMIT 20'
```

2026-08-03 01:05 JST 時点: 室温 ~25.9°C、湿度 ~66%、ファン ON。

---

## 未完了（Cloud Agent 向け TODO）

| 項目 | 状態 |
|------|------|
| Grafana Cloud + BigQuery datasource | 🔲 未構築（初回 30–45分） |
| BigQuery 用 dashboard JSON | 🔲 なし（既存 grafana/ は PostgreSQL 用） |
| ESP32 + DS18B20 → ingest | 🔲 |
| Grafana alert ≥28°C | 🔲 |
| ルーター DHCP 固定（Hub `.110`, P300 `.104`） | 🔲 推奨 |
| Secret Manager `tapo-p300-ip` | ⚠️ まだ `.101` の可能性 — GCP 更新要 |
| poller launchd（cron 代替） | 🔲 テンプレあり、未 load |

---

## 学び（再発防止）

1. **`-5p`/`-5s` の「5」は 5GHz ではない** — プライマリ/セカンダリ。バンドステアリング ON 時は 2.4/5 同名。
2. **Tapo アプリ「オンライン」≠ LAN 到達** — poller は LAN 必須。
3. **セカンダリ SSID 分離 ON** → ルーター管理画面・LAN 機器間とも不通。
4. **P300 ファーム 1.4.0** → TPAP。サードパーティ連携の OFF→ON が必要なことが多い。
5. **Hub IP は DHCP で変わる** — 固定化 or discover ロジック検討。

---

**Last updated:** 2026-08-03 01:16 JST
