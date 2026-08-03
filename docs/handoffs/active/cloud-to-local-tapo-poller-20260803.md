# Local Agent Handoff — Tapo Auto Poller Implementation

**Date:** 2026-08-02  
**From:** Cloud Agent  
**To:** Local Agent (Mac development environment)

---

## TL;DR

Phase 1a期間中、**Mac上でTapoデバイスを15分間隔でポーリング**し、温度・湿度・ファン/ライトのON/OFF状態をBigQueryに自動記録する実装をお願いします。

お盆期間（1週間不在）に備えて、**Mac常時稼働**（電気代: 約100円/週）で運用します。

---

## 背景

### Phase 1aの課題

- ESP32は水温測定のみ担当
- 手動介入イベント（エアコン/ファン操作）の記録が煩雑
- **→ Tapoデバイスから自動データ取得を実装**

### 取得するデータ

| デバイス | IP | 取得データ | 記録先 |
|---------|-----|-----------|--------|
| **Tapo T310** 温湿度センサー | 192.168.10.103（ハブ経由） | 温度・湿度 | BigQuery `sensor_readings` |
| **Tapo P300** 口1（ファン） | 192.168.10.101 | ON/OFF | BigQuery `control_events` |
| **Tapo P300** 口2（ライト） | 192.168.10.101 | ON/OFF | BigQuery `control_events` |

### 取得不可能なデータ（手動記録）

- ❌ **エアコン状態**（H110 IRリモコンハブ: 192.168.10.102）
  - 理由: IRリモコンは一方向通信のため、状態読み取り不可
  - 対応: 手動で `docs/logs/intervention-events.md` に記録

---

## 技術スタック

### 使用ライブラリ

```bash
pip install python-kasa
```

### 既存実装（参考コード）

Raspberry Pi時代の実装が `collector/src/sources/` にあります：

1. **`collector/src/sources/tapo_sensors.py`**
   - Tapo T310温湿度センサーからデータ取得
   - `python-kasa`を使用（`tapo`ライブラリのエラー回避）
   - 非同期処理（`asyncio`）

2. **`collector/src/sources/tapo_lighting.py`**
   - Tapo P300の各口のON/OFF状態を取得
   - `child.is_on`で状態判定

### 環境変数（必要）

```bash
export TAPO_USERNAME="your-tapo-email@example.com"
export TAPO_PASSWORD="your-tapo-password"
export TAPO_HUB_IP="192.168.10.103"         # T310ハブ
export TAPO_P300_IP="192.168.10.101"        # P300マルチタップ
```

**注意**: これらの認証情報は`.env`ファイルに保存し、`.gitignore`で除外してください。

---

## 実装要件

### 1. Pythonスクリプト作成

**新規ファイル**: `scripts/tapo_poller.py`

#### 実装内容

1. **Tapo T310から温度・湿度を取得**
   - `collector/src/sources/tapo_sensors.py`をベースに
   - H100/H110ハブ経由で子デバイス（T310）にアクセス

2. **Tapo P300の各口のON/OFF状態を取得**
   - `collector/src/sources/tapo_lighting.py`をベースに
   - 口1: ファン、口2: ライト（`sensor_id`で識別）

3. **BigQueryへ送信**
   - 既存の`ingest` Cloud Functionを使用
   - URL: `https://ingest-e4jnfqozuq-an.a.run.app`
   - ペイロード例:
     ```json
     {
       "sensor_id": "tapo_t310_001",
       "sensor_type": "temperature",
       "location": "room",
       "value": 27.5,
       "unit": "celsius",
       "device_id": "tapo_hub",
       "firmware_version": "python-kasa"
     }
     ```

#### エラーハンドリング

- Tapoデバイスへの接続失敗時: リトライ（最大3回）
- BigQuery送信失敗時: ローカルログに記録
- スクリプト異常終了時: cronが次回実行でリカバリ

### 2. cron設定

**実行間隔**: 15分

```bash
# crontabに追加
*/15 * * * * cd /path/to/aquapulse && /usr/bin/python3 scripts/tapo_poller.py >> /tmp/tapo_poller.log 2>&1
```

**または** launchd（macOS推奨）を使用:

```xml
<!-- ~/Library/LaunchAgents/com.aquapulse.tapo-poller.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aquapulse.tapo-poller</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/aquapulse/scripts/tapo_poller.py</string>
    </array>
    <key>StartInterval</key>
    <integer>900</integer> <!-- 15分 = 900秒 -->
    <key>StandardOutPath</key>
    <string>/tmp/tapo_poller.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/tapo_poller_error.log</string>
</dict>
</plist>
```

ロード:
```bash
launchctl load ~/Library/LaunchAgents/com.aquapulse.tapo-poller.plist
```

### 3. Mac設定

#### スリープ無効化

```bash
# バッテリー駆動時もスリープしない
sudo pmset -b sleep 0 disablesleep 1

# 電源接続時もスリープしない
sudo pmset -c sleep 0 disablesleep 1

# ディスプレイのみスリープ（省電力）
sudo pmset -b displaysleep 5
sudo pmset -c displaysleep 10
```

#### 電気代

- MacBook Pro 16インチ（アイドル時20W）
- 1週間（168時間）: 約100円
- 1ヶ月（720時間）: 約450円

---

## テスト手順

### 1. 環境セットアップ

```bash
cd /path/to/aquapulse

# 仮想環境作成（推奨）
python3 -m venv .venv
source .venv/bin/activate

# 依存関係インストール
pip install python-kasa requests
```

### 2. 環境変数設定

```bash
# .envファイル作成
cat > .env << EOF
TAPO_USERNAME=your-email@example.com
TAPO_PASSWORD=your-password
TAPO_HUB_IP=192.168.10.103
TAPO_P300_IP=192.168.10.101
EOF

# .envファイルをロード（テスト時）
export $(cat .env | xargs)
```

### 3. 手動実行テスト

```bash
python3 scripts/tapo_poller.py
```

**期待される出力**:
- Tapo T310から温度・湿度取得成功
- Tapo P300の各口のON/OFF状態取得成功
- BigQueryへの送信成功

### 4. BigQueryで確認

```sql
-- sensor_readings テーブル
SELECT *
FROM `aquapulse-dev.aquapulse.sensor_readings`
WHERE sensor_id LIKE 'tapo_%'
ORDER BY timestamp DESC
LIMIT 10;

-- control_events テーブル
SELECT *
FROM `aquapulse-dev.aquapulse.control_events`
WHERE device_id LIKE 'tapo_%'
ORDER BY timestamp DESC
LIMIT 10;
```

### 5. cron動作確認

```bash
# ログ確認
tail -f /tmp/tapo_poller.log

# 15分後にデータが記録されているか確認
# BigQueryで最新のタイムスタンプを確認
```

---

## スキーマ対応

### sensor_readings（温度・湿度）

```json
{
  "timestamp": "2026-08-02T13:00:00Z",
  "sensor_id": "tapo_t310_001",
  "sensor_type": "temperature",
  "location": "room",
  "value": 27.5,
  "unit": "celsius",
  "device_id": "tapo_hub",
  "firmware_version": "python-kasa"
}
```

### control_events（ファン/ライトON/OFF）

```json
{
  "timestamp": "2026-08-02T13:00:00Z",
  "event_type": "device_state_change",
  "device_id": "tapo_p300_fan",
  "device_type": "smart_plug",
  "action": "state_report",
  "trigger": "scheduled_poll",
  "trigger_value": null,
  "action_details": {
    "state": "on",
    "power_consumption": 15.2
  }
}
```

**注意**: `action_details`はJSON型フィールドで、柔軟なデータ構造を許容します。

---

## 制約とトレードオフ

### 制約

1. **Mac常時稼働が必須**
   - お盆期間中にMacがシャットダウンするとデータ取得停止
   - UPS（無停電電源装置）の使用を推奨

2. **ローカルLANアクセスのみ**
   - 外出先からのアクセスは不可
   - Phase 1bでVPN経由アクセスを検討

3. **エアコン状態は取得不可**
   - IRリモコンの技術的制約
   - 手動記録が必要

### トレードオフ

| 項目 | Mac + cron | GCP + GL.iNet + VPN |
|------|-----------|---------------------|
| 初期コスト | ¥0 | ¥5,000-10,000 |
| 月額コスト | ¥450（電気代） | ¥0-100（GCP） |
| セットアップ時間 | 1-2時間 | 4-8時間 |
| 信頼性 | 中（Mac依存） | 高（GCPインフラ） |
| 実装難易度 | 低 | 中～高 |

**Phase 1a判断**: Mac + cronで実装（シンプル、低コスト、短納期）

---

## 参考ドキュメント

| 優先度 | ファイル | 内容 |
|--------|---------|------|
| 1 | **このファイル** | ローカル実装ガイド |
| 2 | `collector/src/sources/tapo_sensors.py` | T310温湿度取得（既存実装） |
| 3 | `collector/src/sources/tapo_lighting.py` | P300 ON/OFF取得（既存実装） |
| 4 | `docs/guides/cloud-agent-handoff-2026-08.md` | Phase 1a全体コンテクスト |
| 5 | `docs/reference/schema.md` | BigQueryスキーマ定義 |
| 6 | `cloud-functions/ingest/main.py` | ingest Cloud Function実装 |

---

## 次のステップ（ローカルエージェント作業）

1. **スクリプト作成**: `scripts/tapo_poller.py`
   - [ ] Tapo T310温湿度取得実装
   - [ ] Tapo P300 ON/OFF取得実装
   - [ ] BigQuery送信実装
   - [ ] エラーハンドリング

2. **環境セットアップ**:
   - [ ] `python-kasa`インストール
   - [ ] `.env`ファイル作成（認証情報）
   - [ ] 手動実行テスト

3. **cron/launchd設定**:
   - [ ] 15分間隔実行設定
   - [ ] ログ出力設定
   - [ ] 動作確認

4. **Mac設定**:
   - [ ] スリープ無効化
   - [ ] ディスプレイのみスリープ（省電力）

5. **最終確認**:
   - [ ] 3時間の連続運用テスト（12回実行）
   - [ ] BigQueryでデータ確認
   - [ ] エラーログ確認

---

## トラブルシューティング

### Tapo接続エラー

```python
# タイムアウトエラー
# → ネットワーク接続確認、IPアドレス確認

# 認証エラー
# → TAPO_USERNAME/PASSWORDが正しいか確認
# → Tapoアプリで同じ認証情報でログイン可能か確認
```

### BigQuery送信エラー

```python
# 403 Forbidden
# → ingest Cloud FunctionのURL確認
# → GCPプロジェクトの認証確認

# 400 Bad Request
# → ペイロードのJSON形式確認
# → スキーマとの整合性確認
```

### cron/launchd実行エラー

```bash
# cronが実行されない
# → crontabの構文確認: crontab -l
# → ログファイル確認: tail -f /tmp/tapo_poller.log

# launchdが実行されない
# → plistファイルの構文確認
# → launchctl list | grep tapo-poller
# → ログファイル確認
```

---

## 質問・確認事項（ユーザーへ）

実装前に確認が必要な事項：

1. **Tapo認証情報の取得方法**
   - Tapoアプリのログインメールアドレス
   - Tapoアプリのパスワード
   - ユーザーに確認してから`.env`に記載

2. **P300の口の識別方法**
   - 口1: ファン、口2: ライトで正しいか
   - `device_id`でどう識別するか（実機テストで確認）

3. **BigQueryテーブルの書き込み権限**
   - 現在の`ingest` Cloud Functionは認証なしで動作しているか
   - Service Accountの権限確認が必要か

---

**Last updated:** 2026-08-02  
**Cloud Agent Session ID:** cursor/event-logging-setup-0d1c
