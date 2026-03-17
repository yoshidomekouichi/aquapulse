#!/bin/bash
# SSH ターミナルで TUI を実行（開発・内容修正用）
# このスクリプトで現在のターミナルに TUI が表示される
cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)/packages:${PYTHONPATH:-}"
[ -f ../.env ] && set -a && . ../.env && set +a

exec python3 dashboard.py
