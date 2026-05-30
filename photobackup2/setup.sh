#!/usr/bin/env bash
set -euo pipefail

SCRIPT_PATH="${BASH_SOURCE[0]}"
while [[ -L "$SCRIPT_PATH" ]]; do
  SCRIPT_DIR="$(cd -P "$(dirname "$SCRIPT_PATH")" && pwd)"
  SCRIPT_PATH="$(readlink "$SCRIPT_PATH")"
  [[ "$SCRIPT_PATH" != /* ]] && SCRIPT_PATH="$SCRIPT_DIR/$SCRIPT_PATH"
done
ROOT_DIR="$(cd -P "$(dirname "$SCRIPT_PATH")" && pwd)"
cd "$ROOT_DIR"

BIN_DIR="$HOME/.local/bin"
LINK_PATH="$BIN_DIR/photobackup.sh"
PROFILE_MARKER_START="# >>> photobackup PATH setup >>>"

path_contains() {
  case ":${PATH:-}:" in
    *":$1:"*) return 0 ;;
    *) return 1 ;;
  esac
}

choose_profile_file() {
  if [[ -n "${BASH_VERSION:-}" && -f "$HOME/.bashrc" ]]; then
    printf '%s\n' "$HOME/.bashrc"
    return
  fi

  if [[ -f "$HOME/.profile" ]]; then
    printf '%s\n' "$HOME/.profile"
    return
  fi

  if [[ -n "${BASH_VERSION:-}" ]]; then
    printf '%s\n' "$HOME/.bashrc"
  else
    printf '%s\n' "$HOME/.profile"
  fi
}

ensure_path_profile_entry() {
  local profile_file="$1"
  touch "$profile_file"

  if grep -Fq "$PROFILE_MARKER_START" "$profile_file"; then
    return
  fi

  cat >>"$profile_file" <<'EOF'

# >>> photobackup PATH setup >>>
if [ -d "$HOME/.local/bin" ]; then
  case ":$PATH:" in
    *":$HOME/.local/bin:"*) ;;
    *) export PATH="$HOME/.local/bin:$PATH" ;;
  esac
fi
# <<< photobackup PATH setup <<<
EOF
}

python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

mkdir -p "$BIN_DIR"

path_was_missing=0
profile_file=""
if ! path_contains "$BIN_DIR"; then
  path_was_missing=1
  profile_file="$(choose_profile_file)"
  ensure_path_profile_entry "$profile_file"
  export PATH="$BIN_DIR:$PATH"
fi

if [[ -e "$LINK_PATH" && ! -L "$LINK_PATH" ]]; then
  cat >&2 <<EOF
Cannot install launcher because $LINK_PATH already exists and is not a symlink.
Move it aside or remove it, then rerun ./setup.sh.
EOF
  exit 2
fi

ln -sfn "$ROOT_DIR/photobackup.sh" "$LINK_PATH"

echo "Virtual environment ready."
echo "Installed launcher: $LINK_PATH -> $ROOT_DIR/photobackup.sh"

if (( path_was_missing )); then
  echo "Added $BIN_DIR to $profile_file for future shells."
  echo "Exported PATH for this setup process."
fi

echo "Run: photobackup.sh <source_directory> <target_directory>"
