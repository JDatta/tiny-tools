#!/usr/bin/env bash
set -euo pipefail

SCRIPT_PATH="${BASH_SOURCE[0]}"
while [[ -L "$SCRIPT_PATH" ]]; do
  SCRIPT_DIR="$(cd -P "$(dirname "$SCRIPT_PATH")" && pwd)"
  SCRIPT_PATH="$(readlink "$SCRIPT_PATH")"
  [[ "$SCRIPT_PATH" != /* ]] && SCRIPT_PATH="$SCRIPT_DIR/$SCRIPT_PATH"
done
ROOT_DIR="$(cd -P "$(dirname "$SCRIPT_PATH")" && pwd)"
PYTHON="$ROOT_DIR/.venv/bin/python"

if [[ ! -x "$PYTHON" ]]; then
  cat >&2 <<EOF
Missing virtual environment: $ROOT_DIR/.venv

Run:
  cd "$ROOT_DIR"
  ./setup.sh

Then run:
  ./photobackup.sh [--dry-run] [--mock-copy] <source_directory> <target_directory>
EOF
  exit 2
fi

exec "$PYTHON" "$ROOT_DIR/photobackup.py" "$@"
