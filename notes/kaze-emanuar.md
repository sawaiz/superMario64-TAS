# Notes: Kaze Emanuar — SM64 engine & performance analysis

**Who:** ROM hacker and engineer best known for rebuilding Super Mario 64’s engine for **complex custom levels on real N64 hardware**, often targeting **60 FPS** and dense geometry that vanilla SM64 cannot sustain.

**Links**
- YouTube: [Kaze Emanuar](https://www.youtube.com/@KazeEmanuar)
- GitHub: [github.com/KazeEmanuar](https://github.com/KazeEmanuar)
- Twitter/X: [@KazeEmanuar](https://twitter.com/KazeEmanuar)
- Related base for modern hacks: [HackerN64/HackerSM64](https://github.com/HackerN64/HackerSM64) (Kaze also maintains a fork)

This workshop mirrors select repos under `decomp/kaze/` for offline study.

---

## Why Kaze matters for decomp + TAS work

Vanilla **n64decomp/sm64** is a *matching* decompilation: it rebuilds bit-identical (or near-identical) retail ROMs. That is ideal for **understanding original behavior** and for TAS-adjacent research that must match console/emulator timing.

Kaze’s work is often the opposite goal: **non-matching, aggressive engine rewrites** so that *new content* (romhacks) can run on original silicon. For this repo:

| Goal | Prefer |
|------|--------|
| Match retail / TAS desync research | `decomp/sm64` (n64decomp) |
| Understand bottlenecks / write denser levels | Kaze videos + `HackerSM64` + optimization demos |
| Validate TAS movies | Mupen64-rr + retail or rebuilt matching ROM |

---

## Major themes from Kaze’s analysis

### 1. “FIXING the ENTIRE SM64 Source Code” (performance pass)
Famous early decomp-era video (~2022): walking through **CPU/RDP bottlenecks** once C source is available.

Takeaways commonly cited in r/emulation and N64 hacker circles:
- Original IDO/compiler-era code has **redundant work**, poor cache locality, and “correct but expensive” patterns.
- Large gains come from **not doing work** (culling, sharing matrices, cheaper math) rather than micro-optimizing single lines.
- Custom engines can run **several times faster** than vanilla on the same hardware for heavy levels.

### 2. Sine / trig and matrix math
Videos: *Finding the BEST sine function for Nintendo 64*, trig segments in later optimization talks.

- Vanilla SM64 uses **lookup tables** for sin/cos (typical for the era).
- Polynomial approximations can be **faster and/or more accurate** depending on N64 FPU/integer tradeoffs; Kaze measures **microsecond-scale** differences that matter when called thousands of times per frame.
- **Billboard matrices** and camera-related transforms: computing the same matrix per instance is wasteful; once-per-camera sharing saves **milliseconds** of CPU and can reduce RDP pressure indirectly.

### 3. Optimization paradox — “optimizations made Mario 64 slower”
Video: [How Optimizations made Mario 64 SLOWER](https://www.youtube.com/watch?v=Ca1hHC2EctY)  
Companion repo: [SM64-but-some-optimizations-are-removed](https://github.com/KazeEmanuar/SM64-but-some-optimizations-are-removed) → `decomp/kaze/SM64-but-some-optimizations-are-removed`

**Core idea:** Some “smart” original choices (or modern-looking optimizations) **hurt** because of **cache misses**, instruction mix, or RDP/CPU imbalance—not raw arithmetic count. On N64, **memory hierarchy** dominates. Removing certain optimizations can make the game *faster* in measured demos.

Implication for researchers: always **profile on target hardware** (or cycle-accurate tools); never trust “fewer ops ⇒ faster.”

### 4. Collision pipeline pain
Kaze + community (Ukikipedia, decomp Discord) repeatedly highlight:
- Floor/wall/ceiling checks are **hot paths** every quarter-step for Mario and many objects.
- Vanilla spatial partitioning and triangle tests scale poorly with **dense custom geometry**.
- Engine rewrites introduce better partitioning, early outs, and data layouts that keep collision **cache-friendly**.

This intersects TAS knowledge: **quarter steps**, surface types, and PU short-casts live in these systems—see also [pannenkoek2012 notes](pannenkoek2012.md).

### 5. Rendering: RDP budget, objects, occlusion
- Exclamation boxes and simple objects can be **orders of magnitude** more expensive than they look (duplicate geometry, bad display lists, memory layout) — e.g. *The Most Wasteful Object in Mario 64*.
- **Occlusion / plane culling** systems skip draw work for geometry fully covered in screen space (recent Kaze demos covered on 80.lv).
- Shader/combiner analysis: understanding Fast3D modes avoids accidental overdraw and unnecessary pipeline flushes.

### 6. Audio engine respect
Kaze has argued SM64’s **sound system is more sophisticated** than many assume (“use the SM64 audio format” style messaging). For romhacks: prefer existing audio infrastructure carefully rather than naive replacements that thrash the RSP.

### 7. 60 FPS and “better engine”
Through cumulative work (matrix sharing, collision, culling, object systems), Kaze’s engines target **stable high framerates** with content far beyond 1996 levels. That is **non-matching** by definition—great for hacks, not for replaying retail TAS movies without a separate matching build.

---

## GitHub map (KazeEmanuar)

| Repo | Role in this workshop |
|------|------------------------|
| [SM64-but-some-optimizations-are-removed](https://github.com/KazeEmanuar/SM64-but-some-optimizations-are-removed) | Demo that removing some opts improves speed — study diffs vs vanilla |
| [HackerSM64](https://github.com/KazeEmanuar/HackerSM64) | Fork of romhack-oriented decomp base |
| [sm64](https://github.com/KazeEmanuar/sm64) | Personal decomp fork |
| [splitscreen-multiplayer](https://github.com/KazeEmanuar/splitscreen-multiplayer) | Engine feature experiment |
| [Peachfury](https://github.com/KazeEmanuar/Peachfury), [Chaos3](https://github.com/KazeEmanuar/Chaos3) | Full hack projects built on optimized engines |

Upstream romhack base used by much of the community: **HackerN64/HackerSM64** (cloned at `decomp/HackerSM64`).

---

## Forum / community consensus (condensed)

From Reddit (r/emulation, r/SM64), NeoGAF threads, HN, Software Engineering Daily interview:

1. **Decomp unlocked real engineering** — without matching C, these rewrites were impractical.
2. **N64 is bandwidth/cache limited** — triangle counts alone mislead; cache miss cost explains “paradox” results.
3. **Original compiler + schedule constraints** explain many oddities; not pure “bad code,” but also not sacred.
4. **Separate “match retail” from “make it fast”** — TAS / console verification need the former; romhacks need the latter.
5. **HackerSM64** is the practical starting point for new levels; raw n64decomp is the reference for original logic.

---

## How to use this with *our* decomp tree

```text
decomp/sm64/          # n64decomp matching US build (baserom.us.z64)
decomp/HackerSM64/    # modern romhack base (optional experiments)
decomp/kaze/          # Kaze demos & forks for reading diffs
```

**Suggested study loop**
1. Build matching `sm64.us.z64` from `decomp/sm64` (`gmake VERSION=us -j$(nproc)`).
2. Open hot files under `src/engine/` (math, surface collision) and `src/game/` (Mario, objects, rendering hooks).
3. Watch a Kaze video on that subsystem; note claimed bottlenecks.
4. Diff against `decomp/kaze/SM64-but-some-optimizations-are-removed` or HackerSM64 equivalents where available.
5. **Validate** behavior in Mupen (Whisky) for TAS; use real hardware / ares for hack FPS claims.

---

## TAS-relevant cautions

- Optimized non-matching engines **change lag and sometimes logic** → **desync** with retail `.m64` movies.
- Always mark builds: `MATCHING` vs `KAZE_ENGINE` / `HACKERSM64`.
- For TASVideos / TAScomp, stick to **community-standard Mupen + retail (or verified matching) ROM**.

---

## Key video index (starting set)

| Topic | Video |
|-------|--------|
| Whole-engine performance pass | [FIXING the ENTIRE SM64 Source Code](https://www.youtube.com/watch?v=t_rzYnXEQlE) |
| Trig / sine design | [Finding the BEST sine function for N64](https://www.youtube.com/watch?v=xFKFoGiGlXQ) |
| Cache / false optimizations | [How Optimizations made Mario 64 SLOWER](https://www.youtube.com/watch?v=Ca1hHC2EctY) |
| Wasteful objects | [The Most Wasteful Object in Mario 64](https://www.youtube.com/watch?v=nA_zZiiH9Jc) |
| Optimization playlist | [Super Mario 64 Optimization](https://www.youtube.com/playlist?list=PLYD47ETYbyuvrFAoKMcwQWWilqRwznoBz) |
| Interview | [Optimizing N64 Code with Kaze (SE Daily)](https://softwareengineeringdaily.com/2024/04/05/bonus-episode-optimizing-nintendo-64-code-kaze-emanuar/) |

---

## Ideas this analysis suggests for our workshop

1. Annotate `src/engine/math_util.c` / surface collision with Kaze bottleneck notes.
2. Benchmark matching vs HackerSM64 object spam scenes in Mupen (frame time, not just FPS OSD).
3. Script: extract function sizes / call frequency for collision vs graphics (static analysis first).
4. Keep a “must not change for TAS” allowlist of files (Mario physics, RNG, lag-critical paths).
5. Port only *documentation* of insights into notes—not silent engine changes—unless building a separate `experiments/` branch.
