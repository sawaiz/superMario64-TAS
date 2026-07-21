# Super Mario 64 TAS Workshop

A local research workspace for **tool-assisted speedruns (TAS)** of *Super Mario 64*: community-standard emulator and diagnostics, published movies, historical IL archives, and study notes from **pannenkoek2012** and **Bismuth**.

> **Legal:** No ROMs are included. Dump SM64 from a cartridge you own (or obtain an image you are legally allowed to use) and place it in the Mupen `roms/` folder. See [notes/emulators-and-tools.md](notes/emulators-and-tools.md).

---

## Repository layout

```
superMario64-TAS/
├── README.md                 ← you are here
├── notes/
│   ├── pannenkoek2012.md     ← engine, ABC, PUs, collision
│   ├── bismuth.md            ← WR explainers, any%/120 routing
│   ├── emulators-and-tools.md
│   └── tas-catalog.md        ← what’s in tas/
├── tools/
│   ├── mupen64/              ← Mupen64 stable repack (TAS emulator)
│   ├── STROOP/               ← RAM observer / object processor
│   └── scripts/              ← re-download helpers
├── tas/
│   ├── full-game/            ← TASVideos pubs (1-key, 16, 70, 120, trees)
│   └── archive/SM64TASArchive/  ← community IL + full-game .m64 milestones
└── roms/                     ← your ROM goes here (gitignored)
```

---

## Quick start

### 1. Tools (already downloaded if you used the setup that created this tree)

```bash
./tools/scripts/download_tools.sh   # Mupen64 repack + STROOP
./tools/scripts/download_tases.sh   # TASVideos movies + SM64TASArchive
```

### 2. Emulator: **Mupen64** (best for SM64 TAS)

| | |
|--|--|
| **Why** | SM64 TAS community standard: `.m64` movies, rerecording, Lua, SM64 Lua Redux |
| **Binary** | `tools/mupen64/repack-stable-main/stable/mupen64.exe` |
| **Site** | https://mupen64.com/ |
| **OS** | Windows native; on **macOS** use Wine / Whisky / Crossover / a Windows VM |

1. Copy your ROM into `tools/mupen64/repack-stable-main/stable/roms/`.
2. Run `mupen64.exe`.
3. Load the game; optionally drag `SM64LuaRedux/src/SM64Lua.lua` onto the window.
4. Play a movie from `tas/` (match **USA vs Japan** to the file).

**STROOP** (Windows): extract is under `tools/STROOP/` — run `STROOP.exe`, attach to Mupen, watch Mario/objects/triangles.

**RTA note:** Mupen64-rr is for **TAS**, not automatically valid for **speedrun.com RTA**. See [notes/emulators-and-tools.md](notes/emulators-and-tools.md).

### 3. Study existing TASes

| Goal | Start here |
|------|------------|
| Fastest full-game glitchfest | `tas/full-game/1-key/` + [Bismuth notes](notes/bismuth.md) |
| Full completion optimization | `tas/full-game/120-stars/` + archive ILs |
| “Fair” multi-star tech | `tas/full-game/70-stars-no-blj/` |
| Per-star WR files | `tas/archive/SM64TASArchive/Individual Levels/` |
| Engine / ABC theory | [pannenkoek2012 notes](notes/pannenkoek2012.md) |

Full table: [notes/tas-catalog.md](notes/tas-catalog.md).

---

## What was installed / downloaded

| Component | Source | Local path |
|-----------|--------|------------|
| **Mupen64 stable repack** | [mupen64/repack-stable](https://github.com/mupen64/repack-stable) | `tools/mupen64/` |
| **SM64 Lua Redux + sm64-viz** | Bundled in repack | `.../stable/SM64LuaRedux`, `sm64-viz` |
| **STROOP (vDev)** | [SM64-TAS-ABC/STROOP](https://github.com/SM64-TAS-ABC/STROOP) | `tools/STROOP/` |
| **TASVideos movies** | [tasvideos.org/246G](https://tasvideos.org/246G) | `tas/full-game/` |
| **SM64 TAS Archive** | [TimeTravelPenguin/SM64TASArchive](https://github.com/TimeTravelPenguin/SM64TASArchive) | `tas/archive/SM64TASArchive/` |

Optional on macOS for casual N64 play (not TAS movies): `brew install --cask ares-emulator` (opens as **ares.app**).

---

## Learning path (recommended)

1. **Mechanics** — Read [notes/pannenkoek2012.md](notes/pannenkoek2012.md): speed caps, quarter steps, BLJ types, PUs.
2. **Route literacy** — Read [notes/bismuth.md](notes/bismuth.md); watch the any% / 1-key explainer and a 120-star episode.
3. **Tooling** — Frame-advance a castle grounds segment in Mupen; attach STROOP; watch horizontal speed and action.
4. **Imitation** — Playback 1-key `.m64`; re-create a single room (e.g. lobby BLJ) as your own movie.
5. **Improvement** — Pick an IL from the archive older than current community WR; try a 1-frame save.

Community hubs: [Ukikipedia](https://ukikipedia.net), [SM64 TASing & ABC Discord](https://discord.gg/ECskvyF), [Mupen64 Discord](https://discord.gg/hFANcme32k), [TASVideos SM64](https://tasvideos.org/246G).

---

## Ideas for improvements and fixes

### A. Tooling / repo engineering

| Idea | Why it matters | Difficulty |
|------|----------------|------------|
| **`.m64` metadata indexer** | Parse headers (ROM name, rerecord count, authors) into `tas/INDEX.md` or JSON | Easy |
| **MupenSharp or Python m64 parser** | Diff two movies frame-by-frame; find first input divergence | Medium |
| **Automated download CI** | GitHub Action re-pulls TASVideos + archive on schedule | Easy |
| **Git LFS or submodule for archive** | Keep repo clone small; large savestates out of main history | Easy |
| **Wine/Whisky launch scripts** | One-command `./tools/scripts/run_mupen.sh` on macOS | Medium |
| **Dockerized Windows TAS stack** | Reproducible Mupen+STROOP for collaborators | Hard |
| **ROM hash gate** | Script refuses to start unless MD5 matches USA/J expected | Easy |
| **BizHawk optional download** | Playback `.bk2` without manual hunt | Easy |

### B. TAS improvement research (game / movies)

| Idea | Angle |
|------|--------|
| **Segment re-sync of 1-key on latest Mupen** | Emulator revisions change lag; re-verify movie, document desync frames |
| **120-star IL → full-game merge audit** | Compare archive IL WRs to full-game 120 segments; list stars still “soft” |
| **Lag-centric camera routes** | Revisit castle and RR with modern lag understanding (object unload / camera modes) |
| **Pause-BLJ vs non-pause trade studies** | Script measure: time saved vs menu overhead per location |
| **J vs U textbox / lag maps** | Spreadsheet of stage entry costs; decide optimal region per category |
| **BitFS / BitDW micro-improvements** | Still historically fertile for frame saves in low% |
| **No-BLJ 70 star modernization** | Apply post-2012 movement tech that isn’t BLJ |
| **All-trees / joke categories** | Low competition → easy publications, good practice |
| **Console verification pipeline** | For any new movie aiming at TASVideos stars: dump → EverDrive / approved cart setup |

### C. Technique R&D (pannenkoek / ABC adjacent)

| Idea | Notes |
|------|--------|
| **0 A-press star ports to full ABC** | Track Ukikipedia ABC status; reproduce in Mupen with STROOP logs |
| **PU lattice calculator** | Given position + speed, predict PU index and landing cell |
| **Scuttlebug / HOLP lab maps** | Savestate library per clone setup for common stars |
| **Hyperspeed float edge cases** | Document when speed hits Inf / NaN and recovery |
| **Quarter-step visualizer** | Lua: draw 4 substep positions per frame (SM64 Lua Redux extension) |

### D. Documentation / education fixes

| Idea | Notes |
|------|--------|
| **Timestamped breakdown of 1-key `.m64`** | Mirror Bismuth chapters with frame numbers |
| **Glossary** | BLJ, HSW, PU, QPU, HOLP, VSC, dust frames, nisflip, … |
| **“First TAS” tutorial branch** | Minimal BoB star with commented inputs |
| **Desync troubleshooting guide** | Plugin, counter factor, ROM hash, savestate version |
| **Credit / license PASS** | Ensure redistributed movies follow TASVideos + archive rules |

### E. Known pitfalls to “fix” in your workflow

1. **Wrong region ROM** → instant desync. Always match movie (J vs U).
2. **Wrong plugin / RSP / graphics** → lag desync on long movies.
3. **Confusing RTA rules with TAS tools** → Mupen-rr is not an RTA free pass.
4. **Editing movies without rerecord discipline** → keep WIP folders and changelogs.
5. **Ignoring lag** — a faster-looking segment can lose frames to camera/objects.
6. **Dust frames on dive recoveries** — free frames if you press A/B one frame late.
7. **Nested git in archive** — re-download script strips `.git` so this repo stays one project; contribute upstream separately.

### F. Stretch goals

- Train a **search bot** (similar in spirit to past SM64 bots) for short IL segments with a clear reward (star grab frame).
- Rebuild **sm64-port** or decomp-based tools for deterministic experiments (note: different from N64 Mupen movies; not drop-in for TASVideos N64).
- Publish a **TAScomp** entry using this tree’s hygiene (ROM hash, script versions, input comments).

---

## Contributing back upstream

Improvements to shared resources belong in their homes:

- New / better IL or full-game `.m64` → [SM64TASArchive](https://github.com/TimeTravelPenguin/SM64TASArchive) or TASVideos submission
- STROOP features/bugs → [STROOP issues](https://github.com/SM64-TAS-ABC/STROOP)
- Mupen TAS features → [mupen64-rr-lua](https://github.com/mupen64/mupen64-rr-lua) / Mupen Discord
- Wiki facts → [Ukikipedia](https://ukikipedia.net)

---

## Credits

- **Mupen64** developers and repack maintainers  
- **STROOP** — SM64-TAS-ABC  
- **TASVideos** publishers and SM64 TAS authors (mkdasher, snark, sonicpacker, SilentSlayers, ToT, Tyler_Kehne, Superdavo0001, IsaacA, and many more)  
- **TimeTravelPenguin** — SM64 TAS Archive  
- **pannenkoek2012** — engine education & ABC  
- **Bismuth** — accessible WR / TAS explainers  
- **Ukikipedia** contributors  

This workshop is an independent study repo, not affiliated with Nintendo.

---

## License

- **Your notes and scripts** in this repo: use freely unless marked otherwise.  
- **Third-party tools and movies**: retain their original licenses and attribution requirements. Do not redistribute ROMs.
