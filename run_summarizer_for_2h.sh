#!/usr/bin/env bash
# Run the timed summarizer for 2 hours using the project's virtualenv Python
# Adjust MINUTES or SLEEP as needed via env or CLI.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$SCRIPT_DIR/.venv/bin/python"
APP="$SCRIPT_DIR/summarize_for_duration.py"

# Defaults
MINUTES=${MINUTES:-120}
SLEEP=${SLEEP:-15}

if [[ ! -x "$PY" ]]; then
  echo "Virtualenv Python not found at $PY"
  echo "Create venv and install deps:"
  echo "  python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
  exit 1
fi

exec "$PY" "$APP" --minutes "$MINUTES" --sleep "$SLEEP"
