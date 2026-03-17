#!/bin/bash
# ディスプレイ出力のテスト。TUI の代わりに簡単なメッセージを表示
# systemd から実行するか、手動で: sudo ./test_display.sh
printf "\033[2J\033[H" >/dev/tty1
echo "AquaPulse Display Test - $(date)" >/dev/tty1
echo "If you see this, output to tty1 works." >/dev/tty1
sleep 5
