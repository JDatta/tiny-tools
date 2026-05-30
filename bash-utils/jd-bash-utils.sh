# jd-bash-utils.sh
#
# Source this file from ~/.bashrc to load a small set of interactive shell
# utilities. These functions intentionally avoid personal paths so they can be
# reused across machines.

jdsync() {
  local defaults=(-r -a -v -P --ignore-existing)

  if [ "$#" -eq 0 ] || [ "$1" = "--help" ] || [ "$1" = "help" ]; then
    cat <<'EOF'
Usage:
  jdsync [rsync options] <source...> <destination>

Default rsync options:
  -r -a -v -P --ignore-existing

Examples:
  jdsync ~/Pictures/ /run/media/$USER/Backup/Pictures/
  jdsync --dry-run ~/Pictures/ /run/media/$USER/Backup/Pictures/
  jdsync --delete ~/Pictures/ /run/media/$USER/Backup/Pictures/

Notes:
  Source trailing slashes follow normal rsync behavior.
  Any options passed to jdsync are forwarded to rsync after the defaults.
EOF
    if [ "$#" -eq 0 ]; then
      return 2
    fi
    return 0
  fi

  command rsync "${defaults[@]}" "$@"
}

shortlog() {
  command git log --oneline -n 10 "$@"
}

prettylog() {
  command git log --pretty=format:'%Cred%h%x09%Cblue%an%Creset%x09%s' "$@"
}

tojpg() {
  local f out ext

  if [ "$#" -eq 0 ]; then
    echo "usage: tojpg <image...>" >&2
    return 1
  fi

  for f in "$@"; do
    if [ ! -f "$f" ]; then
      echo "tojpg: not a file: $f" >&2
      continue
    fi

    out="${f%.*}.jpg"
    ext="${f##*.}"

    case "${ext,,}" in
      heic|heif)
        if ! command -v magick >/dev/null 2>&1; then
          echo "tojpg: ImageMagick 'magick' is required for $f" >&2
          return 1
        fi
        command magick "$f" "$out"
        ;;
      *)
        if ! command -v ffmpeg >/dev/null 2>&1; then
          echo "tojpg: ffmpeg is required for $f" >&2
          return 1
        fi
        command ffmpeg -y -i "$f" -q:v 2 "$out"
        ;;
    esac
  done
}
