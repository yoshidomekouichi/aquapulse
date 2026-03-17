CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE sensor_readings (
    time        TIMESTAMPTZ NOT NULL,
    sensor_id   TEXT NOT NULL,
    metric      TEXT NOT NULL,
    value       DOUBLE PRECISION NOT NULL,
    source      TEXT
);

SELECT create_hypertable('sensor_readings', 'time');

CREATE INDEX idx_sensor_readings_sensor_time ON sensor_readings (sensor_id, time DESC);