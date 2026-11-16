#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
  echo "Usage: $0 [--port PORT] [--host HOST]"
  echo ""
  echo "Starts the PyQueue FastAPI server with uvicorn."
  echo "Environment variables HOST and PORT can also be configured."
  echo ""
  echo "Example:"
  echo "  $0"
  echo "  PORT=8080 $0"
  exit 0
fi

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

echo "Starting PyQueue API server on http://${HOST}:${PORT}..."
exec uv run uvicorn backend.main:app --host "$HOST" --port "$PORT" --reload "$@"
