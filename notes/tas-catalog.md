# TAS Catalog

Movies collected in this repository (downloaded for study; authors retain credit).

## TASVideos publications (`tas/full-game/`)

| Category | Time (pub.) | ID | Files | Region notes |
|----------|-------------|-----|-------|--------------|
| **1 Key** | 04:18.983 | [4490M](https://tasvideos.org/4490M) | `1-key/*.m64`, `4490M.bk2` | Mupen-origin; J; console-verified encode exists |
| **16 Stars** | 13:28.400 | [6943M](https://tasvideos.org/6943M) | `16-stars/6943M.bk2` | Legacy MIPS route category |
| **70 Stars, no BLJ** | 42:58.517 | [2062M](https://tasvideos.org/2062M) | `70-stars-no-blj/2062M.bk2` | Showcases non-BLJ tech |
| **120 Stars** | 1:20:41.517 | [2208M](https://tasvideos.org/2208M) | `120-stars/2208M.bk2` | Collaborative classic |
| **All Trees** | 08:25.183 | [7239M](https://tasvideos.org/7239M) | `all-trees/7239M.bk2` | Joke/alternate goal |

`.bk2` = BizHawk movie archive (zip). `.m64` = Mupen rerecording movie.

### 1 Key authors (4490M)
Tyler_Kehne, mkdasher, sonicpacker, snark, SilentSlayers, ToT, Plush, Dabs, Gaehne D, Eru, sm64expert, dar gos, Superdavo0001, IsaacA — published 2021-07-21.

## Community archive (`tas/archive/SM64TASArchive/`)

Source: [TimeTravelPenguin/SM64TASArchive](https://github.com/TimeTravelPenguin/SM64TASArchive)

| Path | Contents |
|------|----------|
| `Full Game/1 Key/` | Milestone 1-key `.m64` |
| `Full Game/70 Stars/` | 70-star `.m64` |
| `Full Game/120 Stars/` | 120-star `.m64` (incl. 1h20m41s era) |
| `Individual Levels/SM64/` | Per-star IL WRs + savestates (BoB, WF, JRB, …) |
| `120/` | Additional 120 history |
| `Tools/` | Related utilities if present |
| `To Sort/` | Unsorted contributions |

Rough counts after clone: **~100+ `.m64` files**, plus savestates (`.st`).

## How to play back

1. **Mupen64** + matching ROM region → File / movie playback for `.m64`.
2. **BizHawk** N64 core → open `.bk2` for TASVideos packages.
3. Without a ROM, study **YouTube encodes** linked from TASVideos publication pages.

## Refresh downloads

```bash
./tools/scripts/download_tases.sh
```

## Attribution & redistribution

TASVideos republication rules apply to their encodes/movies (credit authors, label as TAS, don’t strip site pointers). Community archive: see its README; contribute improvements upstream via PR.
