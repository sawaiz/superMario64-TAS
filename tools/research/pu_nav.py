#!/usr/bin/env python3
"""Parallel-Universe navigator for retail SM64 TAS (rules-safe: analysis only).

Models the decomp cast used in find_floor / find_ceil:

    TerrainData x = (TerrainData) xPos;  // s16 via trunc + wrap

PU index on an axis: how many full 65536-unit wraps from origin.
QPU-aligned speed: integer multiples of 262144 units/frame keep lattice phase.

Usage:
  python3 pu_nav.py pos 40000 0 -100
  python3 pu_nav.py speed 262144
  python3 pu_nav.py route --from-x 0 --to-x 65536 --speed 262144
  python3 pu_nav.py qpu-speeds --min -20 --max 20
"""

from __future__ import annotations

import argparse
import math
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from constants import (
    LEVEL_BOUNDARY_MAX,
    PU_SIZE,
    QPU_SIZE,
    S16_MAX,
    S16_MIN,
)


def float_to_s16(x: float) -> int | str:
    """Approximate MIPS trunc.w.s then cast to s16.

    Values outside s32 range cause Invalid Operation on console (PU crash).
    """
    if math.isnan(x) or math.isinf(x):
        return "INVALID_TRUNC"
    if abs(x) >= 2**31:
        return "INVALID_TRUNC"
    i = int(math.trunc(x))
    i = ((i + 2**15) % 2**16) - 2**15
    return i


def pu_index(coord: float) -> int:
    """Which PU cell this float lives in (floor division by 65536)."""
    return math.floor(coord / PU_SIZE)


def collision_xz(x: float, z: float) -> tuple[int | str, int | str, bool]:
    """Return (s16_x, s16_z, in_level_boundary_check)."""
    sx, sz = float_to_s16(x), float_to_s16(z)
    if isinstance(sx, str) or isinstance(sz, str):
        return sx, sz, False
    in_bound = (
        -LEVEL_BOUNDARY_MAX < sx < LEVEL_BOUNDARY_MAX
        and -LEVEL_BOUNDARY_MAX < sz < LEVEL_BOUNDARY_MAX
    )
    return sx, sz, in_bound


def real_map_equivalent(x: float, z: float) -> tuple[float, float]:
    """Map float position to [0, PU_SIZE) phase (then shift to s16 view)."""
    sx, sz, _ = collision_xz(x, z)
    if isinstance(sx, str) or isinstance(sz, str):
        return float("nan"), float("nan")
    return float(sx), float(sz)


def frames_to_cover(distance: float, speed: float) -> float | None:
    if speed == 0:
        return None
    return abs(distance / speed)


def qpu_aligned_speeds(k_min: int, k_max: int) -> list[tuple[int, float]]:
    """Speeds that are k * QPU_SIZE (keep PU lattice phase each frame if alone)."""
    return [(k, float(k * QPU_SIZE)) for k in range(k_min, k_max + 1) if k != 0]


def cmd_pos(args: argparse.Namespace) -> None:
    x, y, z = args.x, args.y, args.z
    sx, sy, sz = float_to_s16(x), float_to_s16(y), float_to_s16(z)
    print(f"float pos:  ({x}, {y}, {z})")
    print(f"s16 cast:   ({sx}, {sy}, {sz})")
    print(f"PU index:   X={pu_index(x)}  Z={pu_index(z)}  (PU_SIZE={PU_SIZE})")
    print(f"QPU index:  X={math.floor(x / QPU_SIZE)}  Z={math.floor(z / QPU_SIZE)}")
    if isinstance(sx, str) or isinstance(sz, str):
        print("WARNING: float→int TRUNC invalid — console crash risk (classic PU crash).")
        return
    _, _, ok = collision_xz(x, z)
    print(f"after cast, |coord| < LEVEL_BOUNDARY_MAX ({LEVEL_BOUNDARY_MAX})?: {ok}")
    if not ok:
        print("  → floor/ceil lookup returns empty / lower limit (treat as OOB for partition).")
    print(f"collision-equivalent XZ phase (s16): ({sx}, {sz})")
    print(f"s16 range: [{S16_MIN}, {S16_MAX}]")


def cmd_speed(args: argparse.Namespace) -> None:
    v = args.v
    print(f"speed: {v}")
    print(f"  PU units/frame:  {v / PU_SIZE:.6f} PU/f")
    print(f"  QPU units/frame: {v / QPU_SIZE:.6f} QPU/f")
    rem_pu = abs(v) % PU_SIZE
    rem_qpu = abs(v) % QPU_SIZE
    print(f"  |v| mod PU:  {rem_pu}  (0 ⇒ same PU phase each frame on that axis)")
    print(f"  |v| mod QPU: {rem_qpu} (0 ⇒ QPU-aligned — common moat-door / OJ speeds)")
    if abs(v) >= 2**31:
        print("  WARNING: |speed| huge — position integration may hit INVALID_TRUNC.")


def cmd_route(args: argparse.Namespace) -> None:
    dx = args.to_x - args.from_x
    dz = args.to_z - args.from_z
    dist = math.hypot(dx, dz)
    print(f"delta: ({dx}, {dz})  horizontal dist={dist}")
    if args.speed is not None:
        n = frames_to_cover(dist, args.speed)
        print(f"at |speed|={args.speed}: ~{n} frames if always aligned with path")
    # Suggest nearest QPU speeds that cover dx in integer frames
    print("nearest QPU-aligned speeds that cross Δx in integer frames (sample k):")
    for k in range(-12, 13):
        if k == 0:
            continue
        sp = k * QPU_SIZE
        if dx == 0:
            continue
        frames = dx / sp
        if frames > 0 and abs(frames - round(frames)) < 1e-9 and 1 <= frames <= 600:
            print(f"  k={k:3d}  speed={sp:10.0f}  frames_for_dx={int(frames)}")


def cmd_qpu_speeds(args: argparse.Namespace) -> None:
    rows = qpu_aligned_speeds(args.min, args.max)
    print(f"{'k':>4}  {'speed':>12}  {'|PU/f|':>10}")
    for k, sp in rows:
        print(f"{k:4d}  {sp:12.0f}  {abs(sp) / PU_SIZE:10.1f}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("pos", help="cast a float position to collision s16 / PU index")
    sp.add_argument("x", type=float)
    sp.add_argument("y", type=float)
    sp.add_argument("z", type=float)
    sp.set_defaults(func=cmd_pos)

    ss = sub.add_parser("speed", help="analyze a horizontal speed for PU/QPU alignment")
    ss.add_argument("v", type=float)
    ss.set_defaults(func=cmd_speed)

    sr = sub.add_parser("route", help="rough frame estimate between XZ points")
    sr.add_argument("--from-x", type=float, default=0.0)
    sr.add_argument("--from-z", type=float, default=0.0)
    sr.add_argument("--to-x", type=float, required=True)
    sr.add_argument("--to-z", type=float, default=0.0)
    sr.add_argument("--speed", type=float, default=None)
    sr.set_defaults(func=cmd_route)

    sq = sub.add_parser("qpu-speeds", help="list k·QPU speeds")
    sq.add_argument("--min", type=int, default=-8)
    sq.add_argument("--max", type=int, default=8)
    sq.set_defaults(func=cmd_qpu_speeds)

    args = p.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
