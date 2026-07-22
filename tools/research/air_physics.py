#!/usr/bin/env python3
"""Retail SM64 airborne forwardVel simulation (rules-safe research).

Implements the decomp formulas in update_air_without_turn / update_air_with_turn
and ACT_LONG_JUMP entry (BLJ multiplier). Does NOT model walls, slopes, or lag —
use for speed envelopes and BLJ growth estimates only.

Usage:
  python3 air_physics.py blj --start -20 --jumps 10
  python3 air_physics.py air --speed -100 --frames 30 --stick-mag 32 --dYaw-deg 180
  python3 air_physics.py longjump --speed -30
"""

from __future__ import annotations

import argparse
import math
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from constants import (
    AIR_ACCEL_FACTOR,
    AIR_APPROACH_ZERO,
    AIR_DRAG_THRESHOLD_LONG_JUMP,
    AIR_DRAG_THRESHOLD_NORMAL,
    AIR_NEG_SPEED_RECOVERY,
    AIR_NEG_SPEED_THRESHOLD,
    LONG_JUMP_POS_CAP,
    LONG_JUMP_SPEED_MULT,
)


def approach_f32(current: float, target: float, inc: float, dec: float) -> float:
    """sm64 approach_f32."""
    if current < target:
        return min(target, current + inc)
    if current > target:
        return max(target, current - dec)
    return current


def apply_long_jump_entry(forward_vel: float) -> float:
    """ACT_LONG_JUMP transition: forwardVel *= 1.5; cap only if result > 48."""
    v = forward_vel * LONG_JUMP_SPEED_MULT
    if v > LONG_JUMP_POS_CAP:
        v = LONG_JUMP_POS_CAP
    return v


def air_frame(
    forward_vel: float,
    *,
    long_jump: bool,
    stick_mag: float,
    d_yaw_deg: float,
    with_turn: bool = False,
) -> float:
    """One frame of air horizontal speed update (no wind).

    stick_mag: 0..32 (Mario intendedMag scale before /32 in decomp).
    d_yaw_deg: intendedYaw - faceAngle yaw in degrees (0 = straight).
    """
    drag_thr = AIR_DRAG_THRESHOLD_LONG_JUMP if long_jump else AIR_DRAG_THRESHOLD_NORMAL
    v = approach_f32(forward_vel, 0.0, AIR_APPROACH_ZERO, AIR_APPROACH_ZERO)

    intended_mag = stick_mag / 32.0
    d_yaw = math.radians(d_yaw_deg)
    # decomp: angle math uses s16 units; cos/sin of angle difference for accel
    # We use degrees for CLI convenience; cos(0)=1 full forward relative to face.
    cos_d = math.cos(d_yaw)

    if stick_mag != 0:
        v += AIR_ACCEL_FACTOR * cos_d * intended_mag
        if with_turn:
            pass  # face turn omitted; speed formula same for forward component

    # Uncapped air speed comments in decomp
    if v > drag_thr:
        v -= 1.0
    if v < AIR_NEG_SPEED_THRESHOLD:
        v += AIR_NEG_SPEED_RECOVERY

    return v


def sim_blj_ground_chain(start: float, jumps: int) -> list[float]:
    """Ideal BLJ: each jump applies 1.5× on current speed (no ground friction model).

    Real BLJs interleave land frames, A timing, slope/stair snaps — this is the
    pure multiplier envelope when landing preserves speed between LJs.
    """
    speeds = [start]
    v = start
    for _ in range(jumps):
        v = apply_long_jump_entry(v)
        speeds.append(v)
    return speeds


def cmd_longjump(args: argparse.Namespace) -> None:
    out = apply_long_jump_entry(args.speed)
    print(f"enter ACT_LONG_JUMP: {args.speed} → {out}")
    print(f"  mult={LONG_JUMP_SPEED_MULT}, positive cap only if v>{LONG_JUMP_POS_CAP}")
    if args.speed < 0 and out < args.speed:
        print("  negative speed grew (BLJ core): no negative cap on entry")


def cmd_blj(args: argparse.Namespace) -> None:
    series = sim_blj_ground_chain(args.start, args.jumps)
    print(f"{'n':>4}  {'forwardVel':>14}")
    for i, v in enumerate(series):
        print(f"{i:4d}  {v:14.6f}")
    if len(series) >= 2:
        print(f"ratio last/start: {series[-1] / series[0] if series[0] else float('inf'):.6f}")
        print(f"theory 1.5^n:     {LONG_JUMP_SPEED_MULT ** args.jumps:.6f}")


def cmd_air(args: argparse.Namespace) -> None:
    v = args.speed
    print(f"{'f':>4}  {'forwardVel':>14}")
    print(f"{0:4d}  {v:14.6f}")
    for f in range(1, args.frames + 1):
        v = air_frame(
            v,
            long_jump=args.long_jump,
            stick_mag=args.stick_mag,
            d_yaw_deg=args.dYaw_deg,
            with_turn=args.with_turn,
        )
        print(f"{f:4d}  {v:14.6f}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    s1 = sub.add_parser("longjump", help="single ACT_LONG_JUMP speed transform")
    s1.add_argument("--speed", type=float, required=True)
    s1.set_defaults(func=cmd_longjump)

    s2 = sub.add_parser("blj", help="ideal repeated LJ entry mult chain")
    s2.add_argument("--start", type=float, default=-20.0)
    s2.add_argument("--jumps", type=int, default=8)
    s2.set_defaults(func=cmd_blj)

    s3 = sub.add_parser("air", help="simulate N airborne frames")
    s3.add_argument("--speed", type=float, required=True)
    s3.add_argument("--frames", type=int, default=20)
    s3.add_argument("--stick-mag", type=float, default=32.0)
    s3.add_argument("--dYaw-deg", type=float, default=0.0)
    s3.add_argument("--long-jump", action="store_true")
    s3.add_argument("--with-turn", action="store_true")
    s3.set_defaults(func=cmd_air)

    args = p.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
