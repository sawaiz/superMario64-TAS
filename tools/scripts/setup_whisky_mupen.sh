#!/usr/bin/env bash
# Create / update a Whisky bottle and open Mupen64 for TAS validation on macOS.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
MUPEN_DIR="$ROOT/tools/mupen64/repack-stable-main/stable"
MUPEN_EXE="$MUPEN_DIR/mupen64.exe"
BOTTLE_NAME="${BOTTLE_NAME:-SM64-TAS}"

if [[ ! -f "$MUPEN_EXE" ]]; then
  echo "Mupen missing. Run: ./tools/scripts/download_tools.sh"
  exit 1
fi

# Ensure ROM is in mupen roms folder
ROM_SRC=""
for c in \
  "$ROOT/Super Mario 64 (USA).z64" \
  "$ROOT/roms/Super Mario 64 (USA).z64" \
  "$ROOT/roms/built/sm64.us.z64"
do
  if [[ -f "$c" ]]; then ROM_SRC="$c"; break; fi
done
if [[ -n "$ROM_SRC" ]]; then
  mkdir -p "$MUPEN_DIR/roms"
  cp -f "$ROM_SRC" "$MUPEN_DIR/roms/Super Mario 64 (USA).z64"
  echo "ROM staged in Mupen roms/: $(basename "$ROM_SRC")"
fi

if [[ ! -d /Applications/Whisky.app ]]; then
  echo "Whisky not installed. Install with:"
  echo "  brew install --cask whisky"
  echo "(Note: cask is deprecated/unmaintained as of 2026 — still works on many Macs.)"
  exit 1
fi

echo "Opening Whisky..."
open -a Whisky

cat <<EOF

=== Whisky + Mupen validation checklist ===

1. In Whisky: create a bottle named "$BOTTLE_NAME" (Windows 10, GPTK if available).
2. Bottle → Open C: Drive (or Config → Open Wine configuration as needed).
3. Copy or pin this path as a program:
     $MUPEN_EXE
   Tip: You can "Run..." and select mupen64.exe directly from Finder via Whisky.

4. In Mupen:
   - Confirm Super Mario 64 (USA) appears in the ROM list
   - Load game, optional: drag SM64LuaRedux/src/SM64Lua.lua onto the window
   - Movie → Play: pick a .m64 from:
       $ROOT/tas/full-game/
       $ROOT/tas/archive/SM64TASArchive/

5. Validation goals (console-first — see notes/console-first.md):
   - Retail ROM MD5 (USA z64): 20b854b239203baf6c961b850a4a51a2
   - Built matching decomp SHA1 (US): 9bef1128717f958171a4afac3ed78ee2bb4e86ce
   - 1-key TAS is typically **Japan** — need baserom.jp for those movies
   - USA archive ILs need USA ROM (you have this)
   - Mupen sync is necessary but not sufficient — PU/lag must be console-safe
   - Finished movies should be replayable on real N64 (TASbot / verify path)

CLI (if whisky cmd supports it on your version):
  whisky list
  # Create bottle via GUI if CLI create is unavailable

EOF

# Try whisky CLI if present
if command -v whisky >/dev/null 2>&1; then
  echo "--- whisky CLI ---"
  whisky --help 2>&1 | head -40 || true
  whisky list 2>&1 || true
fi
