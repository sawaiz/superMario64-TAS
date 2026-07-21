# TASVideos Movie Rules (SM64-relevant summary)

**Canonical page:** https://tasvideos.org/MovieRules  
**History:** https://tasvideos.org/MovieRules/History  
**Emulators:** https://tasvideos.org/EmulatorResources  
**Judges:** ask on forums / Discord if unsure  

Raw dump: `tasvideos-MovieRules-raw.txt` (downloaded snapshot).

This is a **working summary** for Super Mario 64 authors — not a substitute for the full page.

---

## Core principles

1. **Hardware-accurate gameplay** — no techniques that only work due to emulation bugs.
2. **Approved tools** — official release of an accepted emulator; perfect `[!]` ROM when possible.
3. **From power-on** — not from savestate (SaveRAM only with verification movie).
4. **Complete the goal** — full game for speed branches; meaningful endpoint.
5. **Optimized effort** — need not be perfect, must not be easily improvable by large amounts.
6. **Attribution** — no plagiarism; credit co-authors who provide input.

---

## Emulator / format (N64)

| Role | Tool | Format |
|------|------|--------|
| **Preferred site format** | BizHawk | `.bk2` |
| **Accepted (community standard for SM64)** | Mupen64-rr / mupen64-rr-lua | `.m64` |

From [EmulatorResources/Mupen](https://tasvideos.org/EmulatorResources/Mupen):

- Mupen was **disallowed (2017)**, **reallowed (2022)**.
- Use **mupen64-rr-lua ≥ 1.1.1** for AVI fixes; **do not use** versions **&lt; 1.0.5** (Queuecrush savestate RCE).
- Site: https://mupen64.com — repack with TAS plugins.
- Mupen has **known timing/graphics inaccuracies**; movies often converted to BizHawk for publication.

**SM64 practice:** author in **Mupen + US/JP good dump**, convert/sync for TASVideos when submitting if required.

---

## When TASing (must / must not)

### Must

- Start from **power-on** (or SaveRAM + verification movie).
- Use settings matching intended console (region, framerate).
- Match **console behavior** as closely as possible.
- Beat known records *accounting for emulation differences*.
- Sync fully before submit; document extra sync settings.

### Must not

- Use **Game Genie / Action Replay / RAM-ROM hacks** for Standard class.
- Use **emulation-only** glitches (slower console-accurate movie can obsolete them).
- Start from arbitrary **emulator savestate**.
- Level-select / incomplete movies for Standard speed goals.
- **Modify ROM or BIOS** (except rare judge-approved cases).
- Force wrong refresh (e.g. PAL game as NTSC) for speed.

### Regional versions

- Any region allowed if justified.
- **Text/cutscene length differences do not count** as improvements — only comparable gameplay.
- SM64 **1 Key** uses **Japan** for Peach intro / text advantages; pure gameplay still compared fairly.

---

## Goal branches relevant to SM64

| Goal | TASVideos class notes |
|------|------------------------|
| **Fastest completion (any%)** | Standard — SM64 “1 Key” lives here |
| **Full completion (120)** | Standard |
| **No major skips** | e.g. “70 stars, no BLJ” style |
| **Glitchless** | Community-defined; avoid ambiguous “feels like glitch” |
| **Playaround / alt** | Alternative class |
| **ROM hacks** | Allowed if public patch, not pure cosmetic; stricter quality bar |

Obsoletion for speed = **gameplay** improvement; version/emulation length deltas are discounted.

---

## Console verification (SM64 culture)

Not strictly required by Movie Rules, but **SM64 1 Key** and others are console-verified because:

- **Parallel Universes** can **crash real N64** (float→int invalid ops).
- Fixed camera + careful PU routing is used so the movie is **console-safe**.
- Community optimizes for **console lag**, not only Mupen input frames.

Rule takeaway: if it desyncs or crashes console, expect rejection pressure even if Mupen looks fine.

---

## Attribution & license

- Submissions under **CC BY 2.0**.
- Co-authorship: anyone providing direct input should be credited unless they decline.

---

## SM64 TAS Competition (community, not TASVideos)

Separate from TASVideos publications:

- Recurring **TAScomp** tasks (Mupen `.m64` + savestate, bot validation).
- Discord-hosted; **task-specific rules** (allowed stars, BLJ yes/no, start state, etc.).
- Ukikipedia: [List of TAS Competition tasks](https://ukikipedia.net/wiki/List_of_TAS_Competition_tasks)
- Many modern “rules” (joke ban, savestate requirements) evolved from past comps (e.g. pannenkoek joke entries).

**Always read the current task post** — general TASVideos rules still apply if you later submit to the site, but comps add constraints.

---

## Checklist before TASVideos SM64 submit

- [ ] Good dump (`[!]`), region documented (J vs U hashes).
- [ ] Mupen ≥ 1.1.1 / accepted BizHawk core; version stated.
- [ ] Movie from power-on; full sync.
- [ ] No cheats / ROM edits.
- [ ] Console-known PU crash workarounds if using PUs.
- [ ] Beats published goal on **gameplay** (not only shorter text).
- [ ] Authors credited; notes explain improvements.
- [ ] Prefer console lag notes if claiming 1 Key improvements.
