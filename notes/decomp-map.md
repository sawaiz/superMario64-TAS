# Decomp source map (n64decomp/sm64)

Companion to [kaze-emanuar.md](kaze-emanuar.md). Paths relative to `decomp/sm64/`.

## High-value directories

| Path | Contents |
|------|----------|
| `src/engine/math_util.c` | Sine/cosine tables, matrix helpers — Kaze trig talks map here |
| `src/engine/surface_collision.c` | Floor/wall/ceiling queries — quarter-steps, PUs (short cast) |
| `src/engine/surface_load.c` | Collision mesh load/partition |
| `src/engine/graph_node*.c` | Scene graph, billboards, geo processing |
| `src/game/mario*.c` | Mario actions, physics entry points |
| `src/game/object_list_processor.c` | Object update order / lag structure |
| `src/game/rendering_graph_node.c` | Draw traversal — RDP/CPU balance |
| `src/game/camera.c` | Camera modes (lag + PU crash workarounds historically) |
| `src/audio/` | Sound engine (Kaze: more sophisticated than assumed) |
| `actors/`, `levels/` | Behaviors, geo, display lists |
| `include/` | Shared headers, structs (MarioState, Object, …) |
| `enhancements/` | Example non-matching mods in vanilla tree |

## Matching rebuild checklist

1. `baserom.us.z64` MD5 = `20b854b239203baf6c961b850a4a51a2`
2. `make VERSION=us` (or Docker script) succeeds with `COMPARE=1`
3. Output SHA1 = `9bef1128717f958171a4afac3ed78ee2bb4e86ce`
4. Load in Mupen (Whisky); play a USA `.m64` from the archive

## Matching vs HackerSM64 vs Kaze engines

```text
n64decomp/sm64     → bit-identical retail research, TAS-safe baseline
HackerSM64         → romhack QoL, expanded features, not for retail TAS
Kaze optimized     → performance / 60 FPS content, non-matching
```

## External docs

- Upstream README: https://github.com/n64decomp/sm64
- HackerSM64 wiki: https://github.com/HackerN64/HackerSM64/wiki
- Ukikipedia (behavior-level knowledge): https://ukikipedia.net
- Official decomp Discord (from upstream README): https://discord.gg/DuYH3Fh
