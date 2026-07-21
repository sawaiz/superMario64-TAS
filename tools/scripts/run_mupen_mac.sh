#!/usr/bin/env bash
# Launch Mupen64 on macOS via Whisky (preferred) or Wine.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
MUPEN_DIR="$ROOT/tools/mupen64/repack-stable-main/stable"
MUPEN="$MUPEN_DIR/mupen64.exe"
BOTTLE="${WHISKY_BOTTLE:-SM64-TAS}"

if [[ ! -f "$MUPEN" ]]; then
  echo "Mupen not found. Run: ./tools/scripts/download_tools.sh"
  exit 1
fi

# Stage ROM if present at repo root
for c in "$ROOT/Super Mario 64 (USA).z64" "$ROOT/roms/Super Mario 64 (USA).z64" "$ROOT/roms/built/sm64.us.z64"; do
  if [[ -f "$c" ]]; then
    mkdir -p "$MUPEN_DIR/roms"
    cp -f "$c" "$MUPEN_DIR/roms/Super Mario 64 (USA).z64"
    break
  fi
done

if command -v whisky >/dev/null 2>&1; then
  if ! whisky list 2>/dev/null | grep -q "$BOTTLE"; then
    echo "Creating Whisky bottle $BOTTLE ..."
    whisky create "$BOTTLE"
  fi
  echo "Launching Mupen via Whisky bottle $BOTTLE ..."
  exec whisky run "$BOTTLE" "$MUPEN" "$@"
fi

cd "$MUPEN_DIR"
for wine in wine64 wine; do
  if command -v "$wine" >/dev/null 2>&1; then
    echo "Starting Mupen with $wine..."
    exec "$wine" mupen64.exe "$@"
  fi
done

if [[ -d "/Applications/Whisky.app" ]]; then
  echo "Whisky app present but CLI missing from PATH. Opening Whisky..."
  open -a Whisky
  exit 0
fi

cat <<EOF
No Whisky/Wine found.

  brew install --cask whisky
  whisky create SM64-TAS
  ./tools/scripts/run_mupen_mac.sh

Binary: $MUPEN
Casual play (not TAS): brew install --cask ares-emulator && open -a ares
EOF
exit 1
