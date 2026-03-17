#!/bin/bash
# Pi Touch Display (tty1) で TUI を実行するスクリプト
cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)/packages:${PYTHONPATH:-}"
[ -f ../.env ] && set -a && . ../.env && set +a

# systemd サービスが動いていたら停止
sudo systemctl stop aquapulse-tui 2>/dev/null || true

# tty1 に切り替え
sudo chvt 1

# script で PTY を作成して TUI を実行（Textual が PTY を必要とする場合に対応）
exec script -q -c "python3 dashboard.py" /dev/null </dev/tty1 >/dev/tty1 2>/tmp/aquapulse-tui.log
