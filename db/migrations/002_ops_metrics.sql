-- ops_metrics: システム監視 + データ収集ヘルス用テーブル
-- sensor_readings とは役割が異なるため分離

CREATE TABLE IF NOT EXISTS ops_metrics (
    time        TIMESTAMPTZ NOT NULL,
    host        TEXT NOT NULL DEFAULT 'raspi5',
    category    TEXT NOT NULL,  -- 'system' | 'collector'
    metric      TEXT NOT NULL,
    source      TEXT,           -- collector の場合はソース名 (tapo_sensors, gpio_temp, etc.)
    value       DOUBLE PRECISION NOT NULL
);

SELECT create_hypertable('ops_metrics', 'time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_ops_metrics_category_time 
    ON ops_metrics (category, time DESC);

CREATE INDEX IF NOT EXISTS idx_ops_metrics_source_time 
    ON ops_metrics (source, time DESC) 
    WHERE source IS NOT NULL;

COMMENT ON TABLE ops_metrics IS 'システム監視・データ収集ヘルスメトリクス';
COMMENT ON COLUMN ops_metrics.category IS 'system: CPU/メモリ等, collector: データ収集状況';
COMMENT ON COLUMN ops_metrics.source IS 'collector カテゴリの場合のソース名';
