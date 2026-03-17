-- sensor_readings に source カラムを追加（既存 DB 用）
-- 新規インストール時は 00_schema.sql に含まれるため不要
ALTER TABLE sensor_readings ADD COLUMN IF NOT EXISTS source TEXT;
