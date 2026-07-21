# Emulators & Tools for Super Mario 64 (TAS + RTA)

## Critical distinction: TAS vs RTA

| Mode | Goal | Emulator ecosystem |
|------|------|--------------------|
| **TAS** (tool-assisted) | Frame-perfect movies (`.m64` / `.bk2`), savestates, re-records | **Mupen64-rr-lua** (community standard for SM64) |
| **RTA** (real-time speedrun) | Human play, leaderboards on speedrun.com | Console or **approved** emulators only — **not** the same rules as TAS |

This repository is primarily a **TAS workshop**. RTA rules are noted so you do not submit TAS tools to RTA boards by mistake.

---

## Best emulator for SM64 TAS (community + TASVideos practice)

### Mupen64 (rerecording / Lua) — **primary choice**

- **Site:** https://mupen64.com/
- **Repack (this repo):** `tools/mupen64/repack-stable-main/stable/mupen64.exe`
- **Source:** https://github.com/mupen64/mupen64-rr-lua
- **Why it wins for SM64 TAS:**
  - Native **`.m64` movie** format used by SM64 TASers and TAScomp
  - Savestates, frame advance, rerecording, piano roll, seeking
  - **Lua API** + bundled **SM64 Lua Redux** and **sm64-viz**
  - Batteries-included plugin set tuned for TASing
- **Platform:** Windows native. On macOS: Wine / Whisky / Crossover / Windows VM / dual boot.
- **ROM folder:** `tools/mupen64/repack-stable-main/stable/roms/`

#### Quick start (Windows or Wine)
1. Run `mupen64.exe`.
2. Put legally dumped SM64 ROM in `roms/`.
3. Double-click ROM in list → TAS input window appears.
4. Optional: drag `SM64LuaRedux/src/SM64Lua.lua` onto the window.
5. Play movies: load matching region ROM, then open `.m64` playback.

#### Common shortcuts (stable docs)
| Key | Action |
|-----|--------|
| Ctrl+O | Load ROM |
| Ctrl+S | Settings |
| Ctrl+N | Lua instances |
| F1–F4 | Save state slots |
| Shift+F1–F4 | Load state slots |

Official getting started: https://mupen64.com/docs/mupen64/stable/1._Getting_Started

### BizHawk
- Used by **TASVideos** as a multi-system standard; SM64 publications often ship **`.bk2`** (converted from Mupen).
- This repo’s TASVideos downloads under `tas/full-game/**/*.bk2` are for BizHawk playback/comparison.
- SM64 **authoring** still usually happens in Mupen, then converts for submission when required.

### Not for SM64 TAS authoring
- **Mupen64Plus** (standalone) — different product; banned or discouraged in many RTA contexts and not the rr TAS toolchain.
- **Project64** — playable, not the SM64 TAS standard.

---

## RTA / speedrun.com (human runs) — valid emulation

Rules change; **always** read the current Super Mario 64 speedrun.com rules and emulator thread before submitting.

Historically / commonly:
- **Console** (N64 / VC / etc. per rules) is always the gold standard.
- **Parallel Launcher** (and related Accurate N64 setups) is a modern community front-end for approved cores (e.g. ParaLLEl-RDP related stacks) for *human* runs.
- Some older emulators (certain Project64 versions, etc.) appear in rule docs with version pins.
- **Mupen64Plus** has been discussed as **banned** for RTA on SM64 boards due to accuracy / timing concerns — do not assume “Mupen” (TAS) is valid for RTA.

**This repo does not install Parallel Launcher by default** (GUI app; install from its official site if you RTA). For casual Mac-native playback of the game (not TAS movies), **ares** is a multi-system option:

```bash
brew install --cask ares-emulator   # → /Applications/ares.app
```

Do **not** confuse with Homebrew formula `ares` (unrelated crypto tool).

---

## STROOP — runtime observer

- **Name:** SuperMario64 Technical Runtime Observer and Object Processor  
- **GitHub:** https://github.com/SM64-TAS-ABC/STROOP  
- **This repo:** `tools/STROOP/` (dev zip + extracted `net461/`)
- **Requires:** Windows + .NET Framework 4.6.1+; OpenGL for map tab
- **Connects to:** Mupen, BizHawk, Project64, Mupen64Plus, Nemu, etc.
- **Use for:** Mario struct, objects, triangles, map, hacks tab, cloning, watches — essential for research TASing and ABC.

---

## Other ecosystem tools

| Tool | Purpose |
|------|---------|
| **SM64 Lua Redux** | Overlay / input helpers inside Mupen (bundled in repack) |
| **sm64-viz** | Visualization helpers (bundled in repack) |
| **MupenSharp** | C# library to read/write `.m64` — https://github.com/TimeTravelPenguin/MupenSharp |
| **Ukikipedia** | Encyclopedic SM64 knowledge — https://ukikipedia.net |
| **SM64 TAS Archive** | Historical WR `.m64` library — vendored under `tas/archive/SM64TASArchive` |
| **TAScomp Discord** | SM64 TAS competitions — often linked from tutorial videos |

---

## ROM legality (read this)

This repository **does not** and **must not** include Super Mario 64 ROMs.

You must supply your own dump from a cartridge you own (or otherwise legally obtained image). Common community reference for **USA** big-endian `.z64`:

| Region | MD5 (commonly cited) |
|--------|----------------------|
| USA | `20b854b239203baf6c961b850a4a51a2` |
| Japan | `85d61f5525af708c9f1e84dce6dc10e9` |

Many any% / 1-key TASes use **Japan**; many 120 / IL archives use **USA**. Match the movie file’s region.

---

## macOS (Apple Silicon) notes

This machine is **arm64 macOS**. Mupen64-rr and STROOP are **Windows x86/x64** apps.

Recommended approaches (pick one):
1. **Whisky / Game Porting Toolkit / Crossover** — run `mupen64.exe` and `STROOP.exe`.
2. **Wine-stable** (Homebrew bottles where available) — variable GPU/plugin success.
3. **Windows 11 ARM VM** (Parallels / UTM) — most reliable for full TAS stack.
4. Dual-boot / separate Windows PC for serious TASing.

Scripts in `tools/scripts/` still download and extract the Windows tools so the tree is complete even if you run them elsewhere.
