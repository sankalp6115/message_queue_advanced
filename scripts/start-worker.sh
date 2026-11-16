#!/usr/bin/env bash
set -e

# Resolve project root directory (one level up from scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
  echo "Usage: $0 [worker_id]"
  echo ""
  echo "Starts a single PyQueue worker process."
  echo ""
  echo "Example:"
  echo "  $0"
  echo "  $0 2"
  exit 0
fi

WORKER_ID="${1:-1}"
echo "Starting PyQueue worker #$WORKER_ID..."
exec uv run python -m backend.workers.worker
