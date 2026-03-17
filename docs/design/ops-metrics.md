# Ops Metrics（運用メトリクス）

システム監視とデータ収集ヘルスのためのメトリクス設計。

`sensor_readings` テーブル（アクアリウムデータ）とは役割が異なるため、`ops_metrics` テーブルに分離。

---

## テーブル構造

```sql
CREATE TABLE ops_metrics (
    time        TIMESTAMPTZ NOT NULL,
    host        TEXT NOT NULL DEFAULT 'raspi5',
    category    TEXT NOT NULL,  -- 'system' | 'collector'
    metric      TEXT NOT NULL,
    source      TEXT,           -- collector の場合はソース名
    value       DOUBLE PRECISION NOT NULL
);
```

---

## メトリクス一覧

### システム（`category = 'system'`）

| metric | 説明 | 単位 |
|--------|------|------|
| `cpu_percent` | CPU 使用率 | % |
| `memory_percent` | メモリ使用率 | % |
| `disk_percent` | ディスク使用率（/） | % |
| `cpu_temp` | CPU 温度 | °C |
| `load_1m` | ロードアベレージ（1分） | - |

### データ収集（`category = 'collector'`）

| metric | source | 説明 |
|--------|--------|------|
| `collection_success` | ソース名 | 成功=1, 失敗=0 |
| `collection_duration_ms` | ソース名 | 収集にかかった時間 (ms) |
| `readings_count` | ソース名 | 取得したデータ件数 |

---

## 環境変数

| 変数 | 説明 | デフォルト |
|------|------|------------|
| `OPS_METRICS_ENABLED` | ops_metrics 収集を有効化 | `true` |
| `SYSTEM_STATS_INTERVAL` | システムメトリクス取得間隔（秒） | `60` |

---

## Grafana クエリ例

```sql
-- CPU 使用率（過去1時間）
SELECT time, value FROM ops_metrics
WHERE category = 'system' AND metric = 'cpu_percent'
  AND $__timeFilter(time)
ORDER BY time;

-- 各ソースの成功率（過去1時間）
SELECT source,
       AVG(value) * 100 AS success_rate_percent
FROM ops_metrics
WHERE category = 'collector' AND metric = 'collection_success'
  AND time > NOW() - INTERVAL '1 hour'
GROUP BY source;

-- 最終成功時刻
SELECT source, MAX(time) AS last_success
FROM ops_metrics
WHERE category = 'collector' AND metric = 'collection_success' AND value = 1
GROUP BY source;

-- 収集レイテンシ（過去1時間）
SELECT time, source, value AS duration_ms
FROM ops_metrics
WHERE category = 'collector' AND metric = 'collection_duration_ms'
  AND $__timeFilter(time)
ORDER BY time;
```

---

## アラート基準（参考）

| 条件 | しきい値 | 意味 |
|------|----------|------|
| CPU 使用率 | > 80% 継続 | 高負荷 |
| メモリ使用率 | > 85% | メモリ不足 |
| ディスク使用率 | > 80% | ディスク残量警告 |
| CPU 温度 | > 70°C | オーバーヒート |
| 収集成功率 | < 90% | データ欠損リスク |
| 収集レイテンシ | > 10000ms | 処理遅延 |

---

## 関連ファイル

| ファイル | 役割 |
|----------|------|
| `db/migrations/002_ops_metrics.sql` | テーブル作成 |
| `collector/src/sources/system_stats.py` | システムメトリクス取得 |
| `collector/src/db/writer.py` | ops_metrics への書き込み |
| `collector/src/main.py` | 収集ヘルス計測・統合 |
