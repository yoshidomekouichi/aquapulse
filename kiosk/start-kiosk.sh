#!/bin/bash
#
# Grafana Kiosk Startup Script
# For Raspberry Pi 5 + Pi Touch Display 1 (800x480)
#

set -e

# --- 設定 ---
# ダッシュボードURLを環境変数またはデフォルトから取得
# 例: http://localhost:3000/d/abc123/aquapulse?kiosk&refresh=30s
GRAFANA_URL="${GRAFANA_URL:-http://localhost:3000/?kiosk}"

# --- 環境変数 ---
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
export WLR_LIBINPUT_NO_DEVICES=1

# --- ログ ---
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

log "Starting Grafana Kiosk..."
log "URL: $GRAFANA_URL"

# --- Grafana が起動するまで待機 ---
log "Waiting for Grafana to be ready..."
MAX_WAIT=120
WAIT_COUNT=0
until curl -s -o /dev/null -w '' http://localhost:3000/api/health 2>/dev/null; do
    sleep 2
    WAIT_COUNT=$((WAIT_COUNT + 2))
    if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
        log "ERROR: Grafana did not become ready within ${MAX_WAIT}s"
        exit 1
    fi
done
log "Grafana is ready (waited ${WAIT_COUNT}s)."

# --- 少し待機（UIの安定化） ---
sleep 2

# --- Chromium 起動オプション ---
CHROMIUM_FLAGS=(
    --kiosk                               # 全画面キオスクモード
    --noerrdialogs                        # エラーダイアログを抑制
    --disable-infobars                    # 情報バーを非表示
    --disable-session-crashed-bubble      # クラッシュ復元バブルを抑制
    --disable-restore-session-state       # セッション復元を無効化
    --disable-features=TranslateUI        # 翻訳UIを無効化
    --disable-component-update            # コンポーネント更新を無効化
    --check-for-update-interval=31536000  # 更新チェック間隔を1年に
    --autoplay-policy=no-user-gesture-required  # 自動再生を許可
    --start-fullscreen                    # フルスクリーン開始
    --window-size=800,480                 # ウィンドウサイズ
    --window-position=0,0                 # ウィンドウ位置
    --hide-scrollbars                     # スクロールバーを非表示
    --incognito                           # シークレットモード（履歴なし）
    --disable-pinch                       # ピンチズームを無効化
    --overscroll-history-navigation=0     # スワイプ戻るを無効化
    --disable-gpu-vsync                   # 低負荷化
    --enable-features=OverlayScrollbar    # オーバーレイスクロールバー
    --ozone-platform=wayland              # Wayland使用を明示
    --disable-dev-shm-usage               # /dev/shm 使用を避ける
    --no-sandbox                          # サンドボックス無効（systemd用）
    --disable-setuid-sandbox              # setuid サンドボックス無効
)

log "Starting Chromium with flags: ${CHROMIUM_FLAGS[*]}"

# --- Chromium 起動 ---
exec chromium "${CHROMIUM_FLAGS[@]}" "$GRAFANA_URL"
