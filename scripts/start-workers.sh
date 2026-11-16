#!/usr/bin/env bash
set -e

# Resolve project root directory (one level up from scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
  echo "Usage: $0 [num_workers]"
  echo ""
  echo "Arguments:"
  echo "  num_workers   Number of worker processes to launch (default: 4)"
  echo ""
  echo "Example:"
  echo "  $0 6"
  exit 0
fi

NUM_WORKERS="${1:-4}"

# Validate argument is a positive integer
if ! [[ "$NUM_WORKERS" =~ ^[1-9][0-9]*$ ]]; then
  echo "Error: Number of workers must be a positive integer. Received: '$NUM_WORKERS'" >&2
  echo "Usage: $0 [num_workers]" >&2
  echo "Example: $0 4" >&2
  exit 1
fi

echo "Starting $NUM_WORKERS PyQueue workers..."

pids=()

cleanup() {
  echo ""
  echo "Stopping all $NUM_WORKERS workers..."
  for pid in "${pids[@]}"; do
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null
    fi
  done
  wait "${pids[@]}" 2>/dev/null
  echo "All workers stopped."
}

trap cleanup SIGINT SIGTERM EXIT

for i in $(seq 1 "$NUM_WORKERS"); do
  echo "  -> Starting Worker #$i..."
  uv run python -m app.workers.worker &
  pids+=($!)
done

echo "Successfully started $NUM_WORKERS workers."
echo "Press Ctrl+C to terminate all workers."

# Disable exit on error for wait so cleanup runs cleanly on interruption
set +e
wait
