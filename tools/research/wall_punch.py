#!/usr/bin/env python3
"""Clock-punch class wall math (from TASVideos 1 Key notes + decomp punch probe).

Decomp: wall punch tests a point 50 units in front of Mario; connects if near wall.
1 Key submission derives min H speed for a given facing delta at the 50-star door clock.

This tool:
  - punch-connect check for (distance_to_wall, delta_facing_deg)
  - 1 Key closed-form hSpdMin for Wall-A/Wall-B clock geometry (US castle numbers)

Usage:
  python3 wall_punch.py connect --dist 52 --dyaw-deg 15
  python3 wall_punch.py clock --theta -272
  python3 wall_punch.py clock-table
"""

from __future__ import annotations

import argparse
import math
import sys

from constants import PUNCH_CONNECT_RADIUS, PUNCH_PROBE_DIST


def punch_connects(distance_to_wall: float, delta_yaw_rad: float) -> bool:
    """True if punch probe hits wall.

    Condition from 1 Key notes:
      cos(Δθ) >= (d - 5) / 50
    with d = distance to wall, probe = 50, connect radius = 5.
    """
    if distance_to_wall > PUNCH_PROBE_DIST + PUNCH_CONNECT_RADIUS:
        return False
    # If farther than 55, never connects regardless of angle
    if distance_to_wall > PUNCH_PROBE_DIST + PUNCH_CONNECT_RADIUS:
        return False
    rhs = (distance_to_wall - PUNCH_CONNECT_RADIUS) / PUNCH_PROBE_DIST
    return math.cos(delta_yaw_rad) >= rhs


def critical_distance(delta_yaw_rad: float) -> float:
    """Max distance at which punch still connects for given angle."""
    return PUNCH_CONNECT_RADIUS + PUNCH_PROBE_DIST * math.cos(delta_yaw_rad)


def clock_hspd_bounds(theta_s16: int) -> tuple[float, float, bool]:
    """1 Key clock-punch closed form (submission 7161S).

    θ in SM64 s16 angle units (65536 = 360°). Negative values face the clock corner.
    Returns (|hSpdMin|, hSpdMax, possible) matching the published table magnitudes.
    """
    # Convert s16 angle units to radians: full circle 0x10000
    delta = (theta_s16 / 65536.0) * 2 * math.pi
    # hSpdMin = 103 * (cos(Δθ) - 0.9) / sin(Δθ)
    # hSpdMax = 400 / cos(Δθ)
    # For negative θ, raw hSpdMin is negative; TAS notes list positive speeds.
    c, s = math.cos(delta), math.sin(delta)
    if abs(s) < 1e-12:
        return float("inf"), float("inf"), False
    h_min_raw = 103.0 * (c - 0.9) / s
    h_min = abs(h_min_raw)
    h_max = abs(400.0 / c) if abs(c) > 1e-12 else float("inf")
    # Possible when min speed is below max (room to hold ~400 into the corner)
    possible = h_min < h_max
    return h_min, h_max, possible


def cmd_connect(args: argparse.Namespace) -> None:
    dy = math.radians(args.dyaw_deg)
    ok = punch_connects(args.dist, dy)
    crit = critical_distance(dy)
    print(f"dist={args.dist}  Δyaw={args.dyaw_deg}°")
    print(f"  punch connects?: {ok}")
    print(f"  critical distance for this angle: {crit:.4f}")
    print(f"  formula: cos(Δθ) >= (d - {PUNCH_CONNECT_RADIUS}) / {PUNCH_PROBE_DIST}")


def cmd_clock(args: argparse.Namespace) -> None:
    hmin, hmax, ok = clock_hspd_bounds(args.theta)
    print(f"θ (s16 units) = {args.theta}")
    print(f"  hSpdMin ≈ {hmin:.6f}")
    print(f"  hSpdMax ≈ {hmax:.6f}")
    print(f"  possible (min<max, min>0)?: {ok}")
    print("  note: 1 Key used θ=-272 with ~400 speed at clock corner")


def cmd_clock_table(_: argparse.Namespace) -> None:
    print(f"{'θ':>8}  {'hMin':>12}  {'hMax':>12}  possible")
    for th in (-320, -304, -288, -272, -256, -240):
        hmin, hmax, ok = clock_hspd_bounds(th)
        print(f"{th:8d}  {hmin:12.4f}  {hmax:12.4f}  {ok}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    c1 = sub.add_parser("connect")
    c1.add_argument("--dist", type=float, required=True)
    c1.add_argument("--dyaw-deg", type=float, required=True)
    c1.set_defaults(func=cmd_connect)

    c2 = sub.add_parser("clock")
    c2.add_argument("--theta", type=int, required=True, help="s16 angle units")
    c2.set_defaults(func=cmd_clock)

    c3 = sub.add_parser("clock-table")
    c3.set_defaults(func=cmd_clock_table)

    args = p.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
