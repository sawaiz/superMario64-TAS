#!/usr/bin/env bash
# Build matching n64decomp/sm64 via Docker (amd64) + Colima on Apple Silicon.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DECOMP="$ROOT/decomp/sm64"
VERSION="${VERSION:-us}"
JOBS="${JOBS:-4}"

export PATH="/opt/homebrew/bin:$PATH"
if [[ -S "${HOME}/.colima/docker.sock" ]]; then
  export DOCKER_HOST="unix://${HOME}/.colima/docker.sock"
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Install Docker CLI: brew install docker colima && colima start"
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "Starting Colima..."
  colima start --cpu 4 --memory 6 --disk 40 || true
  export DOCKER_HOST="unix://${HOME}/.colima/docker.sock"
fi

if [[ ! -d "$DECOMP" ]]; then
  git clone --depth 1 https://github.com/n64decomp/sm64.git "$DECOMP"
fi

BASEROM="$DECOMP/baserom.${VERSION}.z64"
if [[ ! -f "$BASEROM" ]]; then
  for c in "$ROOT/Super Mario 64 (USA).z64" "$ROOT/roms/Super Mario 64 (USA).z64"; do
    [[ -f "$c" ]] && cp "$c" "$BASEROM" && break
  done
fi
[[ -f "$BASEROM" ]] || { echo "Missing baserom.${VERSION}.z64"; exit 1; }

cd "$DECOMP"

# Prefer amd64 image — Ubuntu mips binutils packages exist on amd64
if [[ ! -f Dockerfile.amd64 ]]; then
  cat > Dockerfile.amd64 << 'EOF'
FROM --platform=linux/amd64 ubuntu:22.04 AS build
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    binutils-mips-linux-gnu \
    build-essential \
    git \
    pkgconf \
    python3 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /sm64
ENV PATH="/sm64/tools:${PATH}"
CMD ["make", "VERSION=us", "-j4"]
EOF
fi

echo "Building Docker image sm64 (linux/amd64)..."
docker buildx build --platform linux/amd64 -f Dockerfile.amd64 -t sm64 --load .

echo "Compiling VERSION=$VERSION ..."
docker run --rm --platform linux/amd64 \
  --mount type=bind,source="$(pwd)",destination=/sm64 \
  sm64 make VERSION="$VERSION" -j"$JOBS"

OUT="build/${VERSION}/sm64.${VERSION}.z64"
if [[ -f "$OUT" ]]; then
  echo "OK: $OUT"
  shasum -a 1 "$OUT"
  mkdir -p "$ROOT/roms/built"
  cp "$OUT" "$ROOT/roms/built/sm64.${VERSION}.z64"
  # Stage for Mupen validation
  mkdir -p "$ROOT/tools/mupen64/repack-stable-main/stable/roms"
  cp "$OUT" "$ROOT/tools/mupen64/repack-stable-main/stable/roms/sm64.${VERSION}.built.z64"
  echo "Copied to roms/built/ and Mupen roms/"
else
  echo "Build failed — no $OUT"
  exit 1
fi
