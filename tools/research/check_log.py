#!/usr/bin/env python3
"""Check CSV logs produced by tas_harness.lua (Windows or any host).

Usage:
  python check_log.py logs/run_us_*.csv
  python check_log.py logs/run_us_xxx.csv --min-speed -100 --require-frames 100
  python check_log.py logs/run_us_xxx.csv --qpu-speed-check
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path

# allow import of research constants
sys.path.insert(0, str(Path(__file__).resolve().parent))
from constants import PU_SIZE, QPU_SIZE  # noqa: E402


def load_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8", errors="replace") as f:
        return list(csv.DictReader(f))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("csv_path", type=Path)
    p.add_argument("--min-speed", type=float, default=None, help="assert some h_speed <= this")
    p.add_argument("--max-speed", type=float, default=None, help="assert some h_speed >= this")
    p.add_argument("--require-frames", type=int, default=1)
    p.add_argument("--qpu-speed-check", action="store_true", help="flag frames with |h| near QPU multiples")
    p.add_argument("--action", type=lambda x: int(x, 0), default=None, help="require action seen (hex ok)")
    args = p.parse_args()

    if not args.csv_path.is_file():
        print(f"FAIL: missing {args.csv_path}")
        return 2

    rows = load_rows(args.csv_path)
    n = len(rows)
    print(f"file: {args.csv_path}")
    print(f"rows: {n}")

    if n < args.require_frames:
        print(f"FAIL: need >= {args.require_frames} frames, got {n}")
        return 1

    speeds = [float(r["h_speed"]) for r in rows if r.get("h_speed") not in (None, "")]
    if not speeds:
        print("FAIL: no h_speed column data")
        return 1

    print(f"h_speed min/max: {min(speeds):.6f} / {max(speeds):.6f}")
    xs = [float(r["x"]) for r in rows]
    zs = [float(r["z"]) for r in rows]
    print(f"x range: {min(xs):.1f} .. {max(xs):.1f}")
    print(f"z range: {min(zs):.1f} .. {max(zs):.1f}")

    ok = True
    if args.min_speed is not None and min(speeds) > args.min_speed:
        print(f"FAIL: expected some h_speed <= {args.min_speed}, min was {min(speeds)}")
        ok = False
    if args.max_speed is not None and max(speeds) < args.max_speed:
        print(f"FAIL: expected some h_speed >= {args.max_speed}, max was {max(speeds)}")
        ok = False

    if args.action is not None:
        actions = {int(r["action"]) for r in rows}
        if args.action not in actions:
            print(f"FAIL: action {args.action:#x} never seen")
            ok = False
        else:
            print(f"OK: saw action {args.action:#x}")

    if args.qpu_speed_check:
        hits = 0
        for s in speeds:
            if abs(s) < 1000:
                continue
            rem = abs(s) % QPU_SIZE
            if rem < 1.0 or rem > QPU_SIZE - 1.0:
                hits += 1
        print(f"near-QPU |speed| samples: {hits} (QPU={QPU_SIZE})")

    # simple NaN / inf guard
    for i, r in enumerate(rows):
        for k in ("h_speed", "x", "y", "z"):
            v = float(r[k])
            if not math.isfinite(v):
                print(f"FAIL: non-finite {k} at row {i}")
                ok = False
                break
        if not ok:
            break

    if ok:
        print("PASS")
        return 0
    print("FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
