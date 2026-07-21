# Console-first requirement (hard rule)

**Acceptance criterion for this workshop:** any TAS movie we claim as “done” must be intended to **play back on a real Nintendo 64** (cart or flashcart for *verification only*), not merely sync in Mupen.

Emulators (Mupen, Whisky, ares) are **authoring and research tools**. The **target platform is console hardware**.

This matches:

- TASVideos: [gameplay must be accurate to hardware](https://tasvideos.org/MovieRules#GameplayMustBeAccurateToHardware)
- SM64 community practice (1 Key, 120): console verification, console lag, PU crash avoidance
- Published 1 Key notes ([7161S](https://tasvideos.org/7161S)): optimized for **console timing**, not minimum emulator input frames

---

## What “runs on console” means

| Layer | Requirement |
|-------|-------------|
| **ROM** | Unmodified retail dump (USA or Japan as required by the movie). Matching decomp rebuild OK only if **SHA-1 matches** retail. |
| **Inputs** | `.m64` / dump that a TASbot or verified replay path can feed to hardware |
| **Behavior** | No strats that **only** work because Mupen/BizHawk mishandles floats, lag, or TRUNC |
| **PUs** | Use **console-safe** precautions (below) or avoid unsafe PU motion |
| **Timing claim** | Prefer **console VIs / lag-inclusive** time when comparing 1 Key–class improvements |

Flashcarts (EverDrive, etc.) are for **replaying dumps / verification**, not for changing the game. SRC **N64 RTA** bans flashcarts for *human* leaderboards; TAS console-verify culture still uses them to prove movies.

---

## Non-negotiable constraints (from hardware + decomp)

### 1. Float → int TRUNC (PU crashes)

On console, converting out-of-range floats to integers can raise **Invalid Operation** and **hard crash**.  
Many emulators **silently wrap** instead.

**Rule for us:** never ship a route that depends on emu wrap. Treat `INVALID_TRUNC` from `pu_nav.py` as **forbidden**.

### 2. Camera must not leave the real map during PUs

1 Key / community standard:

- Switch R to **Fixed Camera**
- **Hold R** while in PU so camera stays in real map  
- Switching costs ~**6 frames** (pause) — budget it; do not skip for “faster on emu”

### 3. PU movement safety

- Hitting wall / ceiling / OOB in PU can crash console  
- Prefer **QPU-aligned** speeds (`|v| % 262144 == 0`) where the route allows  
- No-input return to real map may cost frames — keep that cost if it prevents crash

### 4. Lag differs from Mupen

Object load, camera, and RSP/RDP load → **extra lag frames on console** not always present in Mupen.

**Rule for us:**

- Author in Mupen, but **score improvements by console lag** when possible  
- Do not remove “slow” cams that only look worse if they save console lag  
- Do not add “pretty” cams that add console lag for free  
- Document known Mupen vs console lag deltas in segment notes

### 5. Matching vs optimized decomp

| Build | Console retail TAS? |
|-------|---------------------|
| Retail dump / **bit-matching** n64decomp | **Yes** |
| `COMPILER=gcc` non-matching | Research only — **not** the TAS target ROM |
| HackerSM64 / Kaze engine | **Different game** — not retail 1 Key / 120 |

If we rebuild from decomp for verification, **COMPARE must pass** (US SHA-1 `9bef1128717f958171a4afac3ed78ee2bb4e86ce`).

---

## Workflow (author → console)

```text
1. Retail ROM (hash verified)
2. TAS in Mupen64-rr (Whisky OK for editing)
3. Segment tests: STROOP + research scripts (PU/BLJ/squish)
4. Full movie sync from power-on on Mupen
5. Console-safety pass (checklist below)
6. Replay on hardware (TASbot / dump / community verify)
7. Only then: claim time / submit TASVideos
```

Mupen-only “WRs” are **WIP**, not finished products.

---

## Console-safety checklist (every full movie)

Copy into segment notes when locking a movie:

- [ ] ROM MD5 matches intended region (US / JP)
- [ ] Starts from power-on (no savestate-anchored full run)
- [ ] No GameShark / nonstop / modified ROM
- [ ] All PU segments: fixed cam + R held (or proven safe without)
- [ ] No known TRUNC-invalid float magnitudes on critical frames
- [ ] No wall/ceil/OOB while outside real map (unless proven safe)
- [ ] Lag-sensitive segments reviewed for **console** (not only Mupen VIs)
- [ ] Desync test: same plugins/settings documented for others to reproduce
- [ ] Prefer comparison to published console-oriented times (e.g. 1 Key ~4:15.78 console)

---

## Region choice under console-first

| Goal | Typical region | Why |
|------|----------------|-----|
| **1 Key / any% glitch** | **Japan** | Shorter intro; fewer Bowser texts when BitDW skipped |
| **120 / many ILs** | **USA** often | Archive + collab history; verify per movie |

Text length differences are **discounted** on TASVideos; **lag** differences are real on hardware — measure if switching region.

---

## How research tools serve console-first

| Tool | Console-first use |
|------|-------------------|
| `pu_nav.py` | Reject speeds/positions that risk TRUNC; plan QPU lattice |
| `air_physics.py` | Speed envelopes that exist on hardware (same C) |
| `wall_punch.py` | Geometry valid on cart |
| `squish_scan.md` | Dynamic surface cancels that exist on cart |
| Decomp (read-only) | Same code as cart when matching |

**Kaze / non-matching builds** stay in `decomp/kaze` as **education**, not as the playback target.

---

## Hardware / replay pointers

- Published console encodes: linked from TASVideos movie pages (e.g. 1 Key, 120)
- Community: SM64 TASing & ABC Discord; console verifiers (historical: rcombs, Kyman, TASbots)
- TASVideos: [Console verification](https://tasvideos.org/ConsoleVerification/Movies)

We do not require owning a TASbot to *author*, but we **do** require designs that **could** pass console verification without emu-only cheats.

---

## Rejected “optimizations” under this policy

- Faster because Mupen skipped lag that console has  
- PU path that crashes N64 but “works in Mupen”  
- Non-matching recompiled ROM for a “retail” category  
- Settings that unlock wrong framerate / region hacks  

---

## Bottom line

> **If it doesn’t survive a real N64, it isn’t done.**

Mupen is the workshop. The cartridge is the exam.
