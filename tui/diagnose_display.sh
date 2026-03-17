#!/bin/bash
# ディスプレイ真っ暗の診断スクリプト（Pi 5 対応）
# SSH から実行: ./diagnose_display.sh
# 結果は /tmp/display_diagnostic.txt に保存

LOG=/tmp/display_diagnostic.txt
exec > >(tee -a "$LOG") 2>&1

echo "=== AquaPulse ディスプレイ診断 $(date) ==="
echo ""

# 0. Pi 5 ケーブル確認（重要）
echo "--- 0. Pi 5 ケーブル確認 ---"
echo "Pi 5 は 22pin 0.5mm の MIPI コネクタを使用。"
echo "カメラ用とディスプレイ用のアダプタケーブルは配線が異なり、互換性なし。"
echo "→ ディスプレイ接続には「ディスプレイ用」アダプタケーブルが必要。"
echo "  カメラ用ケーブルを使うと I2C タイムアウトで検出されない。"
echo ""

# 1. tty1 への簡単な出力テスト
echo "--- 1. tty1 出力テスト ---"
echo "以下を tty1 に書き込みます（ディスプレイに表示されるはず）:"
MSG="Display Test $(date +%H:%M:%S) - tty1 OK"
printf "\033[2J\033[H%s\n" "$MSG" | sudo tee /dev/tty1 >/dev/null
echo "書き込み完了: $MSG"
echo "→ ディスプレイに何か表示されましたか？ (y/n)"
echo ""

# 2. フレームバッファ
echo "--- 2. フレームバッファ ---"
if [ -e /dev/fb0 ]; then
  echo "/dev/fb0 存在"
  ls -la /dev/fb* 2>/dev/null || true
else
  echo "/dev/fb0 なし"
fi
echo ""

# 3. DRM デバイス
echo "--- 3. DRM デバイス ---"
ls -la /dev/dri/* 2>/dev/null || echo "DRM デバイスなし"
echo ""

# 4. コンソール設定
echo "--- 4. 仮想コンソール ---"
cat /sys/class/tty/tty0/active 2>/dev/null || echo "取得不可"
echo "現在の VC: $(cat /sys/class/tty/tty0/active 2>/dev/null)"
echo ""

# 5. config.txt のディスプレイ関連
echo "--- 5. /boot/firmware/config.txt のディスプレイ設定 ---"
for f in /boot/firmware/config.txt /boot/config.txt; do
  if [ -f "$f" ]; then
    echo "ファイル: $f"
    grep -E "^(hdmi|dtoverlay|display_|dpi_|lcd_|enable_dpi)" "$f" 2>/dev/null || echo "(該当行なし)"
    break
  fi
done
echo ""

# 6. dmesg のディスプレイ関連
echo "--- 6. dmesg ディスプレイ関連 ---"
dmesg 2>/dev/null | grep -iE "drm|dsi|hdmi|display|vc4|backlight|panel" | tail -30
echo ""

# 6b. I2C タイムアウト（ケーブル誤用の典型的症状）
echo "--- 6b. I2C エラー（カメラケーブル誤用で発生） ---"
dmesg 2>/dev/null | grep -iE "i2c.*timeout|i2c.*timed out|rpi_touchscreen|6-0045|deferred probe" || echo "(該当なし)"
echo ""

# 6c. RP1 / DSI ホスト（Pi 5 の DSI は RP1 チップが制御）
echo "--- 6c. RP1 / DSI ホスト ---"
dmesg 2>/dev/null | grep -iE "rp1|mipi.*dsi|dsi.*host" | tail -15
echo ""

# 7. ディスプレイ優先度（Pi 5）
echo "--- 7. ディスプレイ優先度 (Pi 5) ---"
if [ -f /boot/firmware/config.txt ]; then
  grep -E "hdmi_force_hotplug|display_default_lcd|dtoverlay=vc4" /boot/firmware/config.txt 2>/dev/null || true
fi
echo ""

# 8. TUI ログ
echo "--- 8. TUI ログ (直近) ---"
tail -20 /tmp/aquapulse-tui.log 2>/dev/null || echo "ログなし"
echo ""

# 9. サービス状態
echo "--- 9. aquapulse-tui サービス ---"
systemctl status aquapulse-tui 2>/dev/null | head -15 || echo "サービス未登録"
echo ""

# 10. バックライト（公式 7" は I2C 制御、Pi 5 では 6-0045 等）
echo "--- 10. バックライトデバイス ---"
ls -la /sys/class/backlight/ 2>/dev/null || echo "バックライトデバイスなし"
echo ""

# 11. DSI オーバーレイのポート（dsi0 vs dsi1）
echo "--- 11. DSI オーバーレイ設定 ---"
grep "vc4-kms-dsi" /boot/firmware/config.txt 2>/dev/null || echo "(未設定)"
echo ""

echo "=== 診断完了 ==="
echo "結果は $LOG に保存しました。"
echo ""
echo "【次のステップ】"
echo "1. test_display.sh を実行: sudo ./test_display.sh"
echo "   → 5秒間メッセージが表示される。何も出ない場合は tty1 とディスプレイの対応を疑う"
echo "2. Pi 5 ケーブル: ディスプレイ用アダプタケーブルを使用しているか確認（カメラ用は不可）"
echo "3. 6b で I2C タイムアウトが出た場合: カメラケーブル誤用の可能性が高い"
echo "4. 6c で DSI 関連ログが無い場合: オーバーレイが効いていないか、dsi0/dsi1 の指定を確認"
echo "5. 手動実行: sudo ./run_on_display.sh で TUI が表示されるか確認"
