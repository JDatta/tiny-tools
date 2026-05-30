#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source_file="${script_dir}/jd-bash-utils.sh"
target_dir="${HOME}/.bashrc.d"
target_file="${target_dir}/jd-bash-utils.sh"
bashrc="${HOME}/.bashrc"
source_line='[ -f "$HOME/.bashrc.d/jd-bash-utils.sh" ] && . "$HOME/.bashrc.d/jd-bash-utils.sh"'

if [ ! -f "$source_file" ]; then
  echo "setup.sh: missing source file: $source_file" >&2
  exit 1
fi

mkdir -p "$target_dir"
cp "$source_file" "$target_file"

if [ ! -f "$bashrc" ]; then
  printf '%s\n' "$source_line" > "$bashrc"
  echo "Created $bashrc and added jd-bash-utils source line."
  echo "Installed $target_file"
  exit 0
fi

if grep -Fq 'jd-bash-utils.sh' "$bashrc"; then
  echo "$bashrc already references jd-bash-utils.sh"
elif grep -Fq '.bashrc.d' "$bashrc"; then
  echo "$bashrc already sources files from .bashrc.d"
else
  {
    printf '\n'
    printf '# Load jd bash utilities.\n'
    printf '%s\n' "$source_line"
  } >> "$bashrc"
  echo "Updated $bashrc to source jd-bash-utils.sh"
fi

echo "Installed $target_file"
