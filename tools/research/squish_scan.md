# Squish / cancel research (retail, rules-safe)

Decomp sources: `mario.c` (INPUT_SQUISHED), `mario_actions_cutscene.c` (`act_squished`).

## When is INPUT_SQUISHED set?

Every Mario update, if floor exists:

```c
if ((floor dynamic) || (ceil dynamic)) {
    ceilToFloorDist = ceilHeight - floorHeight;
    if (0.0f <= ceilToFloorDist && ceilToFloorDist <= 150.0f)
        m->input |= INPUT_SQUISHED;
}
```

Requirements:

1. **Dynamic** floor and/or ceiling (moving platform / object surface — `SURFACE_FLAG_DYNAMIC`).
2. Gap between floor and ceiling **∈ [0, 150]**.

Static tight corridors alone do **not** set INPUT_SQUISHED.

## What does ACT_SQUISHED do that TASers care about?

| State | Behavior |
|-------|----------|
| 0 | If space > 160 → **immediate ACT_IDLE**, `squishTimer=0` (soft cancel path) |
| 0 | Else pancake scale; if space < 10.1 → damage, state 1 |
| 1→2 | Wait for space ≥ 30, then un-squish timer → ACT_IDLE |
| **Steep floor/ceil** | Sets `vel[0]/vel[2]` to **10** along surface normal; ground step; if leaves ground → **instant un-squish → ACT_IDLE** |

### Speed preservation angle

`set_mario_action(…, ACT_IDLE, 0)` does **not** zero `forwardVel` by itself in the general path (idle entry doesn’t hard-reset H speed the way some jumps do). Combined with:

- entering squish while holding **large |forwardVel|** (e.g. from BLJ),
- **steep dynamic** geometry pushing / releasing,

you get the **squish cancel** class used for **BitS (−149f in 1 Key)**.

## TAS-legal search checklist (Mupen + STROOP)

For each candidate platform (rotators, elevators, cages):

1. Surface has **dynamic** flag while Mario is in the gap.
2. `ceilHeight - floorHeight` can be driven into **(0, 150]** for at least one frame.
3. Optionally **steep** normals (`floor.ny < 0.5` or `ceil.ny > -0.5`) for 10-unit push + leave-ground cancel.
4. On exit to idle/air, log **forwardVel** — did it survive?
5. Can you convert **negative** speed → useful **positive** displacement (BitS axle pattern)?

### Known money spots

| Area | Why |
|------|-----|
| **BitS rotating axle** | Proven 149f (1 Key) — bugged hitbox rotation |
| Other **rotating platforms** BitFS/BitS | Same dynamic gap class |
| **Elevators** with low ceilings | Dynamic floor + tight ceil |
| Object platforms under static ceilings | Dynamic floor only |

### Not worth (usually)

- Static geometry only (no INPUT_SQUISHED).
- Gaps always > 150.
- Squish that only deals damage without speed utility.

## Related cancels to catalog next

From decomp action switches (search pattern: set action while `forwardVel` untouched):

| Candidate | File / trigger | Research question |
|-----------|----------------|-------------------|
| Squish → idle (space > 160) | `act_squished` state 0 | Keep H speed? |
| Squish steep leave-ground | `act_squished` | Airborne with old speed? |
| Slide kick grind | moving actions | BitFS/BitS 1f saves already |
| Water exit Z restore | submerged | Classic TAS speed store |
| Bonk / soft bonk | interaction | Direction flip without full wipe? |
| Landing action cancel (first-frame A/B) | dust frames | Known dust-frame skip |

## Automation idea (still rules-safe)

Lua/STROOP: each frame log

```
action, forwardVel, floorDyn, ceilDyn, gap, floorNy, ceilNy, pos
```

Flag frames where `INPUT_SQUISHED` would be set and `|forwardVel| > 48`. Build a heatmap per course — pure research, retail ROM.
