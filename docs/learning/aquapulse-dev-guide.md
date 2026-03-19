# AquaPulse 開発学習ガイド

**開発初心者向け・網羅的な技術解説書**

アクアリウム IoT プロジェクト「AquaPulse」で使った技術、構成、ツール、コードのロジック、技術選定、物理センサー接続まで、開発の全体像を学ぶためのガイドです。O'Reilly の技術書のように、背景から実装まで丁寧に解説します。

---

## 目次

1. [プロジェクト概要](#1-プロジェクト概要)
2. [技術スタックと技術選定](#2-技術スタックと技術選定)
3. [アーキテクチャ](#3-アーキテクチャ)
4. [物理的なセンサー接続](#4-物理的なセンサー接続)
5. [ディレクトリ構成](#5-ディレクトリ構成)
6. [コードのロジックとライブラリ](#6-コードのロジックとライブラリ)
7. [Docker とコンテナ](#7-docker-とコンテナ)
8. [データベース設計](#8-データベース設計)
9. [通知と運用](#9-通知と運用)
10. [学習のための次のステップ](#10-学習のための次のステップ)
11. [環境変数リファレンス](#11-環境変数リファレンス)
12. [トラブルシューティング](#12-トラブルシューティング)
13. [コードの詳細解説（発展）](#13-コードの詳細解説発展)
14. [TimescaleDB の Continuous Aggregates](#14-timescaledb-の-continuous-aggregates将来の-ml-用)
15. [外から・スマホから読む方法](#15-外からスマホから読む方法)
16. [まとめ](#16-まとめ)

---

## 1. プロジェクト概要

### 1.1 何を作っているか

**AquaPulse** は、淡水アクアリウムの環境データ（水温、気温、湿度、照明 ON/OFF）を収集し、可視化する IoT システムです。

- **目的**: 魚や水草の健康維持に最適な水質・環境を、データに基づいて管理する
- **将来**: 因果推論や機械学習で「何が水質に効くか」を分析し、異常検知や予測を行う

### 1.2 システムの流れ（3行で）

```
センサー（水温・気温・湿度・照明） → データベース（TimescaleDB） → ダッシュボード（Grafana）
```

### 1.3 ハードウェア構成

| 機器 | 役割 |
|------|------|
| Raspberry Pi 5 (8GB) | エッジ端末。センサー収集・DB・Grafana を実行 |
| Pi Touch Display 1 (7インチ) | ダッシュボードの常時表示（キオスクモード） |
| DS18B20 | 水温センサー（1-Wire / GPIO） |
| MCP3424 | アナログ-デジタル変換（I2C）。TDS・pH センサー用 |
| Tapo H100 + T310 | 気温・湿度センサー（Wi-Fi） |
| Tapo P300 | 照明用マルチタップ（Wi-Fi）。ON/OFF 状態を取得 |

---

## 2. 技術スタックと技術選定

### 2.1 一覧表

| レイヤー | 技術 | 選定理由 |
|----------|------|----------|
| 言語 | Python 3.11 | センサー制御・データ処理のライブラリが豊富。型ヒントで可読性向上 |
| DB | TimescaleDB (PostgreSQL 14) | 時系列データに特化。Continuous Aggregates で集約が容易 |
| 可視化 | Grafana | 時系列ダッシュボードの定番。PostgreSQL 対応 |
| 実行環境 | Docker / Docker Compose | 依存関係の隔離、再現性、デプロイの簡素化 |
| デバイス | Raspberry Pi 5 | GPIO・I2C・1-Wire 対応。低消費電力で常時稼働向き |

### 2.2 なぜ TimescaleDB か

- **時系列データの最適化**: タイムスタンプでパーティションし、大量データでも高速
- **Continuous Aggregates**: 1分・5分粒度の集約を DB 側で事前計算（将来の ML 用）
- **gapfill**: 欠損区間の補間が標準機能
- **PostgreSQL 互換**: 既存の SQL やツールがそのまま使える

### 2.3 なぜ Docker か

- **環境の再現性**: 「手元では動くが本番で動かない」を防ぐ
- **依存の隔離**: Python のバージョンやライブラリをコンテナ内に閉じ込める
- **デプロイの単純化**: `docker compose up -d` で一括起動

### 2.4 なぜ Grafana か

- **時系列グラフが得意**: センサーデータの可視化に最適
- **PostgreSQL 対応**: SQL で柔軟にクエリ
- **キオスクモード**: 匿名アクセスでログイン不要の常時表示が可能

---

## 3. アーキテクチャ

### 3.1 全体図

```
┌─────────────────────────────────────────────────────────────────┐
│                     Raspberry Pi (Edge)                           │
├─────────────────────────────────────────────────────────────────┤
│  Sensors                                                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │ gpio_temp   │ │ gpio_tds    │ │ tapo_sensors│ │tapo_lighting│ │
│  │ (1-Wire)    │ │ (I2C)       │ │ (Wi-Fi)     │ │ (Wi-Fi)     │ │
│  │ 60s         │ │ 60s         │ │ 300s        │ │ 300s        │ │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ │
│         │               │               │               │        │
│         └───────────────┴───────────────┴───────────────┘        │
│                                 │                                 │
│                         collector/main.py                         │
│                    (メインループ + 独立スレッド)                     │
│                                 │                                 │
│                                 ▼                                 │
│                         db/writer.py                              │
│                    (sensor_readings, ops_metrics)                 │
└─────────────────────────────────┼─────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  TimescaleDB (PostgreSQL)                                         │
│  sensor_readings (Raw)  /  ops_metrics (ヘルス)                    │
└─────────────────────────────────┼─────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  Grafana (PC / 7" Touch Display)                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 設計思想（なぜこうなっているか）

| 方針 | 理由 |
|------|------|
| **非同期・独立間隔** | Tapo は API 制限がある（5分間隔）。水温は高頻度で取得したい。同期させると複雑になる |
| **Raw データをそのまま保存** | 取得時刻を丸めない。後から別の時間窓で分析できる |
| **特徴量は DB で生成** | Continuous Aggregates で 1分・5分粒度を事前計算。Python でやると重い |
| **学習は PC、推論はエッジ** | 学習は計算資源が必要。推論は軽量でリアルタイム性が重要。分離する |

---

## 4. 物理的なセンサー接続

### 4.1 接続方式の種類

| 方式 | 説明 | 本プロジェクトでの使用例 |
|------|------|--------------------------|
| **1-Wire** | 1本のデータ線で通信。GPIO 1本で複数デバイス | DS18B20 水温センサー |
| **I2C** | 2本（SDA, SCL）で複数デバイス。アドレスで識別 | MCP3424 ADC（TDS・pH） |
| **Wi-Fi** | 無線。IP アドレスで通信 | Tapo H100, P300 |

### 4.2 Raspberry Pi のピン配置（v2.0）

| 物理ピン | BCM GPIO | 役割 | 接続先 |
|:--------:|:--------:|------|--------|
| 1 | - | 3.3V | DS18B20 VDD |
| 6 | - | GND | DS18B20 GND |
| 7 | 4 | 1-Wire データ | DS18B20 データ |
| 3 | 2 | I2C SDA | MCP3424 SDA |
| 5 | 3 | I2C SCL | MCP3424 SCL |
| 17 | - | 3.3V | ブレッドボード（TDS/pH 用） |
| 9 | - | GND | ブレッドボード GND |

### 4.3 DS18B20（水温センサー）

- **配線**: 3.3V, GND, データ（GPIO 4）
- **プルアップ**: 4.7kΩ（データ-3.3V 間）。モジュール内蔵の場合は不要
- **config.txt**: `dtoverlay=w1-gpio` で 1-Wire を有効化
- **読み取り**: `/sys/bus/w1/devices/28-*/w1_slave` を読む。`t=12345` がミリ度

### 4.4 MCP3424（I2C ADC）

- **アドレス**: 0x68（Adr0, Adr1 を GND に接続）
- **CH1**: TDS センサーの電圧 → ppm 換算
- **CH2**: pH センサー（将来）
- **重要**: CH1- (Pin 2) は GND に接続すること。浮いていると不安定

### 4.5 Tapo（Wi-Fi）

- **H100**: ハブ。子デバイス T310/T315 で気温・湿度を取得
- **P300**: マルチタップ。各口の ON/OFF を取得
- **認証**: メールアドレス + パスワード（Tapo アプリと同じ）

---

## 5. ディレクトリ構成

```
aquapulse/
├── collector/           # センサー収集モジュール
│   ├── src/
│   │   ├── main.py      # エントリポイント
│   │   ├── notify.py    # 通知（Email、IP変更、収集失敗）
│   │   ├── db/writer.py # DB 書き込み
│   │   └── sources/     # 各センサーソース
│   ├── scripts/         # 診断・テスト用
│   ├── Dockerfile
│   └── requirements.txt
├── db/
│   ├── init/            # 初期スキーマ（コンテナ初回起動時に実行）
│   └── migrations/      # マイグレーション
├── grafana/
│   └── dashboards/      # ダッシュボード JSON
├── kiosk/               # キオスクモード用スクリプト
├── docs/
│   ├── design/          # 設計ドキュメント
│   ├── hardware/        # 配線図
│   ├── operations/      # 運用ログ
│   └── learning/        # 本ガイド
├── docker-compose.yml
└── .env                 # 環境変数（Git に含めない）
```

---

## 6. コードのロジックとライブラリ

### 6.1 共通フォーマット（reading）

全ソースは同じ形式の辞書リストを返します。

```python
{
    "time": datetime (UTC),
    "sensor_id": str,   # 例: "ds18b20_water_28_00001117a4e0"
    "metric": str,      # 例: "temperature", "humidity", "tds", "power_state"
    "value": float,
    "source": str       # オプション。例: "python-kasa"
}
```

### 6.2 ソースの動的ロード（main.py）

環境変数 `SOURCES` で有効なソースを指定し、動的に import します。

```python
SOURCES_RAW = os.getenv("SOURCES", os.getenv("SOURCE", "mock"))
SOURCES = [s.strip() for s in SOURCES_RAW.split(",") if s.strip()]

def _load_source(name):
    if name == "tapo_sensors":
        if os.getenv("TAPO_BACKEND") == "tapo":
            from sources.tapo_sensors_tapo import get_readings
        else:
            from sources.tapo_sensors import get_readings
        return get_readings
    elif name == "tapo_lighting":
        from sources.tapo_lighting import get_readings
        return get_readings
    # ... gpio_temp, gpio_tds, mock

SOURCE_LOADERS = {name: _load_source(name) for name in SOURCES}
```

**ポイント**: 条件分岐でライブラリを切り替え（tapo vs python-kasa）。遅延 import で未使用ソースの読み込みを避ける。

### 6.3 メインループと独立スレッド

Tapo 等はメインループで 5 分間隔。gpio_temp, gpio_tds は別スレッドで 60 秒間隔。

```python
# メインループ（Tapo 等）
while True:
    for name, get_readings_fn in other_sources.items():
        readings, health = collect_with_health(name, get_readings_fn, conn, ops_conn)
        all_readings.extend(readings)
        all_health.extend(health)
    for r in all_readings:
        save_reading(conn, r)
    save_ops_metrics_batch(ops_conn, all_health)
    time.sleep(SAMPLE_INTERVAL)  # 300 秒

# 独立スレッド（gpio_temp）
def _gpio_temp_loop(stop_event):
    while not stop_event.is_set():
        try:
            readings = get_readings()
            for r in readings:
                save_reading(conn, r)
        except Exception as e:
            print(f"[gpio_temp] Failed: {e}")
        stop_event.wait(GPIO_TEMP_INTERVAL)  # 60 秒
```

**ポイント**: `threading.Event` で graceful shutdown。各ソースは独立した間隔で動作。

### 6.4 1-Wire 読み取り（gpio_temp.py）

```python
def _read_temperature_sync(device_path: str) -> Optional[float]:
    with open(device_path, "r") as f:
        content = f.read()
    for line in content.strip().split("\n"):
        if "t=" in line:
            temp_str = line.split("t=")[-1].strip()
            temp_millideg = int(temp_str)
            return round(temp_millideg / 1000.0, 2)  # ミリ度 → 摂氏
    return None
```

**ポイント**: `/sys/bus/w1/devices/28-*/w1_slave` の 2 行目に `t=12345` 形式。1000 で割って摂氏に。

### 6.5 I2C 読み取り（gpio_tds.py）

```python
I2C_BUS = 1
MCP3424_ADDR = 0x68

def _read_ch1_voltage() -> float:
    bus = smbus.SMBus(I2C_BUS)
    try:
        bus.write_byte(MCP3424_ADDR, 0x80)  # 設定: 18bit, 1x gain, one-shot
        time.sleep(0.1)
        raw = bus.read_i2c_block_data(MCP3424_ADDR, 0, 4)
        val = ((raw[0] & 0x03) << 16) | (raw[1] << 8) | raw[2]
        if val & 0x20000:  # 符号拡張
            val -= 0x40000
        return val * 2.048 / 262144  # LSB → 電圧(V)
    finally:
        bus.close()
```

**ポイント**: MCP3424 のレジスタ仕様に従い、18bit 値を電圧に変換。`smbus2` は純 Python で、`smbus` がなければフォールバック。

### 6.6 非同期処理（tapo_sensors.py）

Tapo はネットワーク I/O のため `asyncio` を使用。

```python
async def _get_readings_async():
    for hub_ip in ip_list:
        try:
            dev = await Discover.discover_single(hub_ip, username=..., password=...)
            await dev.update()
            if not _is_h100_device(dev):
                continue  # 別デバイス → 次を試す（ローラー作戦）
            break
        except Exception as e:
            last_error = e
            continue
    else:
        raise last_error
    # dev から T310/T315 の temperature, humidity を抽出
    ...

def get_readings():
    return asyncio.run(_get_readings_async())
```

**ポイント**: `asyncio.run()` で同期ラッパー。複数 IP を順に試す「ローラー作戦」で DHCP 変動に対応。

### 6.7 DB 書き込み（db/writer.py）

```python
def save_reading(conn, reading):
    cols = ["time", "sensor_id", "metric", "value"]
    vals = [reading["time"], reading["sensor_id"], reading["metric"], reading["value"]]
    if "source" in reading and reading["source"]:
        cols.append("source")
        vals.append(reading["source"])
    placeholders = ", ".join(["%s"] * len(cols))
    with conn.cursor() as cur:
        cur.execute(
            f"INSERT INTO sensor_readings ({', '.join(cols)}) VALUES ({placeholders})",
            tuple(vals),
        )
    conn.commit()
```

**ポイント**: パラメータ化クエリで SQL インジェクション防止。`source` はオプション。

### 6.8 Tapo P300（照明）の読み取り（tapo_lighting.py）

```python
for child in dev.children or []:
    sensor_id = f"tapo_lighting_{child.device_id}"
    value = 1.0 if child.is_on else 0.0
    readings.append({
        "time": now,
        "sensor_id": sensor_id,
        "metric": "power_state",
        "value": value,
        "source": "python-kasa",
    })
```

**ポイント**: P300 は複数の電源口（children）を持つ。各口の `is_on` で ON=1.0, OFF=0.0 を記録。Grafana で照明の ON/OFF 時間帯を可視化できる。

### 6.9 モックソース（mock.py）

```python
def get_readings():
    base_temp = 25.0
    random_fluctuation = random.uniform(-1, 1)
    temperature = base_temp + random_fluctuation
    return [{
        "time": datetime.datetime.now(datetime.timezone.utc),
        "sensor_id": "mock_temperature",
        "metric": "temperature",
        "value": round(temperature, 2),
    }]
```

**用途**: センサーなしでパイプラインをテスト。`SOURCES=mock` で DB と Grafana の動作確認が可能。

### 6.10 システムメトリクス（system_stats.py）

```python
# psutil で CPU・メモリ・ディスク
cpu_percent = psutil.cpu_percent(interval=1)
mem = psutil.virtual_memory()
disk = psutil.disk_usage("/")

# Raspberry Pi の CPU 温度は /sys から
with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
    temp_millideg = int(f.read().strip())
    cpu_temp = temp_millideg / 1000.0
```

**ポイント**: `ops_metrics` に `category: system` で保存。Grafana でラズパイの負荷・温度を監視できる。

### 6.11 使用ライブラリ一覧

| パッケージ | 用途 |
|------------|------|
| psycopg2-binary | PostgreSQL 接続 |
| python-kasa | Tapo デバイス制御（H100, P300） |
| tapo | Tapo 温湿度の代替実装（互換性問題あり） |
| smbus2 | I2C 通信（MCP3424） |
| psutil | CPU・メモリ・ディスク取得 |

---

## 7. Docker とコンテナ

### 7.1 docker-compose.yml の構造

```yaml
services:
  db:
    image: timescale/timescaledb:latest-pg14
    volumes:
      - ./db_data:/var/lib/postgresql/data
      - ./db/init:/docker-entrypoint-initdb.d  # 初回のみ SQL 実行
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]

  grafana:
    image: grafana/grafana:latest
    depends_on:
      db:
        condition: service_healthy

  collector:
    build: ./collector
    network_mode: host   # ホストのネットワークをそのまま使用（Tapo 接続用）
    volumes:
      - /sys/bus/w1/devices:/sys/bus/w1/devices:ro  # 1-Wire
      - ./collector_data:/app/data                 # 通知状態
```

### 7.2 network_mode: host の理由

- collector は Tapo（Wi-Fi）に接続するため、ホストと同じネットワークが必要
- `127.0.0.1:5432` で DB に接続（ホスト経由）
- 1-Wire は `/sys/bus/w1/devices` をマウントしてアクセス

### 7.3 環境変数の渡し方

```yaml
environment:
  TAPO_USERNAME: ${TAPO_USERNAME}
  TAPO_IP_CANDIDATES: ${TAPO_IP_CANDIDATES:-}  # 未設定時は空
```

`.env` ファイルの値が `${VAR}` に展開される。`:-` は未設定時のデフォルト。

### 7.4 Collector の Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
COPY src/ ./src/
COPY scripts/ ./scripts/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "src/main.py"]
```

- **python:3.11-slim**: 軽量な Python イメージ。slim は標準ライブラリ最小限
- **-u**: バッファリング無効で `print()` が即ログに出力される
- **scripts/**: 診断用スクリプト（test_tapo.py 等）もコンテナに含める

---

## 8. データベース設計

### 8.1 sensor_readings（センサーデータ）

```sql
CREATE TABLE sensor_readings (
    time        TIMESTAMPTZ NOT NULL,
    sensor_id   TEXT NOT NULL,
    metric      TEXT NOT NULL,
    value       DOUBLE PRECISION NOT NULL,
    source      TEXT
);
SELECT create_hypertable('sensor_readings', 'time');
```

- **hypertable**: TimescaleDB の時系列テーブル。`time` で自動パーティション
- **metric**: temperature, humidity, tds, power_state など

### 8.2 ops_metrics（運用メトリクス）

- **collection_success**: 収集成功=1, 失敗=0
- **readings_count**: 取得件数
- **collection_duration_ms**: 収集にかかった時間
- **system**: CPU, メモリ, ディスク, 温度

### 8.3 Grafana での SQL 例

**水温の時系列グラフ**:

```sql
SELECT time, value
FROM sensor_readings
WHERE sensor_id LIKE 'ds18b20_%' AND metric = 'temperature'
  AND time >= $__timeFrom() AND time < $__timeTo()
ORDER BY time
```

**気温・湿度（Tapo）**:

```sql
SELECT time, sensor_id, metric, value
FROM sensor_readings
WHERE sensor_id LIKE 'tapo_%' AND metric IN ('temperature', 'humidity')
  AND time >= $__timeFrom() AND time < $__timeTo()
ORDER BY time
```

**照明 ON/OFF**:

```sql
SELECT time, sensor_id, value
FROM sensor_readings
WHERE metric = 'power_state'
  AND time >= $__timeFrom() AND time < $__timeTo()
ORDER BY time
```

`$__timeFrom()`, `$__timeTo()` は Grafana のダッシュボードの時間範囲に自動で置換される。

---

## 9. 通知と運用

### 9.1 通知の種類

| 種類 | トリガー | 内容 |
|------|----------|------|
| IP 変更 | Tapo の接続 IP が変わった | 何から何に、前回からの経過、頻度、ペース |
| 収集失敗 | 連続 2 回失敗 | 期待値 vs 実際、前回成功からの経過、ヒント |

### 9.2 状態の永続化

- `collector_data/tapo-ip-state.json`: IP 変更履歴
- `collector_data/collector-failure-state.json`: 連続失敗回数、最終通知時刻

### 9.3 メール送信（標準ライブラリのみ）

```python
import smtplib
from email.mime.text import MIMEText

msg = MIMEText(body, "plain", "utf-8")
msg["Subject"] = subject
with smtplib.SMTP(host, 587) as smtp:
    smtp.starttls()
    smtp.login(user, password)
    smtp.sendmail(user, [to_addr], msg.as_string())
```

---

## 10. 学習のための次のステップ

### 10.1 理解を深める順序

1. **データの流れ**: センサー → collector → DB → Grafana を追う
2. **1つのソースを読む**: `gpio_temp.py` が短く、1-Wire の仕組みが学べる
3. **main.py のループ**: スレッドとメインループの役割分担
4. **Docker**: `docker compose up` で何が起きるか

### 10.2 試してみること

- `SOURCES=mock` でモックデータのみ収集
- Grafana で SQL を書いてグラフを追加
- 新しいソースを `_load_source` に追加する

### 10.3 参考リンク

- [TimescaleDB ドキュメント](https://docs.timescale.com/)
- [Raspberry Pi GPIO](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html)
- [python-kasa](https://github.com/python-kasa/python-kasa)

---

## 11. 環境変数リファレンス

### 11.1 必須（本番運用時）

| 変数 | 説明 | 例 |
|------|------|-----|
| POSTGRES_USER | DB ユーザー | postgres |
| POSTGRES_PASSWORD | DB パスワード | （強力なパスワード） |
| POSTGRES_DB | DB 名 | aquapulse |
| SOURCES | 有効なソース（カンマ区切り） | gpio_temp,gpio_tds,tapo_sensors,tapo_lighting |
| TAPO_USERNAME | Tapo アプリのメールアドレス | user@example.com |
| TAPO_PASSWORD | Tapo アプリのパスワード | （アプリと同じ） |

### 11.2 オプション（Tapo 関連）

| 変数 | 説明 | デフォルト |
|------|------|------------|
| TAPO_HUB_IP | H100 の固定 IP（優先） | - |
| TAPO_LIGHTING_IP | P300 の固定 IP | - |
| TAPO_IP_CANDIDATES | ローラー作戦用 IP リスト（カンマ区切り） | 192.168.3.2〜12 |
| TAPO_BACKEND | python-kasa または tapo | python-kasa |

### 11.3 オプション（収集間隔）

| 変数 | 説明 | デフォルト |
|------|------|------------|
| SAMPLE_INTERVAL | Tapo 等のメインループ間隔（秒） | Tapo 使用時 300、それ以外 5 |
| GPIO_TEMP_INTERVAL | 水温取得間隔（秒） | 60 |
| TDS_INTERVAL | TDS 取得間隔（秒） | 60 |
| SYSTEM_STATS_INTERVAL | システムメトリクス間隔（秒） | 60 |

### 11.4 オプション（通知）

| 変数 | 説明 |
|------|------|
| NOTIFY_EMAIL | 通知先メールアドレス |
| SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD | SMTP 設定（Gmail はアプリパスワード） |
| LINE_NOTIFY_TOKEN | LINE Notify トークン（Email 未設定時） |
| NOTIFY_STATE_DIR | 状態ファイルのディレクトリ | /app/data |

### 11.5 オプション（TDS キャリブレーション）

| 変数 | 説明 | デフォルト |
|------|------|------------|
| TDS_SENSOR_ID | sensor_id の上書き（テスト用） | tds_ch1 |
| TDS_K | 電圧→ppm の係数 | 500 |

---

## 12. トラブルシューティング

### 12.1 DS18B20 が検出されない

1. **config.txt の確認**: `dtoverlay=w1-gpio` が追加されているか
2. **再起動**: 設定変更後は再起動が必要
3. **デバイス確認**: `ls /sys/bus/w1/devices/` で `28-*` が表示されるか
4. **配線**: 3.3V, GND, データ（GPIO 4）が正しいか。プルアップ抵抗（4.7kΩ）がモジュール内蔵でない場合は必要

### 12.2 MCP3424 / I2C が応答しない

1. **I2C 有効化**: `raspi-config` → Interface Options → I2C → Enable
2. **デバイス確認**: `i2cdetect -y 1` で 0x68 が表示されるか
3. **CH1- の接続**: MCP3424 Pin 2 (CH1-) を GND に接続。浮いていると不安定

### 12.3 Tapo に接続できない

1. **認証**: TAPO_USERNAME, TAPO_PASSWORD がアプリと同じか
2. **ネットワーク**: collector は `network_mode: host` でホストと同じネットワーク。Tapo と同一 LAN か
3. **ローラー作戦**: TAPO_IP_CANDIDATES に候補 IP を追加。`test_tapo.py` で診断

### 12.4 DB に接続できない

1. **ホスト**: collector が `network_mode: host` の場合、DB_HOST=127.0.0.1 でホスト経由
2. **起動順**: db の healthcheck が通るまで collector は待機。`docker compose logs db` で確認
3. **ポート**: 5432 が他プロセスで使用されていないか

---

## 13. コードの詳細解説（発展）

### 13.1 asyncio.to_thread の使い方（gpio_temp.py）

`gpio_temp.py` は `get_readings()` が `asyncio.run(_get_readings_async())` を呼び、内部で `asyncio.to_thread(_read_temperature_sync, device_path)` を使っています。

```python
# ファイル I/O はブロッキングなので、スレッドプールで実行
temp = await asyncio.to_thread(_read_temperature_sync, device_path)
```

**なぜこうするか**: `open()` や `f.read()` はブロッキング。メインスレッドで実行すると他のタスクを止める。`asyncio.to_thread()` でスレッドプールに投げ、イベントループをブロックしない。

### 13.2 遅延 import の意図

```python
def _load_source(name):
    if name == "tapo_sensors":
        from sources.tapo_sensors import get_readings  # ここで初めて import
        return get_readings
```

**理由**: `SOURCES=mock` のとき、tapo_sensors を import すると python-kasa がロードされ、不要な依存が起動時に読み込まれる。遅延 import で、実際に使うソースのモジュールだけをロードする。

### 13.3 ヘルスメトリクスの設計

`collect_with_health` は成功・失敗どちらでもメトリクスを返します。

- **collection_success**: 1.0 = 成功, 0.0 = 失敗
- **collection_duration_ms**: 収集にかかった時間（デバッグ・パフォーマンス監視用）
- **readings_count**: 取得件数（期待値との比較で通知判定）

Grafana で `collection_success == 0` のアラートを張れば、収集失敗を可視化できます。

### 13.4 状態の永続化（notify.py）

```python
state = {
    "last_ip_tapo_sensors": "192.168.3.5",
    "last_change_at_tapo_sensors": "2026-03-17T10:00:00Z",
    "change_history": [
        {"source": "tapo_sensors", "old_ip": "192.168.3.4", "new_ip": "192.168.3.5", "at": "..."}
    ]
}
```

JSON ファイルで永続化し、コンテナ再起動後も「前回の IP」「変更履歴」を保持。通知文に「前回から何時間」「過去7日で何回」を含めることで、根本対策（DHCP 予約など）の判断材料にします。

---

## 14. TimescaleDB の Continuous Aggregates（将来の ML 用）

時系列データを 1 分・5 分粒度で集約するビューを事前計算しておくと、ML の特徴量として使いやすくなります。

```sql
-- 1 分粒度の平均（例）
CREATE MATERIALIZED VIEW sensor_readings_1m
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 minute', time) AS bucket,
    sensor_id,
    metric,
    avg(value) AS value
FROM sensor_readings
GROUP BY bucket, sensor_id, metric;
```

- **time_bucket**: 指定間隔でタイムスタンプを丸める
- **WITH (timescaledb.continuous)**: バックグラウンドで自動更新
- クエリ時は `SELECT * FROM sensor_readings_1m` で高速にアクセス

---

## 15. 外から・スマホから読む方法

### 15.1 GitHub / GitLab で Markdown を表示

- このファイルをリポジトリに push すると、GitHub の Web 画面で Markdown がレンダリングされます
- スマホのブラウザでも同様に閲覧可能
- **Private リポジトリ**: ログインすれば同じように閲覧可能

### 15.2 GitHub Pages（Public の場合）

- リポジトリを Public にし、Settings → Pages で有効化
- `docs/` をソースにすると、`https://<user>.github.io/<repo>/learning/aquapulse-dev-guide` でアクセス可能
- **注意**: Private リポジトリでは GitHub Pro が必要

### 15.3 他の選択肢

- **PDF に変換**: `pandoc aquapulse-dev-guide.md -o aquapulse-dev-guide.pdf` で PDF 化し、Google Drive 等にアップロード
- **Notion / Obsidian**: Markdown をインポートしてクラウド同期
- **Gist**: 長文は分割が必要だが、Public Gist なら URL 共有で誰でも閲覧可能

---

## 16. まとめ

本ガイドでは、AquaPulse プロジェクトの技術スタック、アーキテクチャ、物理センサー接続、コードのロジック、環境変数、トラブルシューティングまでを網羅しました。

開発初心者の方は、まず「データの流れ」を追い、次に `gpio_temp.py` のような短いソースから読むことをお勧めします。Docker と TimescaleDB の基礎が分かれば、全体像の理解が深まります。

---

*本ガイドは AquaPulse プロジェクトの実装に基づいて作成しました。*
