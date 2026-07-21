#!/usr/bin/env bash
# Download published Super Mario 64 TAS movies from TASVideos and refresh the community archive.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

mkdir -p \
  tas/full-game/1-key \
  tas/full-game/16-stars \
  tas/full-game/70-stars-no-blj \
  tas/full-game/120-stars \
  tas/full-game/all-trees \
  tas/archive

echo "==> TASVideos publications (BizHawk .bk2 + 1-Key .m64)"
# 1 Key — https://tasvideos.org/4490M
curl -L --fail -o tas/full-game/1-key/4490M.bk2 \
  "https://tasvideos.org/4490M?handler=Download"
curl -L --fail -o tas/full-game/1-key/1key-m64.zip \
  "https://tasvideos.org/4490M?fileId=12639&handler=DownloadAdditional"
unzip -qo tas/full-game/1-key/1key-m64.zip -d tas/full-game/1-key/

# 120 Stars — https://tasvideos.org/2208M
curl -L --fail -o tas/full-game/120-stars/2208M.bk2 \
  "https://tasvideos.org/2208M?handler=Download"

# 70 Stars no BLJ — https://tasvideos.org/2062M
curl -L --fail -o tas/full-game/70-stars-no-blj/2062M.bk2 \
  "https://tasvideos.org/2062M?handler=Download"

# 16 Stars — https://tasvideos.org/6943M
curl -L --fail -o tas/full-game/16-stars/6943M.bk2 \
  "https://tasvideos.org/6943M?handler=Download"

# All Trees — https://tasvideos.org/7239M
curl -L --fail -o tas/full-game/all-trees/7239M.bk2 \
  "https://tasvideos.org/7239M?handler=Download"

echo "==> Community SM64 TAS Archive (IL WRs, full-game .m64 milestones)"
if [[ -d tas/archive/SM64TASArchive ]]; then
  echo "    Archive already present at tas/archive/SM64TASArchive (skipping clone)"
  echo "    To refresh: rm -rf tas/archive/SM64TASArchive && re-run this script"
else
  git clone --depth 1 https://github.com/TimeTravelPenguin/SM64TASArchive.git \
    tas/archive/SM64TASArchive
  rm -rf tas/archive/SM64TASArchive/.git
fi

echo "==> Done. Movie catalog:"
find tas -name '*.m64' -o -name '*.bk2' | sort | head -50
echo "..."
echo "Total .m64: $(find tas -name '*.m64' | wc -l | tr -d ' ')"
echo "Total .bk2: $(find tas -name '*.bk2' | wc -l | tr -d ' ')"
