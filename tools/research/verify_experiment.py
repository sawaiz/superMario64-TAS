#!/usr/bin/env python3
"""Experiment verification layers for SM64 TAS (console-first).

Tier A — fully automated here (no emulator):
  Physics envelopes from decomp (BLJ, air, PU cast, clock-punch windows).

Tier B — semi-automated:
  Inspect .m64 headers; print Mupen/Whisky commands to play a movie.

Tier C — human / hardware (cannot fully automate in this environment):
  Full game-state sim, lag, PU crashes, TASbot console replay.

Usage:
  python3 verify_experiment.py formula blj --start -20 --jumps 6
  python3 verify_experiment.py formula pu --x 40000 --z 0
  python3 verify_experiment.py m64 ../tas/full-game/1-key/*.m64
  python3 verify_experiment.py play --movie path/to.m64
"""

from __future__ import annotations

import argparse
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from air_physics import apply_long_jump_entry, air_frame, sim_blj_ground_chain  # noqa: E402
from pu_nav import float_to_s16, pu_index, collision_xz  # noqa: E402
from wall_punch import clock_hspd_bounds  # noqa: E402
from constants import QPU_SIZE, PU_SIZE  # noqa: E402


def cmd_formula_blj(args: argparse.Namespace) -> None:
    series = sim_blj_ground_chain(args.start, args.jumps)
    print("=== Tier A: BLJ entry chain (decomp 1.5×, no land model) ===")
    for i, v in enumerate(series):
        print(f"  after {i} LJ entries: {v:.6f}")
    print("PASS if your Mupen STROOP forwardVel on LJ frame matches ±epsilon")
    print("FAIL if you only match after ignoring land/dust/slope (expected gap)")


def cmd_formula_pu(args: argparse.Namespace) -> None:
    print("=== Tier A: PU collision cast ===")
    sx, sz, ok = collision_xz(args.x, args.z)
    print(f"  float ({args.x}, {args.z}) → s16 ({sx}, {sz}) in_boundary={ok}")
    print(f"  PU index X={pu_index(args.x)} Z={pu_index(args.z)}")
    if isinstance(sx, str) or isinstance(sz, str):
        print("REJECT for console: INVALID_TRUNC risk")
        return
    if args.speed is not None:
        v = args.speed
        print(f"  speed {v}: mod PU={abs(v)%PU_SIZE} mod QPU={abs(v)%QPU_SIZE}")
        if abs(v) % QPU_SIZE == 0:
            print("  QPU-aligned: good candidate for console-safe lattice travel")
        else:
            print("  not QPU-aligned: OK only if route accounts for phase drift")


def cmd_formula_clock(args: argparse.Namespace) -> None:
    hmin, hmax, ok = clock_hspd_bounds(args.theta)
    print("=== Tier A: clock-punch window (1 Key geometry) ===")
    print(f"  θ={args.theta}  hMin={hmin:.4f}  hMax={hmax:.4f}  possible={ok}")
    if args.speed is not None:
        s = args.speed
        inside = hmin <= s <= hmax
        print(f"  speed {s}: inside window? {inside}")


def cmd_formula_air(args: argparse.Namespace) -> None:
    print("=== Tier A: air speed frames ===")
    v = args.speed
    print(f"  f0 {v:.6f}")
    for f in range(1, args.frames + 1):
        v = air_frame(
            v,
            long_jump=args.long_jump,
            stick_mag=args.stick_mag,
            d_yaw_deg=args.dYaw_deg,
        )
        print(f"  f{f} {v:.6f}")


def parse_m64(path: Path) -> dict:
    data = path.read_bytes()
    if data[:4] != b"M64\x1a":
        raise ValueError(f"not an m64: {path}")
    ver, uid, vi_count, rerecord = struct.unpack_from("<IIII", data, 4)
    # https://tasvideos.org/EmulatorResources/Mupen/M64
    # 0x15: num controllers (1 byte) in some docs; layout version 3:
    # offset 0x18: length of controller data in bytes? 
    # Actually common v3:
    # 0x0C vi count, 0x10 rerecords, 0x14 vis/sec, 0x18 num controllers (u4?),
    vis_per_sec = struct.unpack_from("<I", data, 0x14)[0]
    rom_name = data[0xC4 : 0xC4 + 32].split(b"\0")[0].decode("ascii", "replace")
    # input start typically 0x400 for v3
    header_end = 0x400
    input_bytes = max(0, len(data) - header_end)
    # 4 bytes per controller per frame typically for 1 controller
    approx_frames = input_bytes // 4
    return {
        "path": str(path),
        "version": ver,
        "uid": uid,
        "vi_count": vi_count,
        "rerecords": rerecord,
        "vis_per_sec": vis_per_sec,
        "rom_name": rom_name,
        "approx_input_frames": approx_frames,
        "size": len(data),
    }


def cmd_m64(args: argparse.Namespace) -> None:
    print("=== Tier B: .m64 header inspect (no emulation) ===")
    for pattern in args.movies:
        for path in sorted(Path().glob(pattern) if "*" in pattern else [Path(pattern)]):
            if not path.is_file():
                # try from ROOT
                alt = ROOT / path
                path = alt if alt.is_file() else path
            if not path.is_file():
                print(f"  missing: {pattern}")
                continue
            info = parse_m64(path)
            print(f"  {path.name}")
            for k, v in info.items():
                if k != "path":
                    print(f"    {k}: {v}")
            # crude region hint
            print("    region_hint: use JP for classic 1-key, US for many ILs — match ROM")


def cmd_play(args: argparse.Namespace) -> None:
    movie = Path(args.movie)
    if not movie.is_file():
        movie = ROOT / args.movie
    mupen = ROOT / "tools/mupen64/repack-stable-main/stable/mupen64.exe"
    print("=== Tier B: launch Mupen (GUI) — you verify playback ===")
    print(f"  movie: {movie}")
    print(f"  mupen: {mupen}")
    if not mupen.is_file():
        print("FAIL: mupen missing — run tools/scripts/download_tools.sh")
        return
    if not movie.is_file():
        print("FAIL: movie missing")
        return
    print(
        """
  Manual steps (Whisky):
    1. whisky run SM64-TAS <mupen64.exe>
    2. Load matching region ROM
    3. Movie → Play → select the .m64
    4. Optional: SM64 Lua Redux + STROOP for watches

  This script cannot read Mario position from a headless N64 core yet.
  Formula tier (verify_experiment.py formula ...) checks math offline.
"""
    )
    if args.launch:
        bottle = args.bottle
        cmd = ["whisky", "run", bottle, str(mupen)]
        print("  launching:", " ".join(cmd))
        try:
            subprocess.Popen(cmd)
            print("  Mupen start requested — complete movie play in GUI")
        except FileNotFoundError:
            print("  whisky not in PATH; open Whisky app and run mupen manually")


def cmd_tiers(_: argparse.Namespace) -> None:
    print(
        """
Verification tiers
------------------
A) Formula sim (this machine, automated)
   - BLJ / air / PU cast / clock window
   - Does NOT include walls, lag, objects, camera, RNG text

B) Emulator playback (Mupen GUI via Whisky)
   - Proves movie syncs on community TAS stack
   - STROOP for experiment watches
   - Still can diverge from console lag/crashes

C) Real N64 (required for "done" — console-first.md)
   - TASbot / community verify
   - Only C accepts a finished claim

What I (the agent) can do in-session:
  - Run Tier A fully
  - Launch Tier B / parse m64
  - Not run full closed-loop N64 game state or console
"""
    )


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("tiers", help="explain what can be simulated")
    t.set_defaults(func=cmd_tiers)

    f = sub.add_parser("formula", help="Tier A offline physics")
    fs = f.add_subparsers(dest="fcmd", required=True)

    b = fs.add_parser("blj")
    b.add_argument("--start", type=float, default=-20.0)
    b.add_argument("--jumps", type=int, default=6)
    b.set_defaults(func=cmd_formula_blj)

    pu = fs.add_parser("pu")
    pu.add_argument("--x", type=float, required=True)
    pu.add_argument("--z", type=float, default=0.0)
    pu.add_argument("--speed", type=float, default=None)
    pu.set_defaults(func=cmd_formula_pu)

    cl = fs.add_parser("clock")
    cl.add_argument("--theta", type=int, default=-272)
    cl.add_argument("--speed", type=float, default=None)
    cl.set_defaults(func=cmd_formula_clock)

    air = fs.add_parser("air")
    air.add_argument("--speed", type=float, required=True)
    air.add_argument("--frames", type=int, default=10)
    air.add_argument("--stick-mag", type=float, default=32.0)
    air.add_argument("--dYaw-deg", type=float, default=0.0)
    air.add_argument("--long-jump", action="store_true")
    air.set_defaults(func=cmd_formula_air)

    m = sub.add_parser("m64", help="Tier B inspect movie files")
    m.add_argument("movies", nargs="+")
    m.set_defaults(func=cmd_m64)

    pl = sub.add_parser("play", help="Tier B open Mupen for manual movie play")
    pl.add_argument("--movie", required=True)
    pl.add_argument("--launch", action="store_true")
    pl.add_argument("--bottle", default="SM64-TAS")
    pl.set_defaults(func=cmd_play)

    args = p.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
