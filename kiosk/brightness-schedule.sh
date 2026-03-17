#!/bin/bash
#
# 時間帯に応じた自動輝度調整
# cron で毎時実行するか、systemd timer で使用
#
# ⚠️ 現在 I2C 通信エラーのため動作しません
# 詳細: docs/display/grafana-kiosk.md「既知の問題」参照
#

SCRIPT_DIR="$(dirname "$0")"
HOUR=$(date +%H)

# 時間帯設定（24時間制）
if [ "$HOUR" -ge 7 ] && [ "$HOUR" -lt 18 ]; then
    # 7:00-17:59 昼間
    "$SCRIPT_DIR/brightness.sh" day
elif [ "$HOUR" -ge 18 ] && [ "$HOUR" -lt 22 ]; then
    # 18:00-21:59 夜
    "$SCRIPT_DIR/brightness.sh" night
elif [ "$HOUR" -ge 22 ] || [ "$HOUR" -lt 1 ]; then
    # 22:00-00:59 就寝前
    "$SCRIPT_DIR/brightness.sh" dim
else
    # 1:00-6:59 深夜（最小）
    "$SCRIPT_DIR/brightness.sh" off
fi
