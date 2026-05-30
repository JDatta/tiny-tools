#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$ROOT_DIR/.venv/bin/python"

if [[ ! -x "$PYTHON" ]]; then
  cat >&2 <<EOF
Missing virtual environment: $ROOT_DIR/.venv

Run:
  ./setup_venv.sh

Then run:
  ./photobackup.sh [--dry-run] [--mock-copy] <source_directory> <target_directory>
EOF
  exit 2
fi

exec "$PYTHON" "$ROOT_DIR/photobackup.py" "$@"
