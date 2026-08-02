#!/usr/bin/env bash
# Keep Mac awake so tapo poller cron/launchd can reach LAN devices.
# Usage: ./scripts/keep-mac-awake.sh start|stop|status
set -euo pipefail

PIDFILE="${TMPDIR:-/tmp}/aquapulse-caffeinate.pid"

case "${1:-status}" in
  start)
    if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
      echo "Already running (pid $(cat "$PIDFILE"))"
      exit 0
    fi
    caffeinate -dimss &
    echo $! > "$PIDFILE"
    echo "Started caffeinate pid $(cat "$PIDFILE")"
    ;;
  stop)
    if [[ -f "$PIDFILE" ]]; then
      kill "$(cat "$PIDFILE")" 2>/dev/null || true
      rm -f "$PIDFILE"
      echo "Stopped"
    else
      pkill -f "caffeinate -dimss" 2>/dev/null || true
      echo "No pidfile"
    fi
    ;;
  status)
    if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
      echo "Running pid $(cat "$PIDFILE")"
    else
      echo "Not running"
    fi
    pmset -g | grep -E "sleep|displaysleep|disksleep"
    ;;
  *)
    echo "Usage: $0 start|stop|status" >&2
    exit 1
    ;;
esac
