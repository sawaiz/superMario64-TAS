# TASVideos SM64 priorities & improvement ideas

Source hub: [tasvideos.org/246G](https://tasvideos.org/246G)  
History: [SM64TASHistory](https://tasvideos.org/SM64TASHistory)  
Submission detail (1 Key): [7161S](https://tasvideos.org/7161S)

---

## Featured publications (what TASVideos currently highlights)

| Rank of “importance” | Goal | Pub | Time | Why it matters |
|----------------------|------|-----|------|----------------|
| **1 — flagship** | **1 Key** (any%) | [4490M](https://tasvideos.org/4490M) | **4:18.983** (BizHawk); m64 ≈ **4:16.4**; console ≈ **4:15.78** | Pure fastest completion; Star award; console-verified; defines modern SM64 TAS tech (PU moat door, OJ, squish cancel) |
| **2 — prestige** | **all 120 stars** | [2208M](https://tasvideos.org/2208M) | **1:20:41.517** (2012 pub) | “Play the whole game optimally”; community’s biggest collaborative project — **heavily outdated offline** (see below) |
| 3 | **70 stars, no BLJ** | [2062M](https://tasvideos.org/2062M) | **42:58.517** | Showcase of non-BLJ tech; still readable “game” |
| 4 | **16 stars** | [6943M](https://tasvideos.org/6943M) | **13:28.400** | Historical mid-tier category (MIPS only for 2nd key) |
| 5 | **all trees** | [7239M](https://tasvideos.org/7239M) | **08:25.183** | Alternate goal / community fun |

**Most important TAS to study first: 1 Key ([4490M](https://tasvideos.org/4490M)).**  
If you care about “what the community actually spent 14 years polishing,” **120 Stars** is a close second — and is mid-revolution in 2026.

Local files:
- `tas/full-game/1-key/` — published m64 + bk2  
- `tas/full-game/120-stars/` — published 1:20:41-era bk2  
- Archive full-game / ILs under `tas/archive/SM64TASArchive/`

---

## Why 1 Key is the #1 TASVideos movie

1. **Category endgame for “beat the game fast”** — history on the page: 70 → 16 → 1 star → 0 star / 2 keys → **1 key** after **Moat Door Skip** via parallel universes (Tyler Kehne et al.).
2. **Maximum glitch density** — almost no “normal” play; BLJ, PU, Overflow Jump, lag routing, console crash workarounds.
3. **Site prestige** — Star, N64/DS TAS of 2021, console playback encode, multi-author “all-stars” credit list.
4. **Technical bar** — optimized for **console lag**, not just emulator input frames ([7161S](https://tasvideos.org/7161S)).

Watch: [YouTube encode](https://www.youtube.com/watch?v=fXT7Wyt94Ek) · Explainers: Bismuth’s older any% video + notes in `notes/bismuth.md`.

### What the published 1 Key already improved (post–4:21.30)

From [7161S](https://tasvideos.org/7161S) (published improvement path):

| Save | Who / idea | Size |
|------|------------|------|
| BitFS castle approach | Plush | 2f |
| BitFS / BitS slidekick starts | Plush | 1f + 1f |
| BitFS movement | Superdavo0001 + dar gos | 1f |
| DDD + BitFS lag (Mario cam) | IsaacA | 3f net |
| Bowser fight cameras | Superdavo0001 | 5f |
| BitFS key land wait | IsaacA | 0.5 VI |
| **BitS squish-cancel route** | Tyler Kehne design → **Dabs** | **149f** |

Authors explicitly note: **not minimum input frames** — e.g. pause-to-change-camera costs ~5 input frames to save lag on console.

---

## 120 Stars: the other “most important” project

TASVideos still features the **2012** collaborative **1:20:41**. Community status in **2026**:

- New full TAS premiered at **SGDQ 2026**: **~1:14:04** (project lead/encode: Palix and many contributors).
- ≈ **6.5 minutes** faster than the published TASVideos movie.
- Bismuth’s star-by-star explainer series launched alongside it.

So: **for “what to improve,” 120 is the biggest open delta vs the published page**, but **competition is already extreme** — you improve individual stars / lag, not “the whole category from scratch,” unless joining that collab culture.

IL tracking (community): Google sheet often linked from speedrun.com SM64 TAS threads  
`https://docs.google.com/spreadsheets/d/12Sl41gqLUGzBU0p1nx7uNKOAP835NIoFXqda1j6oqag`

---

## Improvements worth exploring (ranked for *this* workshop)

### Tier A — High impact / still realistic micro-work

| Target | Why | How to attack |
|--------|-----|----------------|
| **1 Key lag re-audit (console-first)** | Authors already proved lag ≫ raw movement; Mupen ≠ console | Use rcombs-style lag notes; camera mode / object unload; compare VI count on hardware or accurate dumps |
| **BitS / BitFS cycle routing** | Platforms are cyclic; “faster” movement can **lose** to cycles (Plush’s notes) | Systematic cycle search; slidekick / grind variants; squish-cancel alternate setups |
| **Basement + post-moat door** | Less glamorous than PU; often soft | Frame-by-frame vs archive / newer WIPs; MIPS-less 1-key path is fixed but movement isn’t perfect forever |
| **Bowser throw / key land timings** | Half-frames already found once | RNG / angle / lag on key object |
| **Camera pause trade study** | Known 5f cost for lag savings | Find cameras that don’t need pause, or cheaper mode switches |

### Tier B — Category / publication gaps

| Target | Why |
|--------|-----|
| **Submit/update 120 to TASVideos** after 1:14 era stabilizes | Published page still 1:20:41 — huge publication delta |
| **70 stars no BLJ modernization** | 42:58 is old; modern non-BLJ movement, clips, lag |
| **16 stars re-opt** | User-file WIPs in ~14:xx range (verify quality); legacy but popular for learning |
| **Japan vs USA lag maps** | 1 Key uses **J** (no Peach intro; BitFS/BitS text); 120 often **U** — wrong region = free loss |

### Tier C — Research / long-shot (high reward if real)

| Idea | Notes |
|------|-------|
| **Faster 0-star VCUtM / moat door setup** | Core of 1 Key; was rewritten once already (near-lake BLJ). New BLJ spots or OJ routing could still exist |
| **New BitS height tech** | Squish cancel was 149f; any new height/speed conversion is huge |
| **PU crash-safe shortcuts on console** | Fixed cam + no-input return cost frames; cheaper safety = free time |
| **Overflow Jump / QPU route variants** | Still underused outside known segments |
| **ABC → any% tech transfer** | Squish cancel came from ABC research (bad_boot). Watch pannenkoek / Ukikipedia for transferable cancels |

### Tier D — Soft / educational (good first TAS goals)

- Single-room redos of **published 1 Key** segments (castle grounds BLJ, VCUtM elevator, BitFS OJ).
- **IL improvements** vs `tas/archive/SM64TASArchive/Individual Levels/` where archive time > current sheet WR.
- **All-trees** / joke goals — low competition, practice tooling.

### Be careful with user-file “records”

TASVideos User Files include a **“Newest 1 Key 2026”** WIP claiming **4:12.583** (15155 frames) — *not* a published movie. Treat as **unverified** until the SM64 TAS Discord / known authors endorse it (console lag, desync, truncated movies, region mistakes are common on user uploads).

---

## Practical priority for this repo

1. **Study** published **1 Key** m64 in Mupen + STROOP (`notes/bismuth.md`, submission 7161S).  
2. **Track** new **120** (1:14:04) vs old 1:20:41 — IL sheet + Bismuth series.  
3. **Pick one segment** with known lag or cycle sensitivity (BitS, BitFS, DDD) and aim for a **documented frame save**, not a full WR.  
4. Only then attempt full-movie reassembly / TASVideos submission hygiene (region, plugins, console verify).

---

## Quick reference links

- Game page: https://tasvideos.org/246G  
- 1 Key pub: https://tasvideos.org/4490M  
- 1 Key sub notes: https://tasvideos.org/7161S  
- 120 pub (old): https://tasvideos.org/2208M  
- Game resources: https://tasvideos.org/GameResources/N64/SuperMario64  
- User files: https://tasvideos.org/UserFiles/Game/246  
- Forum: https://tasvideos.org/Forum/Topics/1621  
