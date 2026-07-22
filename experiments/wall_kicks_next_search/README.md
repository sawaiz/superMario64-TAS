# Wall Kicks Will Work: expanded automated search

## Result

The code-driven Mupen64 search tested 73 mutations from the same USA savestate.
Eight airborne stick variants reached `ACT_FALL_AFTER_STAR_GRAB` at sample 224 /
VI 538, one game update (two VIs) earlier than baseline sample 225 / VI 540.

The smallest selected winner is `air_full_x100_y-128`: change stick X from 98
to 100 for samples 149-201 while preserving every button input. Three additional
replays returned the same touch VI, exit VI, and parity hash
`69da52d0126e4da6`.

The result has a tradeoff. The baseline reaches grounded
`ACT_STAR_DANCE_EXIT` at sample 228 / VI 546, while all eight earlier-touch
variants reach it at sample 229 / VI 548. This is therefore a real IL star-touch
lead and a strong search seed, but not yet an end-to-end star-sequence save.

![Candidate timing and outcomes](results.png)

![Emulator telemetry snapshot](telemetry-snapshot.png)

The second image is generated from emulator telemetry because this Mupen video
plugin returned black BMPs through its screenshot API. It is deliberately
labelled as telemetry rather than presented as a gameplay capture.

## Candidate totals

| Search family | Tested | Earlier touch | Same touch VI | Missed star |
|---|---:|---:|---:|---:|
| Archived-route transplant | 6 | 0 | 0 | 6 |
| Textbox timing | 23 | 0 | 6 | 17 |
| Air control | 22 | 8 | 4 | 10 |
| Final approach | 22 | 0 | 16 | 6 |
| **Total** | **73** | **8** | **26** | **39** |

Earlier-touch air settings, applied across samples 149-201:

- `(96, -124)`
- `(98, -126)`, `(98, -124)`
- `(100, -128)`, `(100, -126)`, `(100, -124)`
- `(102, -126)`, `(102, -124)`

## What the archived movies taught us

The USA and Japan 5.53-second movies both replayed with valid parity against
their matching ROMs. Their absolute sample numbers differ because their movie
starts differ, but each takes exactly 124 input samples from first walking to
star touch. The local baseline also takes 124. A raw donor-input transplant is
therefore not a free movement save, and all six transplants missed due to small
position/yaw state differences.

## Most promising next tests

1. **Earlier touch plus earlier landing.** Sweep the pre-touch trajectory around
   X 96-102 and Y -128 to -120, scoring both touch and grounded exit. The goal is
   to preserve VI 538 while arriving lower or with a better vertical state.
2. **Two-phase air control.** Use the successful value only over the minimum
   window, then restore or counter-steer before contact. This directly targets
   the extra airborne update after the early touch.
3. **State-matched donor search.** Align archive inputs by Mario position, speed,
   and facing yaw rather than movie sample number before transplanting them.
4. **Robustness neighborhood.** Exhaust the integer stick grid adjacent to
   `(100, -128)` and replay winners multiple times before console testing.

Textbox and last-moment button shifts are lower priority: 45 tests across those
families produced no earlier touch and were often route-breaking.

## Reproduce

```powershell
python tools\research\wkw_next_search.py --stages route textbox air final
python tools\research\wkw_next_search.py --stages verify --verify-runs 3
python tools\research\plot_speedup_results.py
```

Candidate movies and savestates are generated locally and gitignored. The
committed [results.json](results.json) contains every timing and parity result.
