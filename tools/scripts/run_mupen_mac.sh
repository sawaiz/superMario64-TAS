#!/usr/bin/env bash
# Attempt to launch Mupen64 on macOS via Whisky/Wine if available.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
MUPEN="$ROOT/tools/mupen64/repack-stable-main/stable/mupen64.exe"

if [[ ! -f "$MUPEN" ]]; then
  echo "Mupen not found. Run: ./tools/scripts/download_tools.sh"
  exit 1
fi

cd "$(dirname "$MUPEN")"

if command -v whisky >/dev/null 2>&1; then
  echo "Launch via Whisky UI: add bottle and run $MUPEN"
fi

for wine in wine64 wine; do
  if command -v "$wine" >/dev/null 2>&1; then
    echo "Starting Mupen with $wine..."
    exec "$wine" mupen64.exe "$@"
  fi
done

if [[ -d "/Applications/Whisky.app" ]]; then
  echo "Whisky is installed. Open Whisky, create a Windows 10 bottle,"
  echo "then run: $MUPEN"
  open -a Whisky
  exit 0
fi

cat <<EOF
No Wine/Whisky found in PATH.

Mupen64-rr is a Windows TAS emulator. On Apple Silicon macOS, pick one:

  1) Install Whisky:  brew install --cask whisky
  2) Install Wine:    brew install wine-stable   # if bottle available
  3) Use Parallels/UTM Windows 11 ARM VM (most reliable for STROOP + Mupen)
  4) Run on a Windows PC and sync this git repo

Binary ready at:
  $MUPEN

For casual SM64 play (not .m64 TAS playback):
  brew install --cask ares-emulator && open -a ares
EOF
exit 1
