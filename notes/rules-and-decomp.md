# Official rules + decomp-informed TAS optimizations

See also: [console-first.md](console-first.md) (**real N64 is the finish line**), [rules/](rules/), [kaze-emanuar.md](kaze-emanuar.md), [tasvideos-priorities.md](tasvideos-priorities.md).

---

## 0. Project acceptance (before any rule sheet)

This workshop optimizes under one acceptance test:

> **The movie must be designed to complete on a real Nintendo 64 with a retail ROM.**

Mupen is for TASing. Console is for truth. Details and checklist: [console-first.md](console-first.md).

---

## 1. Which “official rules” apply?

| Context | Authority | What you’re allowed to do |
|---------|-----------|---------------------------|
| **TASVideos publication** | [MovieRules](https://tasvideos.org/MovieRules) + [EmulatorResources](https://tasvideos.org/EmulatorResources) | Tool-assist on matching retail ROM; hardware-accurate glitches OK; **no** modified engine |
| **SM64 TAScomp** | Task post + Discord bot | Per-task constraints on Mupen `.m64` |
| **speedrun.com RTA** | SRC categories + Platform variables | Human play; **no TAS tools**; restricted emulators |

These are **different sports**. Decomp engine rewrites (HackerSM64 / Kaze 60 FPS) are for **romhacks**, not Standard SM64 TAS or vanilla SRC.

---

## 2. TASVideos (tool-assisted) — essentials

Full summary: [rules/tasvideos-MovieRules.md](rules/tasvideos-MovieRules.md).

- **ROM:** perfect dump; SM64 US MD5 `20b854b239203baf6c961b850a4a51a2`, JP `85d61f5525af708c9f1e84dce6dc10e9`.
- **Emulator:** BizHawk preferred for site; **Mupen64-rr-lua** accepted for N64 (SM64 community standard). Mupen **≥ 1.1.1**; never &lt; 1.0.5.
- **No** Action Replay / Game Genie for Standard.
- **No** emulation-only glitches; console-accurate behavior preferred.
- **Timing:** power-on → last necessary input.
- **Region text** doesn’t count as “improvement.”
- SM64 **1 Key** is Standard “fastest completion”; **120** is full completion.

---

## 3. speedrun.com Super Mario 64 (RTA) — archived

API game id: `o1y9wo6q`.  
Files: `rules/speedrun-com-categories.txt`, `rules/speedrun-com-variables.txt`.

### Main full-game categories

| Category | Restrictions (gameplay) |
|----------|-------------------------|
| **120 Star** | None |
| **70 Star** | **All BLJ banned**; **MIPS clip banned**; other door/star circumventions banned |
| **16 Star** | **Side BLJ banned**; 30-star door only via **MIPS clip** |
| **1 Star** | **DDD skip banned** |
| **0 Star** | Cannot collect any stars |

### Platform (variable)

| Platform | Emulators / hardware |
|----------|----------------------|
| **N64** | Official carts only; Everdrive/flash **banned**; no repro/mod carts |
| **VC** | Official Wii / Wii U / Switch NSO only; no injects |
| **EMU** | **Only:** Project64 **1.6.x**, Rosalie's Mupen GUI **0.5.x+**, OpenEmu **2.x+** (Mac). All others **banned** |

**EMU required settings (common rejects):**

- **Counter Factor = 1** (not default 2) — removes emulated lag (PJ64 / RMG).
- **Limit FPS** on.
- Default save type unchanged.
- Timing: power-on/reset → big star dust; logo at **1.33s** for retiming.

**Critical:** **Mupen64-rr (TAS) is NOT an allowed RTA EMU.** Parallel Launcher / random mupen64plus builds are not on the allowlist unless they match the listed products.

---

## 4. Can decomp optimizations help a TAS?

### Short answer

| Approach | Valid for TASVideos Standard SM64? | Valid for SRC vanilla? | Helps TAS? |
|----------|--------------------------------------|-------------------------|------------|
| **Read decomp** to understand physics/collision/lag | **Yes** | N/A (human) | **Yes — primary use** |
| **STROOP / Lua** reading same RAM as decomp structs | **Yes** | No (TAS tools) | **Yes** |
| **Change C and rebuild ROM** (faster collision, 60 FPS, Kaze opts) | **No** (different game / ROM hack) | **No** | Only for hacks |
| **NON_MATCHING / HackerSM64 features** | Only as ROM-hack goal | Separate boards | — |

**Kaze-style engine rewrites save FPS for dense levels; they do not produce a valid 1 Key / 120 TAS of retail SM64.**

### What decomp *does* unlock for legal TAS improvement

Using `decomp/sm64` as a **spec**:

#### A. Parallel Universes (documented in source)

`src/engine/surface_collision.c` — `find_floor` / `find_ceil`:

```c
//! (Parallel Universes) Because position is casted to an s16, reaching higher
//  float locations can return floors despite them not existing there.
TerrainData x = (TerrainData) xPos;  // effectively s16 cast
```

- Float position wraps into **16-bit** collision space → PU grid.
- Explains exact lattice: \(2^{16}\) unit cells, QPU \(2^{18}\).
- **TAS use:** compute valid QPU speeds / landing cells without trial-and-error; document console crash (TRUNC on huge floats) → fixed cam rules.

#### B. Uncapped air speed / BLJ physics

`src/game/mario_actions_airborne.c` — `update_air_*`:

```c
//! Uncapped air speed. Net positive when moving forward.
if (m->forwardVel > dragThreshold) {  // 48 long jump, 32 else
    m->forwardVel -= 1.0f;
}
if (m->forwardVel < -16.0f) {
    m->forwardVel += 2.0f;  // weak recovery from deep negative
}
// + 1.5 * intendedMag * cos(dYaw) acceleration while airborne
```

- **Negative** hyperspeed decays slowly; **positive** past drag threshold only loses 1/frame.
- Long jump drag threshold **48** vs normal **32**.
- **TAS use:** exact BLJ / air accel models; when to hold vs release stick; pause-BLJ frame math.

#### C. Quarter-steps & wall priority

Collision + movement use multi-step updates (documented extensively in TASVideos Game Resources and 1 Key submission clock-punch math). Decomp makes **wall test order** and **50-unit punch probes** explicit — same class of insight that saved the **clock punch** frame on the 2nd floor.

#### D. Lag as object/camera work

Object list processing + camera graph determine **RDP/CPU load** → lag frames.

- Decomp + STROOP: which objects/slots/modes cost lag.
- **TASVideos-legal optimization:** change **inputs/camera** (as 1 Key did), **not** the engine.
- Kaze’s “billboard matrix once per frame” is an **engine** fix — illegal for retail TAS, but tells you **why** camera angles lag.

#### E. Squish cancel / action cancels

Action state machine in `mario_actions_*.c` — conditions for squish, idle, speed retention.

- Squish cancel (149f BitS) was found via **engine research**, implementable on **retail** once conditions known.
- **TAS use:** search for other cancel combinations with decomp + TAS.

#### F. What decomp should **not** tempt you into

| Temptation | Why invalid for Standard TAS |
|------------|------------------------------|
| Cap negative speed / fix BLJ | Changes game; also ruins category |
| Faster `find_floor` spatial hash | Non-matching ROM |
| Remove lag by culling objects in C | Non-matching ROM |
| 60 FPS engine | Non-matching |
| Patch TRUNC crash for free PU | Console wouldn’t match; ROM mod |

---

## 5. Highest-value decomp → TAS research projects

Implemented starters live in `tools/research/` + `notes/research/high-value-tas.md`.

1. **Formal PU navigator** — `tools/research/pu_nav.py` (s16 cast, QPU speeds).
2. **Lag heatmaps** — methodology in research notes; instrument in Mupen/STROOP.
3. **Action cancel catalog** — squish conditions in `tools/research/squish_scan.md`.
4. **Clock-punch class geometry** — `tools/research/wall_punch.py`.
5. **Air/BLJ envelopes** — `tools/research/air_physics.py`.
6. **J vs U text/lag table** from decomp `text/` + measured lag — still open.

All of the above **keep the retail ROM** and stay inside TASVideos + community norms.
---

## 6. Quick decision tree

```
Want faster retail SM64 TAS movie?
  → Keep baserom.us/jp.z64 identical
  → Use Mupen TAS tools + STROOP
  → Read decomp for formulas
  → Change INPUTS only

Want denser levels / 60 FPS on N64?
  → HackerSM64 / Kaze engines
  → Separate hack leaderboards / TASVideos ROM-hack goals
  → Not interchangeable with 1 Key / 120 retail pubs
```

---

## 7. Links

- TASVideos Movie Rules: https://tasvideos.org/MovieRules  
- TASVideos Mupen: https://tasvideos.org/EmulatorResources/Mupen  
- SM64 game page: https://tasvideos.org/246G  
- SRC SM64: https://www.speedrun.com/sm64  
- n64decomp: https://github.com/n64decomp/sm64  
- Ukikipedia BLJ / PU / TAScomp lists  
