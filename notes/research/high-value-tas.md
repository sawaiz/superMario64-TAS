# High-value TAS research (rules-safe + console-first)

**Constraints:**

1. Retail baserom only — optimize **inputs** / routing / lag via camera — never ship a modified engine.
2. **Must run on real N64** when finished — see [console-first.md](../console-first.md).
3. Prefer **console lag / VI time** over “looks faster in Mupen only.”

Rules: [rules-and-decomp.md](../rules-and-decomp.md).

Tools (from repo root):

```bash
cd tools/research
python3 pu_nav.py pos 40000 0 100
python3 pu_nav.py qpu-speeds --min -4 --max 4
python3 air_physics.py blj --start -20 --jumps 12
python3 air_physics.py longjump --speed -30
python3 wall_punch.py clock-table
```

## Completed experiment: WKW one-frame search

A code-only Mupen search tested 20 one-sample deletion and input-retiming
variants around the 6.10 s Wall Kicks Will Work movie. No candidate beat the
baseline star-completion VI; see
[wall-kicks-speedup-experiment.md](wall-kicks-speedup-experiment.md) for the
method, graphs, raw results, and reproduction commands.

---

## 1. Parallel Universes — exact lattice

### Decomp fact

`TerrainData` = `s16` (`include/types.h`).  
`find_floor` / `find_ceil` cast float position to `TerrainData` **before** cell partition.

```c
// surface_collision.c
//! (Parallel Universes) Because position is casted to an s16 ...
TerrainData x = (TerrainData) xPos;
```

| Constant | Value | Meaning |
|----------|------:|---------|
| PU size | **65536** | one s16 wrap |
| QPU size | **262144** | 4 PUs — common TAS speed step |
| LEVEL_BOUNDARY_MAX | **8192** | after cast, outside ⇒ no floor in partition |
| CELL_SIZE | **1024** | 16×16 cells in main map |

### Console crash (TRUNC) — hard fail

If float→int conversion is outside s32 range, **N64 invalid op** (Fedak / 1 Key notes). Emulators often wrap instead → path **works in Mupen, dies on console**.

**Mandatory:** fixed camera + R in PUs; stay within safe float magnitudes; prefer QPU-aligned speeds; treat `pu_nav.py` `INVALID_TRUNC` as **route rejected**.

### Research actions

1. For moat-door / OJ segments, only accept speeds with `|v| % 262144 == 0` (or document intentional phase).
2. Use `pu_nav.py pos` on STROOP-copied coordinates each experiment.
3. Map “real” door XY to s16-equivalent PU approach vectors.

---

## 2. BLJ / air speed — closed form

### Long jump entry (the BLJ bug)

```c
// mario.c ACT_LONG_JUMP
if ((m->forwardVel *= 1.5f) > 48.0f) {
    m->forwardVel = 48.0f;
}
```

- **Positive** speeds: 1.5× then hard cap **48**.
- **Negative** speeds: 1.5× with **no cap** → hyperspeed BLJ.

### Air update (per frame)

- Soft approach toward 0 by **0.35**.
- Stick: `+ 1.5 * (mag/32) * cos(dYaw)`.
- If `v > 32` (or **48** in long jump): `v -= 1`.
- If `v < -16`: `v += 2` (slow recovery).

Decomp marks **uncapped air speed** as intentional oversight.

### Quarter steps

`perform_air_step`: **4** substeps, each `vel/4`. Mid-frame floor/wall/ceil events explain sub-frame clips and “gwk” wall storage quirks (commented in `mario_step.c`).

### Research actions

1. `air_physics.py blj` for envelope; compare to real BLJ with land frames in Mupen.
2. Optimize **pause-BLJ** by counting game frames vs pause buffers (rules: still retail).
3. Air steer at hyperspeed: small dYaw costs — model with `air_physics.py air`.

---

## 3. Squish cancel class

See [tools/research/squish_scan.md](../../tools/research/squish_scan.md).

**INPUT_SQUISHED** only if **dynamic** floor/ceil and gap ∈ **[0, 150]**.  
BitS axle: dynamic geometry + steep normals + speed retain into idle/air → **149f** published.

### Research actions

1. STROOP log dynamic platforms in BitFS/BitS/RR with `|spd|>48`.
2. Hunt elevators under low dynamic or static ceilings.
3. Any new cancel that keeps `forwardVel` is Tier-A for 1 Key / low%.

---

## 4. Clock-punch / wall geometry

1 Key second floor: **1 frame** from fully understanding punch probe + wall priority.

- Punch probe **50** units ahead; connect within **5** of wall.
- `wall_punch.py clock-table` reproduces their θ → hSpeed window (`θ=-272` optimal).

### Research actions

1. Apply same method to **other castle corners** (WDW painting side, spiral, lobby).
2. Slide-kick / jump-kick wall tests may share probe geometry.
3. Document wall triangle priority where seams matter (quantum tunneling comment in `surface_collision.c`).

---

## 5. Lag (console-first, still input-only)

Legal: change **camera mode**, **facing**, **object activity** via movement — not C culling.

### Methodology

| Signal | How |
|--------|-----|
| Mupen VI / lag counters | Movie length vs input frames |
| STROOP object slots | Count active / high-poly near camera |
| Console TASbot / rcombs notes | 1 Key lag map precedent |

### Priority segments (from published 1 Key improvement list)

1. DDD camera (already −3f net once — re-audit with modern cams).
2. BitFS / BitS Bowser fights (mines, falling platforms).
3. Castle with many paintings/objects on screen.

### Research actions

1. Side-by-side two cams same movement; count lag frames.
2. Avoid pause-cam if a free cam mode matches lag save (known 5f pause cost).

---

## 6. Priority queue (execute in order)

| # | Project | Est. value | Effort |
|---|---------|------------|--------|
| 1 | Squish/dynamic-platform survey BitS/BitFS | High (multi-frame) | Medium |
| 2 | QPU speed sheet for moat / OJ | Medium (fewer desyncs) | Low — **tool done** |
| 3 | Lag cam matrix DDD/BitFS/BitS | High on console | Medium |
| 4 | Clock-punch class elsewhere in castle | 1–5f | Medium |
| 5 | BLJ pause efficiency (lake / stairs) | Low–mid | Low — **sim done** |
| 6 | Action-cancel catalog (Lua) | Speculative high | High |

---

## 7. Explicitly out of scope (rules)

- Recompiling decomp with faster collision / 60 FPS / Kaze opts as “SM64 TAS”
- Emulator-only PU crash avoidance that fails on console
- Cheats, nonstop, Usamune codes in a TASVideos Standard movie

---

## 8. Verification of tools (sanity)

```text
longjump -30 → -45          # 1.5× negative
blj from -20 ×8 → grows     # 1.5^n envelope
pos 40000 → s16 -25536      # classic overflow example
θ=-272 clock → possible YES # matches 1 Key table
```
