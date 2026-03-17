#!/bin/bash
#
# ディスプレイ輝度制御スクリプト
# Usage: ./brightness.sh [0-255 | day | night | dim | off]
#
# ⚠️ 現在 I2C 通信エラーのため動作しません
# 詳細: docs/display/grafana-kiosk.md「既知の問題」参照
#

BACKLIGHT="/sys/class/backlight/11-0045/brightness"

# プリセット値
BRIGHTNESS_DAY=255      # 昼間（太陽光）
BRIGHTNESS_NIGHT=150    # 夜（室内照明）
BRIGHTNESS_DIM=50       # 暗め（就寝前）
BRIGHTNESS_OFF=10       # 最小（真っ暗、完全オフは見えなくなる）

set_brightness() {
    local value=$1
    if [ "$value" -ge 0 ] && [ "$value" -le 255 ]; then
        echo "$value" | sudo tee "$BACKLIGHT" > /dev/null
        echo "Brightness set to: $value"
    else
        echo "Error: Value must be 0-255"
        exit 1
    fi
}

show_current() {
    echo "Current brightness: $(cat $BACKLIGHT) / 255"
}

case "${1:-}" in
    day)
        set_brightness $BRIGHTNESS_DAY
        ;;
    night)
        set_brightness $BRIGHTNESS_NIGHT
        ;;
    dim)
        set_brightness $BRIGHTNESS_DIM
        ;;
    off)
        set_brightness $BRIGHTNESS_OFF
        ;;
    [0-9]*)
        set_brightness "$1"
        ;;
    status|"")
        show_current
        ;;
    *)
        echo "Usage: $0 [0-255 | day | night | dim | off | status]"
        echo ""
        echo "Presets:"
        echo "  day   = $BRIGHTNESS_DAY (太陽光の中でも見える)"
        echo "  night = $BRIGHTNESS_NIGHT (室内照明)"
        echo "  dim   = $BRIGHTNESS_DIM (就寝前)"
        echo "  off   = $BRIGHTNESS_OFF (最小)"
        exit 1
        ;;
esac
