#!/bin/bash
#
# Grafana Kiosk インストールスクリプト
# Raspberry Pi 5 + Pi Touch Display 1 用
#

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVICE_FILE="grafana-kiosk.service"

echo "=========================================="
echo " Grafana Kiosk インストーラー"
echo "=========================================="
echo ""

# --- Root 確認 ---
if [ "$EUID" -ne 0 ]; then
    echo "Error: このスクリプトは root 権限で実行してください"
    echo "Usage: sudo $0"
    exit 1
fi

# --- Step 1: パッケージインストール ---
echo "[1/5] 必要なパッケージをインストール中..."
apt update
apt install -y cage chromium fonts-noto-cjk wtype

# --- Step 2: スクリプトの実行権限 ---
echo "[2/5] スクリプトに実行権限を付与..."
chmod +x "${SCRIPT_DIR}/start-kiosk.sh"

# --- Step 3: DRM デバイスの確認 ---
echo "[3/5] DRM デバイスを確認中..."
echo ""
echo "利用可能な DRM デバイス:"
ls -la /dev/dri/
echo ""

# DSI ディスプレイがどのカードか推測
if [ -d "/sys/class/drm/card1-DSI-1" ]; then
    DRM_DEVICE="/dev/dri/card1"
    echo "DSI ディスプレイは card1 に接続されています"
elif [ -d "/sys/class/drm/card0-DSI-1" ]; then
    DRM_DEVICE="/dev/dri/card0"
    echo "DSI ディスプレイは card0 に接続されています"
else
    DRM_DEVICE="/dev/dri/card1"
    echo "DSI を自動検出できません。card1 をデフォルトとして使用します"
    echo "表示されない場合は service ファイルで card0 に変更してください"
fi

# --- Step 4: systemd サービスのインストール ---
echo "[4/5] systemd サービスをインストール中..."

# DRM デバイスを置換してコピー
sed "s|/dev/dri/card1|${DRM_DEVICE}|g" "${SCRIPT_DIR}/${SERVICE_FILE}" > /etc/systemd/system/${SERVICE_FILE}

systemctl daemon-reload

# --- Step 5: getty と TUI の無効化 ---
echo "[5/5] getty@tty1 と旧 TUI サービスを無効化中..."
systemctl disable getty@tty1 2>/dev/null || true
systemctl stop aquapulse-tui.service 2>/dev/null || true
systemctl disable aquapulse-tui.service 2>/dev/null || true

# --- 画面スリープ無効化の確認 ---
echo ""
echo "=========================================="
echo " インストール完了！"
echo "=========================================="
echo ""
echo "次のステップ:"
echo ""
echo "1. cmdline.txt に consoleblank=0 を追加（画面スリープ防止）:"
echo "   sudo nano /boot/firmware/cmdline.txt"
echo "   # 末尾に 'consoleblank=0' を追加"
echo ""
echo "2. ダッシュボードURLを設定:"
echo "   sudo nano /etc/systemd/system/${SERVICE_FILE}"
echo "   # Environment=GRAFANA_URL=http://localhost:3000/d/YOUR_DASHBOARD_ID?kiosk"
echo ""
echo "3. サービスを有効化・起動:"
echo "   sudo systemctl enable ${SERVICE_FILE%.service}"
echo "   sudo systemctl start ${SERVICE_FILE%.service}"
echo ""
echo "4. 再起動してテスト:"
echo "   sudo reboot"
echo ""
echo "トラブルシューティング:"
echo "   sudo journalctl -u ${SERVICE_FILE%.service} -f"
echo ""
