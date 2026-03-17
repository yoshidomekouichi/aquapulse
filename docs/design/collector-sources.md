# Collector ソース一覧

collector が対応するセンサーソースと、各ソースの環境変数・sensor_id の一覧。

---

## ソース一覧

| ソース名 | 説明 | sensor_id 例 | 備考 |
|----------|------|---------------|------|
| `gpio_temp` | DS18B20 水温 | `ds18b20_water_28_00001117a4e0` | 独立ループ（GPIO_TEMP_INTERVAL） |
| `gpio_tds` | TDS（MCP3424 CH1） | `tds_ch1` または `TDS_SENSOR_ID` | I2C 要。テスト時は `TDS_SENSOR_ID=tds_test_ch1` |
| `tapo_sensors` | Tapo 温湿度 | `tapo_*` | H100 + T310/T315。`TAPO_BACKEND=tapo` で tapo ライブラリ、未設定で python-kasa |
| `tapo_lighting` | Tapo 照明 ON/OFF | `tapo_lighting_*` | P300 マルチタップ（python-kasa）。**TAPO_LIGHTING_IP は P300 の IP**（H100 とは別） |
| `mock` | モックデータ | `mock_temperature` | 開発・テスト用 |
| `system_stats` | システムメトリクス | - | CPU/メモリ/ディスク/温度。`ops_metrics` テーブルに記録 |

**Tapo 系**: tapo_sensors は tapo/python-kasa 両対応。tapo_lighting は python-kasa。**TAPO_HUB_IP**（H100）と **TAPO_LIGHTING_IP**（P300）は別デバイス。トラブル時は [tapo-status-report.md](tapo-status-report.md) を参照。

**sensor_readings の source カラム**: Tapo 系（python-kasa）の reading には `source='python-kasa'` が付与される。過去ログとの照合や将来のライブラリ切り替え時に利用。

---

## 環境変数

| 変数 | 説明 | デフォルト |
|------|------|------------|
| `SOURCES` | 有効にするソース（カンマ区切り） | `mock` |
| `TAPO_BACKEND` | tapo_sensors のライブラリ。`tapo` または `python-kasa`（未設定時） | `python-kasa` |
| `TAPO_HUB_IP` | H100 の IP（温湿度センサー用） | - |
| `TAPO_LIGHTING_IP` | P300 マルチタップの IP（照明 ON/OFF 用）。H100 とは別デバイス | - |
| `TDS_SENSOR_ID` | TDS の sensor_id。テスト時は `tds_test_ch1` 推奨 | `tds_ch1` |
| `TDS_K` | 電圧→ppm の係数。キャリブレーション用 | `500` |
| `GPIO_TEMP_INTERVAL` | 水温の取得間隔（秒） | `60` |
| `TDS_INTERVAL` | TDS の取得間隔（秒）。テスト時は `10` 等に短縮可 | `60` |
| `SAMPLE_INTERVAL` | Tapo 等の取得間隔（秒） | Tapo あり: 300、なし: 5 |
| `OPS_METRICS_ENABLED` | ops_metrics 収集を有効化 | `true` |
| `SYSTEM_STATS_INTERVAL` | システムメトリクス取得間隔（秒） | `60` |

---

## Grafana クエリ例

```sql
-- 水温
WHERE sensor_id = 'ds18b20_water_28_00001117a4e0' AND metric = 'temperature'

-- TDS（本番）
WHERE sensor_id = 'tds_ch1' AND metric = 'tds'

-- TDS（テスト中）
WHERE sensor_id = 'tds_test_ch1' AND metric = 'tds'

-- tapo_lighting（P300 照明 ON/OFF）。sensor_id は P300 のデバイスごとに異なる
WHERE metric = 'power_state' AND sensor_id LIKE 'tapo_lighting_%' AND $__timeFilter(time)
-- 特定デバイス指定の例:
-- WHERE metric = 'power_state' AND sensor_id = 'tapo_lighting_80227057FCADBA274FA7573C40B966F923F67C8D00' AND $__timeFilter(time)
```
