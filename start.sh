#!/usr/bin/env bash
# Vidify one-shot launcher.
#
# Creates a Python venv, installs backend + frontend deps (first run only),
# builds the frontend, launches the FastAPI server, and opens
# http://localhost:7860 in your browser.
#
# Flags:
#   --dev         run backend and frontend separately with hot reload
#   --no-open     don't try to open the browser
#   --port N      override the backend port (default 7860)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

DEV=0
OPEN=1
PORT=7860
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dev) DEV=1; shift ;;
    --no-open) OPEN=0; shift ;;
    --port) PORT="$2"; shift 2 ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "unknown flag: $1" >&2; exit 2 ;;
  esac
done

if ! command -v python3 >/dev/null; then
  echo "error: python3 is required" >&2; exit 1
fi
if ! command -v node >/dev/null; then
  echo "error: node is required (install Node.js 18+)" >&2; exit 1
fi
if ! command -v ffmpeg >/dev/null; then
  echo "warning: ffmpeg not found on PATH — some models will fail" >&2
fi

VENV="$SCRIPT_DIR/backend/.venv"
if [[ ! -d "$VENV" ]]; then
  echo "[1/4] Creating Python venv in backend/.venv…"
  python3 -m venv "$VENV"
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"
pip install --quiet --upgrade pip

if ! python -c "import vidify" >/dev/null 2>&1; then
  echo "[2/4] Installing backend dependencies…"
  pip install --quiet -e "$SCRIPT_DIR/backend"
fi

if [[ ! -d "$SCRIPT_DIR/frontend/node_modules" ]]; then
  echo "[3/4] Installing frontend dependencies…"
  (cd "$SCRIPT_DIR/frontend" && npm install --silent)
fi

if [[ $DEV -eq 1 ]]; then
  echo "[4/4] Dev mode: starting FastAPI (:$PORT, reload) + Vite (:5173)…"
  export VIDIFY_DEV=1 VIDIFY_PORT="$PORT"
  (cd "$SCRIPT_DIR/frontend" && npm run dev) &
  FRONTEND_PID=$!
  trap 'kill $FRONTEND_PID 2>/dev/null || true' EXIT INT TERM
  python -m vidify.main
else
  if [[ ! -f "$SCRIPT_DIR/frontend/dist/index.html" ]]; then
    echo "[4/4] Building frontend…"
    (cd "$SCRIPT_DIR/frontend" && npm run build --silent)
  fi
  URL="http://localhost:$PORT"
  echo "[4/4] Starting Vidify at $URL"
  if [[ $OPEN -eq 1 ]]; then
    (sleep 1.5 && (xdg-open "$URL" >/dev/null 2>&1 || open "$URL" >/dev/null 2>&1 || true)) &
  fi
  export VIDIFY_PORT="$PORT"
  python -m vidify.main
fi
