# Decompilation workspace

## Trees

| Path | Source | Purpose |
|------|--------|---------|
| `sm64/` | [n64decomp/sm64](https://github.com/n64decomp/sm64) | **Matching** decomp — rebuild retail-equivalent ROMs |
| `HackerSM64/` | [HackerN64/HackerSM64](https://github.com/HackerN64/HackerSM64) | Romhack-oriented base (community standard) |
| `kaze/` | [KazeEmanuar](https://github.com/KazeEmanuar) forks/demos | Performance analysis & engine experiments |

## Baserom

Place or link your legal dump as:

```text
sm64/baserom.us.z64   # USA
sm64/baserom.jp.z64   # Japan (many any% / 1-key TASes)
```

This workshop already copies the USA ROM when present at the repo root.

**USA `.z64` MD5:** `20b854b239203baf6c961b850a4a51a2`  
**Built US ROM SHA1 (expected):** `9bef1128717f958171a4afac3ed78ee2bb4e86ce`

## Build (macOS)

```bash
# deps once
brew install coreutils make pkg-config
brew tap tehzz/n64-dev
brew install tehzz/n64-dev/mips64-elf-binutils

# from repo root
./tools/scripts/build_decomp.sh
# or: VERSION=us JOBS=8 ./tools/scripts/build_decomp.sh
```

Docker alternative (from `sm64/`):

```bash
docker build -t sm64 .
docker run --rm --mount type=bind,source="$(pwd)",destination=/sm64 sm64 make VERSION=us -j4
```

## Kaze analysis

See [../notes/kaze-emanuar.md](../notes/kaze-emanuar.md).

Do **not** use non-matching optimized engines when validating retail TAS movies.
