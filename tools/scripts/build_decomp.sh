#!/usr/bin/env bash
# Build matching SM64 from n64decomp/sm64 (macOS / Linux).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DECOMP="$ROOT/decomp/sm64"
VERSION="${VERSION:-us}"
JOBS="${JOBS:-$(sysctl -n hw.ncpu 2>/dev/null || nproc 2>/dev/null || echo 4)}"

if [[ ! -d "$DECOMP" ]]; then
  echo "Cloning n64decomp/sm64..."
  mkdir -p "$ROOT/decomp"
  git clone --depth 1 https://github.com/n64decomp/sm64.git "$DECOMP"
fi

# Resolve baserom
BASEROM="$DECOMP/baserom.${VERSION}.z64"
if [[ ! -f "$BASEROM" ]]; then
  CANDIDATES=(
    "$ROOT/Super Mario 64 (USA).z64"
    "$ROOT/roms/Super Mario 64 (USA).z64"
    "$ROOT/roms/baserom.${VERSION}.z64"
  )
  for c in "${CANDIDATES[@]}"; do
    if [[ -f "$c" ]]; then
      echo "Copying baserom from: $c"
      cp "$c" "$BASEROM"
      break
    fi
  done
fi

if [[ ! -f "$BASEROM" ]]; then
  echo "Missing $BASEROM — place a legal Super Mario 64 ROM there."
  exit 1
fi

echo "baserom MD5: $(md5 -q "$BASEROM" 2>/dev/null || md5sum "$BASEROM" | awk '{print $1}')"
if [[ "$VERSION" == "us" ]]; then
  EXPECT="20b854b239203baf6c961b850a4a51a2"
  GOT="$(md5 -q "$BASEROM" 2>/dev/null || md5sum "$BASEROM" | awk '{print $1}')"
  if [[ "$GOT" != "$EXPECT" ]]; then
    echo "WARNING: USA baserom MD5 is $GOT (expected $EXPECT). Build may fail asset extract / compare."
  else
    echo "USA baserom MD5 OK."
  fi
fi

cd "$DECOMP"

# Prefer GNU make on macOS
if command -v gmake >/dev/null 2>&1; then
  MAKE=gmake
else
  MAKE=make
fi

# Detect cross prefix if needed
if ! command -v mips-linux-gnu-as >/dev/null 2>&1 \
   && ! command -v mips64-elf-as >/dev/null 2>&1 \
   && ! command -v mips64-linux-gnu-as >/dev/null 2>&1; then
  echo "ERROR: MIPS binutils not found."
  echo "  macOS: brew tap tehzz/n64-dev && brew install tehzz/n64-dev/mips64-elf-binutils"
  echo "  or use Docker: docker build -t sm64 . && docker run --rm -v \"\$PWD\":/sm64 sm64 make VERSION=$VERSION -j$JOBS"
  exit 1
fi

echo "Building VERSION=$VERSION with $MAKE -j$JOBS ..."
$MAKE VERSION="$VERSION" -j"$JOBS"

OUT="$DECOMP/build/${VERSION}/sm64.${VERSION}.z64"
if [[ -f "$OUT" ]]; then
  echo "Built: $OUT"
  echo "SHA1: $(shasum -a 1 "$OUT" | awk '{print $1}')"
  # Expected US: 9bef1128717f958171a4afac3ed78ee2bb4e86ce
  mkdir -p "$ROOT/roms/built"
  cp "$OUT" "$ROOT/roms/built/sm64.${VERSION}.z64"
  echo "Copied to roms/built/sm64.${VERSION}.z64"
else
  echo "Build finished but output not found at $OUT — check logs."
  exit 1
fi
