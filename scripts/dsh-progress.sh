#!/usr/bin/env bash
# Run a dsh headless task with a live progress bar and a full log.
#
# Usage:
#   scripts/dsh-progress.sh <projectPath> <task...>

set -euo pipefail

if [ $# -lt 2 ]; then
  echo "Usage: $0 <projectPath> <task...>" >&2
  exit 1
fi

PROJECT="$(cd "$1" && pwd)"
shift
TASK="$*"

CACHE="$PROJECT/floorplan/.cache"
mkdir -p "$CACHE"
PROGRESS="$CACHE/progress.json"
ANSWER="$CACHE/answer.txt"
LOG="$CACHE/adapter.log"

ADAPTER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

rm -f "$PROGRESS" "$ANSWER"
: > "$LOG"

( cd "$ADAPTER_DIR" && exec npx @deepseek-ai/dsh headless "$TASK" > "$ANSWER" 2>> "$LOG" ) &
DSH_PID=$!

draw() {
  local pct="$1" msg="$2" width=24 filled empty f e
  filled=$(( pct * width / 100 ))
  empty=$(( width - filled ))
  if [ "$filled" -gt 0 ]; then printf -v f "%${filled}s"; f=${f// /#}; else f=""; fi
  if [ "$empty"  -gt 0 ]; then printf -v e "%${empty}s";  e=${e// /.}; else e=""; fi
  printf "\r[%s%s] %3d%%  %s" "$f" "$e" "$pct" "$msg"
}

LAST=""
while kill -0 "$DSH_PID" 2>/dev/null; do
  if [ -f "$PROGRESS" ]; then
    pct=$(sed -n 's/.*"percent": *\([0-9]*\).*/\1/p' "$PROGRESS" | head -n1)
    msg=$(sed -n 's/.*"message": *"\([^"]*\)".*/\1/p' "$PROGRESS" | head -n1)
    if [ -n "${pct:-}" ] && [ -n "${msg:-}" ]; then
      KEY="$pct|$msg"
      if [ "$KEY" != "$LAST" ]; then
        draw "$pct" "$msg"
        LAST="$KEY"
      fi
    fi
  fi
  sleep 0.3
done

set +e
wait "$DSH_PID"
STATUS=$?
set -e

printf "\r\033[K"
if [ "$STATUS" -eq 0 ]; then printf "[########################] 100%%  Done\n"; else printf "[########################] 100%%  Failed\n"; fi
echo
echo

if [ -s "$ANSWER" ]; then
  echo "── Answer ──────────────────────────────────────────────"
  cat "$ANSWER"
  echo
  echo "────────────────────────────────────────────────────────"
else
  echo "No answer on stdout."
fi

echo "Full log: $LOG"
exit "$STATUS"
