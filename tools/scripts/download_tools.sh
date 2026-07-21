#!/usr/bin/env bash
# Download SM64 TAS tools into this repository.
# Usage: from repo root: ./tools/scripts/download_tools.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

mkdir -p tools/mupen64 tools/STROOP

echo "==> Mupen64 stable repack (SM64 TAS community standard)"
curl -L --fail -o tools/mupen64/mupen64-repack-stable.zip \
  "https://github.com/mupen64/repack-stable/archive/refs/heads/main.zip"
rm -rf tools/mupen64/repack-stable-main
unzip -q tools/mupen64/mupen64-repack-stable.zip -d tools/mupen64/
echo "    Extracted to tools/mupen64/repack-stable-main/stable/mupen64.exe"

echo "==> STROOP (dev build)"
curl -L --fail -o tools/STROOP/STROOP-vDev.zip \
  "https://github.com/SM64-TAS-ABC/STROOP/releases/download/vDev/STROOP.zip"
rm -rf tools/STROOP/net461
unzip -q tools/STROOP/STROOP-vDev.zip -d tools/STROOP/
echo "    Extracted to tools/STROOP/net461/STROOP.exe (or similar)"

echo "==> Done. Place a legally obtained Super Mario 64 ROM in:"
echo "    tools/mupen64/repack-stable-main/stable/roms/"
echo "    Expected: Super Mario 64 (USA) .z64 / .n64 / .v64"
echo "    USA MD5 (big-endian .z64): 20b854b239203baf6c961b850a4a51a2"
echo ""
echo "Mupen64 is Windows-only. On macOS, run via Wine/Whisky/Crossover or a Windows VM."
echo "Docs: https://mupen64.com/"
