# Mac Tapo Poller

**Phase 1a 観測レイヤー** — Tapo デバイスを LAN から読み取り、GCP `ingest` → BigQuery に記録する。

## 現実的な構成（今後も想定）

```
┌─────────────────────────────────────────────────────────────┐
│  自宅 LAN (192.168.10.x)                                     │
│                                                              │
│  Tapo H100/H110 ── T310 温湿度 ──┐                           │
│  Tapo P300 (口1 ファン / 口2 ライト) ──┤                       │
│                                      │                       │
│  [Mac tapo_poller] ◄── python-kasa ─┘  15分間隔             │
│       │                                                      │
│       │ HTTPS POST                                           │
└───────┼──────────────────────────────────────────────────────┘
        ▼
  Cloud Functions: ingest
        ▼
  BigQuery: sensor_readings
        │
        ├── room_temperature / room_humidity  (T310)
        ├── power_state (fan ON/OFF, light ON/OFF)
        │
        └── (将来) ESP32 → 水温 ds18b20_001 / aquarium

  Grafana: 水温 + 室温 + ファン状態を同一タイムラインで表示
```

### 役割分担

| コンポーネント | 役割 | 間隔 |
|----------------|------|------|
| **Mac poller** | Tapo 室温・湿度・P300 ON/OFF | 15分 |
| **ESP32**（後日） | 水槽水温 DS18B20 | 60秒 |
| **ingest** | 共通入口 → BigQuery | — |
| **intervention-events.md** | エアコン等 Tapo 非対応の手動操作 | 随時 |

### なぜ Mac か

- Tapo は **python-kasa が LAN 前提**（GCP から届かない — ADR-0007/0008）
- ESP32 から Tapo 直接制御・取得は **暗号化の都合で不可**
- Mac は **開発機＋常時電源** で poller に最適（お盆 ~100円/週）
- Phase 1b 自動化後も **観測ログ** として残せる

### 将来の移行パス

| 段階 | poller の置き場 |
|------|-----------------|
| Phase 1a（今） | Mac + launchd 15分 |
| Phase 1b | Mac 継続 or GL.iNet 常時機 |
| Phase 2+ | Cloud Scheduler + LAN エージェント（VPN 後） |

**ingest のペイロード形式は変えない** — poller の実行場所だけ差し替え可能。

---

## 今夜から試す（クイックスタート）

### 1. 依存関係

```bash
cd ~/Projects/aquapulse
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/requirements-tapo-poller.txt
```

### 2. `.env`（リポジトリ直下）

```bash
cat >> .env << 'EOF'
TAPO_USERNAME=your-tapo-email@example.com
TAPO_PASSWORD=your-tapo-password
TAPO_HUB_IP=192.168.10.103
TAPO_P300_IP=192.168.10.101
TAPO_P300_FAN_INDEX=0
TAPO_P300_LIGHT_INDEX=1
INGEST_URL=https://ingest-e4jnfqozuq-an.a.run.app
EOF
```

（Secret Manager と同じ Tapo 認証情報で OK）

### 3. ドライラン（LAN 接続確認）

```bash
source .venv/bin/activate
python scripts/tapo_poller.py --dry-run
```

### 4. 本番 POST（今夜1回）

```bash
python scripts/tapo_poller.py
```

### 5. BigQuery 確認

```bash
bq query --use_legacy_sql=false \
  'SELECT timestamp, sensor_id, sensor_type, value, unit
   FROM `aquapulse-dev.aquapulse.sensor_readings`
   WHERE device_id = "mac_poller_v1"
   ORDER BY timestamp DESC LIMIT 20'
```

### 6. 15分間隔で今夜から回す（launchd）

```bash
# テンプレートをコピーしてパスを確認
cp scripts/launchd/com.aquapulse.tapo-poller.plist.template \
   ~/Library/LaunchAgents/com.aquapulse.tapo-poller.plist

# ProgramArguments の python パスを .venv に合わせて編集
launchctl load ~/Library/LaunchAgents/com.aquapulse.tapo-poller.plist
```

Mac がスリープすると poller が止まる。**お盆前は電源接続 + スリープ無効**を推奨。

---

## 記録される sensor_id

| sensor_id | 内容 |
|-----------|------|
| `tapo_{device_id}` | T310 温度・湿度 |
| `tapo_p300_fan` | P300 口1 ファン ON/OFF (0/1) |
| `tapo_p300_light` | P300 口2 ライト ON/OFF |

口の番号は `TAPO_P300_FAN_INDEX` / `TAPO_P300_LIGHT_INDEX` で変更可。

---

## 関連ドキュメント

- [local-agent-handoff-tapo-poller.md](../../docs/guides/local-agent-handoff-tapo-poller.md)
- [cloud-agent-handoff-2026-08.md](../../docs/guides/cloud-agent-handoff-2026-08.md)
