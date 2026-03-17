# AquaPulse 作業ログ

## 2026-03-17（火）

### やったこと

- **Grafana キオスクモードの構築**
  - Pi Touch Display 1 (800x480) に Grafana ダッシュボードを全画面表示
  - Wayland コンポジタ `cage` + Chromium でキオスク実現
  - `seatd` を導入して DRM セッション管理
  - systemd サービス `grafana-kiosk.service` で自動起動
  - 匿名アクセス設定（`GF_AUTH_ANONYMOUS_ENABLED`）で認証スキップ

- **ops_metrics（システム監視）の追加**
  - `db/migrations/002_ops_metrics.sql` - 新テーブル追加
  - `collector/src/sources/system_stats.py` - CPU/メモリ/ディスク/温度を収集
  - `collector/src/main.py` - 収集ヘルス計測を統合（duration_ms, success）
  - `grafana/dashboards/aquapulse-operations.json` - Ops ダッシュボード作成

- **ダッシュボードの分離（PC用 / Display用）**
  - `aquapulse-pc.json` - 13インチMacBook向け、6つのStats + 詳細グラフ
  - `aquapulse-display.json` - 7インチTouch Display向け、4つのStats + コンパクトグラフ
  - 800x480 でスクロールなしで一覧できるレイアウトに最適化

- **ドキュメント整理**
  - `docs/display/` フォルダを新規作成、キオスク関連を集約
  - TUI 関連ドキュメントを `docs/archive/tui/` に移動（廃止のため）
  - `docs/README.md` を更新、ナビゲーション改善

- **README 画像の更新**
  - PC用 / Display用 の2カラム表示に変更
  - `docs/images/dashboard-pc.png`, `dashboard-display.png` を追加

- **輝度制御スクリプトの作成**
  - `kiosk/brightness.sh` - 手動輝度調整
  - `kiosk/brightness-schedule.sh` - 時間帯別自動調整
  - ⚠️ I2C エラー（-121）のため現在動作せず → 既知の問題として記録

- **P300 データ収集の復旧**
  - `TAPO_LIGHTING_IP` が Hub（192.168.3.6）を指していたのを P300（192.168.3.8）に修正
  - 5口すべて（熱帯魚ライト、アクアコンパクト、水槽ヒーター、Gexスリムフィルター、USB）の収集を復旧
  - Grafana の Tapo_Tank_Light パネルを正しい sensor_id に修正

### インフラ・トラブル対応

- **新ダッシュボードで "Failed to load dashboard forbidden"**
  - 原因: `GF_AUTH_ANONYMOUS_ENABLED=true` でも、ダッシュボード個別のパーミッションが未設定だった
  - 旧ダッシュボード（adsbdzn）には Viewer ロールが設定済み、新ダッシュボードは `[]`（空）
  - 解決: Grafana API でパーミッションを追加
    ```bash
    curl -X POST -u admin:admin \
      -H "Content-Type: application/json" \
      "http://localhost:3000/api/dashboards/uid/aquapulse-display/permissions" \
      -d '{"items":[{"role":"Viewer","permission":1},{"role":"Editor","permission":2}]}'
    ```
  - トラブルシューティングを `docs/display/grafana-kiosk.md` に追記

- **SSD 移行後の Remote SSH 接続失敗**
  - シンボリックリンク（`~/.vscode-server`, `~/.cursor-server`）が旧パス `/mnt/ssd/...` を指していた
  - 新パス `/vscode-server`, `/cursor-server` に修正して解消
  - 詳細: `docs/ssd-migration-report.md`

- **I2C 通信エラー（タッチ・輝度）**
  - DSI（映像）は正常だが、I2C（タッチ 0x38、輝度 0x45）が通信エラー
  - リボンケーブル確認が必要 → TODO として記録

- **Chromium パッケージ名変更**
  - Debian Trixie では `chromium-browser` → `chromium` に変更
  - インストールスクリプトを修正

### 次回・今後

- [ ] I2C 問題調査（リボンケーブル抜き差し、別ポート試行）
- [ ] イベント記録システム（餌やり、水替え等）の設計・実装

---

## 2026-03-15（日）

### やったこと

- **TDS センサー（MCP3424 CH1）の collector 統合**
  - `sources/gpio_tds.py` を新規作成。MCP3424 CH1 から電圧を読み、TDS(ppm) に換算して DB に保存
  - `main.py` に gpio_tds を SOURCE_LOADERS に登録
  - `requirements.txt` に smbus2 を追加
  - `docker-compose.yml` に `/dev/i2c-1` を devices でマウント、`TDS_SENSOR_ID` を環境変数で渡せるように追加
  - テスト時は `.env` に `TDS_SENSOR_ID=tds_test_ch1` を設定して本番データと分離
  - 電圧→ppm 換算は線形（`ppm = voltage * TDS_K`）。`TDS_K` でキャリブレーション可能（デフォルト 500）

- **MCP3424 CH1- を GND に接続**
  - 差動入力の負側が浮いていたため測定が不安定だった。CH1- (Pin 2) を GND に接続して解消
  - 接続後、水道水で 0.56V を確認（以前は -0.06V 付近）

- **TDS 暫定運用（瓶測定）の整備**
  - 水槽内では 0ppm のため、アイソレータ導入まで 1日1回ガラス瓶で測定する運用を採用
  - `collector/scripts/measure_tds_bottle.py` を新規作成。プローブを瓶に浸して実行、ppm 表示。`--save` で DB に保存
  - `.env` 変更・docker compose の起動は不要。ホスト上で `python3 collector/scripts/measure_tds_bottle.py` を実行
  - sensor_id は `tds_bottle`（Grafana で連続測定と区別可能）。詳細は [improvement-plan.md](../hardware/improvement-plan.md)

### 次回・今後

- **SOURCES に gpio_tds を追加**して collector を再起動、Grafana で TDS を可視化（水槽内は 0ppm のため、瓶測定運用を優先）
- DFR0504 アイソレータ導入後、水槽内での常時測定に移行
- pH センサー（CH2）の実装

### インフラ・トラブル対応

- **Grafana で DB データが表示されない（400 Bad Request）**
  - 症状: ログインはできるが、パネルに水温・TDS などのグラフが出ない。`docker compose logs grafana` で `/api/ds/query status=400` が連続
  - 原因: 3/14 に固定 IP（172.28.0.2）をコメントアウトしたが、Grafana の PostgreSQL データソースは `172.28.0.2:5432` のまま。ラズパイ再起動後、Docker が IP を再割り当てし、172.28.0.2 が db を指さなくなった
  - 対処: Grafana → Configuration → Data sources → PostgreSQL の **Host URL** を `172.28.0.2:5432` から **`db:5432`** に変更し、Save & test
  - 教訓: 固定 IP をやめたら、Grafana の Host も同時にホスト名（`db`）に変更すること。詳細は [recovery-runbook.md](recovery-runbook.md#grafana-でデータが表示されない)

---

## 2026-03-14（土）

### やったこと

- **水温センサー（DS18B20）のピン移行**
  - データ線をピン5（GPIO 3）→ ピン7（GPIO 4）に移行
  - 配線: ピン1(3.3V), ピン6(GND), ピン7(データ) の 1, 6, 7 構成に
  - 理由: ADC（MCP3424T）で TDS/pH を追加する予定のため、I2C 用ピン3, 5 を空ける
  - config.txt は `dtoverlay=w1-gpio` のままで、デフォルト GPIO 4 が使われるため編集不要

- **配線記録ドキュメントの作成**
  - `docs/hardware/wiring/` を新規作成。ピン配置、センサー別詳細、変更履歴を記録
  - 今後配線を追加・変更したら都度更新する前提

- **DB コンテナの再起動安定化対策**（docker-compose.yml）
  - `TS_TUNE_MEMORY: 512MB` を追加（TimescaleDB のメモリ自動検出失敗による Exit 128 対策）
  - `healthcheck` を追加（pg_isready で DB の readiness を監視）
  - Grafana, collector の `depends_on` を `condition: service_healthy` に変更（DB が使えるまで起動を待機）
  - 固定 IP（172.28.0.2）をコメントアウト（ネットワーク競合対策）

- **電源復旧後の DB 復旧**
  - 電源復旧後、DB のみ Exited (128) で落ちていた
  - `Address already in use` で再起動失敗 → `docker compose down` → `up -d` で解消
  - 上記対策適用後、DB が healthy になってから Grafana/collector が起動することを確認

### インフラ・トラブル対応

- **DB コンテナ単独落ち**: 電源断後の復旧時に DB のみが起動失敗。`docker compose down` でネットワークをリセットしてから `up -d` で復旧。今後は healthcheck と service_healthy により起動順序が安定化

### 次回・今後

- **ADC（MCP3424T）の接続**: ピン3, 5 に I2C で接続。TDS/pH 計測コードの実装
- **I2C の有効化**: `/boot/firmware/config.txt` で `dtparam=i2c_arm=on` のコメントを外す

---

## 2026-03-03（火）

### やったこと

- **ネットワーク障害の復旧**
  - Raspberry Pi 5 の Wi-Fi 接続が突如ロストし、SSH・ネットワーク経由のアクセスが不可に
  - 有線 LAN ケーブル（2m）を調達し、ラズパイとルーターを直接接続
  - OS 再起動後、有線 LAN 経由で DHCP により IP を取得

- **IP アドレスの特定**
  - Mac ターミナルから `nmap -sn 192.168.3.0/24` でローカルネットワークをスキャン
  - 有線 LAN で割り当てられた IP `192.168.3.17` を特定

- **システム生存確認**
  - `ssh koichi@192.168.3.17` で SSH 接続成功
  - `docker ps` により主要コンテナの正常稼働を確認（データ欠損リスクは最小限）
    - `aquapulse-data_collector-1` (Python スクリプト)
    - `timescaledb` (PostgreSQL / 時系列 DB)
    - `grafana` (BI ダッシュボード)
    - `aquapulse-mosquitto-1` (MQTT ブローカー)

- **Remote-SSH 環境の構築**
  - Wi-Fi トラブルシューティングを後回しにし、有線 LAN 上で開発効率を優先
  - Mac 側で SSH 公開鍵を作成し、ラズパイの `~/.ssh/authorized_keys` に登録（パスワードレス認証）
  - Mac の `~/.ssh/config` に接続情報を追記
  - Cursor の Remote-SSH でラズパイに接続成功。コンテナ再起動・ファイル直接編集が可能に

### やったこと（パート2）

- **IP アドレスの固定**（NetworkManager）
  - `nmcli connection show` で接続名を確認: 有線 `netplan-eth0`、無線 `netplan-wlan0-D80F99C56038-2G`
  - 重要: `ipv4.method manual` はアドレス設定の**後**に指定する必要あり（順序を間違えるとエラー）
  - 有線: `192.168.3.17`、無線: `192.168.3.14` を固定化

- **Docker の建て直し**
  - `Address already in use` で db コンテナ起動失敗 → `docker compose down` → `up -d` で解消
  - 全コンテナ（db, grafana, collector）正常稼働を確認

- **Grafana パスワードリセット**
  - `admin`/`admin` ではログインできず（以前に変更済み）
  - `docker compose exec grafana grafana cli admin reset-admin-password admin` でリセット成功

- **水温センサー（DS18B20）の Grafana 可視化**
  - クエリ: `sensor_id = 'ds18b20_water_28_00001117a4e0'` AND `metric = 'temperature'`
  - 水温データが Grafana で表示できることを確認

- **VSCode SQLTools で DB 接続**
  - PostgreSQL データソースを追加（localhost:5432, db: aquapulse, user: postgres）
  - `.sql` ファイルでクエリを書いて `Cmd+E` → `Cmd+E` で実行、結果をエディタ内で確認可能に

### インフラ・トラブル対応

- **Wi-Fi 接続ロスト**: 有線 LAN への切り替えで即時復旧。Wi-Fi の原因調査は未実施（後日対応予定）
- **nmcli の ipv4.method**: `manual` を先に指定するとエラー → アドレス・ゲートウェイ・DNS を先に設定し、最後に `manual` を指定

### 次回・今後

1. ~~**IP アドレスの固定**~~: 完了（有線 192.168.3.17、無線 192.168.3.14）
2. **API サーバーの構築 (FastAPI)**: スマホからの手動記録を受け付けるバックエンドエンドポイントを Docker コンテナとして追加
3. **入力 UI の開発 (Streamlit)**: 水槽の前からサクッと入力できる専用 Web UI を構築し、FastAPI と連携
4. **Phase 2（手動入力・AI 予測基盤）の開発**を上記の順で進める

---

## 2026-02-25（火）

### やったこと

- **照明（tapo_lighting）の追加**
  - Tapo P300 電源タップから ON/OFF 状態を取得
  - `sources/tapo_lighting.py` を新規作成、`metric='power_state'`, `value=0/1` で DB に保存
  - P300 の 5 口すべてを取得、照明は `...C8D00` が該当（23時で OFF になる設定と一致）

- **ソースのリネーム**（将来の拡張を見据えて）
  - `tapo.py` → `tapo_sensors.py`（温湿度）
  - `tapo_plug.py` → `tapo_lighting.py`（照明）
  - 今後 `tapo_heater`, `tapo_feeding` などを追加しやすい構成に

- **Grafana で照明 ON/OFF を可視化**
  - `power_state` の State timeline / Time series パネルを追加
  - `sensor_id = 'tapo_lighting_80227057FCADBA274FA7573C40B966F923F67C8D00'` で照明のみ表示

- **Mock の停止**
  - `SOURCES` から `mock` を削除 → `tapo_sensors,tapo_lighting` のみ
  - 過去の mock データは DB に残り、Grafana でも表示継続

- **アーキテクチャ設計の文書化**
  - `docs/design/architecture.md` に ML・データ基盤の設計方針を保存
  - `.cursor/rules/architecture.mdc` で AI が参照できるように

- **開発環境の整備**
  - PostgreSQL 拡張（Chris Kolkman）で Cursor から直接クエリ実行
  - `aq-psql` エイリアス案を検討

### インフラ・トラブル対応

- **Docker daemon.json 競合**: `data-root` が systemd フラグと daemon.json で二重定義 → daemon.json から削除して解消
- **~/.docker を SSD に移行**: buildx の「no space left」対策（SD カードのルートが満杯のため）
- **DB ポート競合**: `Address already in use` → `docker compose down` → `up -d` で解消
- **Docker ビルド時の DNS**: `--network=host` でビルドすれば安定

### 次回・今後

- **水温センサー**（27日到着予定）→ GPIO または別ソースで取得を追加
- **飲み会**（26〜27日）のため一旦区切り。到着後に再開する想定

### 暇なときにできる小さなタスク（メモ）

- [ ] `docs/design/metrics.md` に sensor_id とコンセントの対応（C8D00=照明 など）を追記
- [ ] `README.md` の現状（tapo_sensors, tapo_lighting、mock 停止）を反映
- [ ] 水温センサー到着前に `tapo_heater` のスケルトンだけ作っておく
- [ ] `.env.example` に `TAPO_LIGHTING_IP` を追加

---

## 2026-02-24（火）

### やったこと

- **Tapo ソースの追加**（H100 + T310/T315 温湿度センサー）
  - `sources/tapo.py` を新規作成、`get_readings()` で温度・湿度を取得
  - `tapo` ライブラリを使用（H100 対応）

- **複数ソース対応**
  - `SOURCES` 環境変数でカンマ区切り指定（例: `mock,tapo`）
  - 各ソースの `get_readings()` を順次呼び、結果を結合して DB に保存

- **フォールトトレランス**
  - 各ソースの取得を try/except で囲み、失敗時はログ出力して続行
  - 1 つのソース失敗でも他は継続

- **collector の network_mode: host**
  - Docker ブリッジから Tapo（192.168.3.x）へ接続できなかったため、host に変更
  - `DB_HOST: 127.0.0.1` に変更

- **H100 と H110 の違い**
  - T310/T315 は H100 に接続 → H100 の IP を指定して取得
  - H110 は 403 Forbidden（非対応の可能性）

- **取得頻度**
  - Tapo センサーの更新タイミングに合わせて 5 分（300 秒）に変更

- **Grafana**
  - mock / Tapo 温度 / Tapo 湿度を別パネルで表示

### その他

- ディスク容量不足で Docker ビルド失敗 → `/var/lib/docker` を SSD に移動して解消
- `SAMPLE_INTERVAL` が空文字で `int()` エラー → `or` でデフォルトを適用するよう修正

## 2026-02-23（月）

### やったこと

- **Collector のリファクタリング**（18日の「次回やること」の「Collector コードの読み解き・整理」を実施）
  - `mock_collector.py` を役割ごとに分割
  - **データ取得** → `sources/mock.py` の `get_readings()`
  - **DB 書き込み** → `db/writer.py` の `save_reading()`
  - **起動・ループ** → `main.py`

- **共通フォーマットの導入**
  - 読み取りデータを `{"time", "sensor_id", "metric", "value"}` に統一
  - `get_readings()` がこの形式の辞書リストを返し、`save_reading(conn, reading)` がそれを受け取る
  - Tapo / GPIO 対応時に同じインターフェースで差し替え可能な構成にした

- **起動エントリポイントの変更**
  - Dockerfile の `CMD` を `mock_collector.py` から `main.py` に変更
  - `main.py` が `get_readings()` → `save_reading()` を呼ぶ構成に変更

- **sensor_id の変更**: `temp_sensor_01` → `mock_temperature`

### ディレクトリ構成（変更後）

```text
collector/src/
├── main.py         # エントリポイント・ループ
├── sources/
│   └── mock.py     # モックデータ取得（get_readings）
└── db/
    └── writer.py   # DB 書き込み（save_reading）
```
現在の状態
Collector は「取得」と「保存」が分離され、共通フォーマットで TAPO 移行の土台ができている
Grafana のクエリで sensor_id = 'mock_temperature' に変更する必要あり（temp_sensor_01 から変更のため）

次回やること（メモ）
[ ] TAPO 移行（Collector 整理済みのため着手可能）
[ ] Grafana ダッシュボードの改善（sensor_id の変更反映、パネルタイトル・単位の設定など）


## 2026-02-18（水）
### やったこと

- **Collector → DB → Grafana の貫通を達成**
  - `collector` が TimescaleDB（PostgreSQL）に 5 秒ごとに `sensor_readings` へ INSERT していることを確認
  - `docker compose exec db psql ...` で `temperature` のレコードが取得できる状態まで到達

- **ビルド時の DNS 問題の切り分けと解決**
  - `docker compose build collector` が `Temporary failure in name resolution`（`psycopg2-binary` 取得失敗）で毎回コケていた
  - ホストでは `getent hosts pypi.org` が成功 → ホスト DNS は正常
  - ビルド時は「ビルド用コンテナの DNS」を使っており、ここが壊れていると判明
  - **対策: ビルド時だけホストネットワークを使用**:
    ```bash
    cd /mnt/ssd/projects/aquapulse
    docker build -f collector/Dockerfile --network=host -t aquapulse-collector ./collector
    ```
  - これにより `pip install --no-cache-dir -r requirements.txt` が成功し、`psycopg2-binary` を含んだ新しい `aquapulse-collector` イメージを作成

- **Collector コンテナの再起動と DB 書き込み確認**
  - DB コンテナのポート競合（Address already in use）を確認しつつ、`docker compose down` → `docker compose up -d db` でクリーンに再起動
  - 新しいイメージを使って collector を起動:
    ```bash
    docker compose up -d collector
    docker compose logs collector -f
    ```
  - ログに `--- AquaPulse Mock Collector Started (Interval: 5s) ---` と `Connected to DB.` が出力されることを確認
  - DB 側での確認:
    ```bash
    docker compose exec db psql -U postgres -d aquapulse -c \
      "SELECT * FROM sensor_readings ORDER BY time DESC LIMIT 5;"
    ```
    → `temp_sensor_01` / `temperature` / `value` のレコードが 5 秒おきに増えていることを確認

- **Grafana ダッシュボードによる可視化**
  - `grafana` コンテナを起動し、`http://<Raspberry Pi の IP>:3000` にアクセス
  - PostgreSQL データソースを追加（例）:
    - **Name**: aquapulse_mock
    - **Host**: `172.28.0.2:5432`
    - **Database**: `aquapulse`
    - **User**: `postgres`
    - **Password**: `.env` の `POSTGRES_PASSWORD`
    - **SSL mode**: `disable`
  - 新しいダッシュボード → Add visualization → Data source に上記を選択
  - クエリを SQL モードで設定:
    ```sql
    SELECT
      time AS "time",
      value AS "temperature"
    FROM sensor_readings
    WHERE metric = 'temperature'
    ORDER BY time;
    ```
  - Visualization を `Time series` にして適用し、温度の時系列グラフが表示されることを確認
  - ダッシュボード上部の Refresh を `5s` や `10s` に設定し、Collector の INSERT に追従する「準リアルタイム」表示を実現

### 課題と解決

| 課題 | 解決 |
|---|---|
| collector のビルド時に `psycopg2-binary` が取得できず、常に古いイメージで起動してしまう | ビルド用コンテナの DNS が壊れていると切り分け、`docker build --network=host ...` でホストと同じ DNS・ネットワークを使ってビルドし、インストールに成功 |
| `docker compose run collector ...` 実行時に `Address already in use` が発生 | 5432 ポートの利用状況を `ss` で確認し、`docker compose down` → `up -d db` でクリーンに再起動して解消 |
| Grafana でどのようにクエリを書けばよいか分からない | `sensor_readings(time, sensor_id, metric, value)` を前提に、`metric='temperature'` を条件にしたシンプルな SELECT でまず動くグラフを作成し、その上で集約や単位などの調整を行う方針にした |

### 現在の状態

- **Raspberry Pi 5 上で以下が動作**:
  - `collector`: モック温度データを 5 秒ごとに生成し、TimescaleDB の `sensor_readings` に INSERT
  - `db`（TimescaleDB/PostgreSQL）: `sensor_readings(time, sensor_id, metric, value)` にデータ蓄積中
  - `grafana`: `AquaPulse PostgreSQL` データソース経由で温度データを Time series グラフとして表示
- `docker build -f collector/Dockerfile --network=host -t aquapulse-collector ./collector` を使う運用であれば、collector のビルドは安定して通る
- ダッシュボードを保存済み（`aquapulse_Mock` などの名前）で、ブラウザからいつでもモック温度の時系列を確認可能

### 次回やること（メモ）

**推奨順序**: ① Collector の整理 → ② TAPO 移行。整理で「取得」と「保存」を分け、共通フォーマットを決めておくと TAPO/GPIO の追加が楽になる。

- [ ] **Collector コードの読み解き・整理**（TAPO 移行より先に実施推奨）
  - `mock_collector.py` の構造を再確認し、「データ取得部分」と「DB 書き込み部分」の役割をはっきりさせる
  - 将来の Tapo API / GPIO センサー対応を見据えて、インターフェース（戻り値の形式など）をどう共通化するかを検討する
- [ ] **TAPO 移行**（Collector 整理のあと）
  - 上記の共通インターフェースに沿って Tapo 用の取得モジュールを追加し、モックと差し替え or 併用できるようにする
- [ ] **Grafana ダッシュボードの改善**（TAPO データが出てからでも可）
  - パネルタイトル・単位（°C）の設定、時間範囲プリセットの調整
  - 将来的な複数センサー・複数メトリクスに向けて、センサーIDや metric を選べるようなダッシュボード変数の導入を検討
- [ ] **次フェーズのデータソース拡張**
  - モックからどの実センサー（Tapo / GPIO）に進むかを決める
  - それに合わせて DB スキーマや Collector の処理フロー（リトライ・タイムアウト・ログなど）の要件を整理する

## 2026-02-17（月）

### やったこと
- Raspberry Pi 5（Debian bookworm、SSD ブート）で AquaPulse プロジェクトを構築
- Docker Compose で Collector（Python）、TimescaleDB、Grafana を起動
- Collector: Dockerfile、requirements.txt、.dockerignore を作成し、mock_collector.py を実行するように設定
- DB: db/init/00_schema.sql で sensor_readings テーブルと TimescaleDB hypertable を定義
- docker-compose.yml: 3 サービスを aquapulse_net で接続、環境変数・ボリュームを設定
- **Docker ネットワークの安定化**:
  - ホスト名 `db` での接続を再トライ → 失敗（DNS connection refused）
  - 固定 IP 方式に切り替え
  - 当初 collector に誤って IP を割り当て → タイムアウト
  - db に `172.28.0.2` を正しく割り当て → Grafana 接続 OK

### 課題と解決
| 課題 | 解決 |
|---|---|
| exec format error（/usr/bin/runc が空） | containerd.io の再インストールが必要 |
| No space left on device（ルートが満杯） | apt のキャッシュ・lists を SSD に bind mount して回避 |
| unsupported shim version (3) | containerd を 1.7.29 にダウングレード |
| Grafana Restarting | パーミッション・SQLite ロックを疑ったが、最終的に起動 |
| Grafana の DB 接続エラー（ホスト名 `db` の名前解決失敗） | 当初 `172.18.0.2` で回避 |
| ホスト名 `db` の再トライ失敗（127.0.0.11:53 connection refused） | 固定 IP 方式に切り替え |
| 固定 IP の割り当て先を誤る（collector に割当 → タイムアウト） | db に `172.28.0.2` を割り当て、Grafana・Collector は IP で接続 |

### 現在の状態
- 3 コンテナ（db, grafana, collector）は起動済み
- Grafana の PostgreSQL データソースは `172.28.0.2` で接続 OK
- db は固定 IP `172.28.0.2`、Collector の DB_HOST も `172.28.0.2` に設定済み
- Collector は 5 秒ごとに JSON を標準出力に出力（DB への書き込みは未実装）

### ネットワーク構成（固定 IP 適用後）

```text
db (172.28.0.2) ◄── grafana 接続 OK
      ▲
      └── collector（DB_HOST: 172.28.0.2）

```

---

## 2026-02-16（日）

### やったこと
- Raspberry Pi 5 の Docker 環境トラブルシューティング
- SD カードの容量不足（使用率 100%）によるシステム不安定化の解消
- Docker デーモンが起動しない（SEGV エラー）問題の解決
- **SSD 完全移行の実施**:
  - 設定ファイル（daemon.json）による指定を廃止
  - OS レベルでの `mount --bind` を採用し、`/var/lib/docker` の実体を SSD に強制変更

### 課題と解決
| 課題 | 解決 |
|---|---|
| Docker 起動失敗 (signal=SEGV) | `daemon.json` と `systemd` フラグの二重定義（競合）を特定し、設定ファイルを全削除してリセット |
| SD カード容量枯渇 (VS Code 接続断) | `journalctl --vacuum` 等で一時領域を確保し、Docker のデータを SSD へ逃がすことで恒久対応 |
| 複雑な設定による管理コスト増 | `daemon.json` を使わず、シンプルに `mount --bind /mnt/ssd/docker-core /var/lib/docker` で一本化 |
| AI との意思疎通（コード非表示など） | プロンプトと出力形式を見直し、確実なコマンド実行ベースで進行するよう軌道修正 |

### 現在の状態
- Docker デーモン: **Active (running)**
- Docker Root Dir: `/var/lib/docker` (実体は SSD `/mnt/ssd/docker-core-final`)
- コンテナ: 未起動（インフラ層の復旧完了）
- VS Code: 正常に接続可能

---