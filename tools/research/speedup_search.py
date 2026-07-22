#!/usr/bin/env python3
"""Search selected one-sample deletions in a short SM64 TAS movie.

The experiment runs entirely through Mupen64's supported CLI. Each candidate
removes one controller sample, plays from the matching snapshot, logs state via
tas_harness.lua, and is accepted only if ACT_STAR_DANCE_EXIT is reached on an
earlier VI than the baseline.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import struct
import subprocess
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]
MUPEN = ROOT / "tools/mupen64/repack-stable-main/stable/mupen64.exe"
MUPEN_DIR = MUPEN.parent
MUPEN_LOG = MUPEN_DIR / "logs/mupen.log"
ROM = ROOT / "roms/Super Mario 64 (USA).z64"
HARNESS = ROOT / "tools/research/harness/tas_harness.lua"
BASE_MOVIE = (
    ROOT
    / "tas/archive/SM64TASArchive/Individual Levels/SM64"
    / "CCM - Cool, Cool Mountain/Wall Kicks Will Work"
    / "6s10ms (Textboxes)/Wall Kicks Will Work (U).m64"
)
BASE_STATE = BASE_MOVIE.with_suffix(".st")
LOG_DIR = ROOT / "logs"
OUTPUT_DIR = ROOT / "experiments/wall_kicks_frame_delete"
CANDIDATE_DIR = OUTPUT_DIR / "candidates"

HEADER_SIZE = 0x400
LENGTH_SAMPLES_OFFSET = 0x18
STAR_ACTION = 0x00001302
USA_MD5 = "20b854b239203baf6c961b850a4a51a2"
FINAL_HASH_RE = re.compile(r"Final hash: ([0-9a-f]+) \(([0-9]+) checkpoints\)")

# Boundaries and interior points of neutral/repeated-input runs before the star.
DEFAULT_FRAMES = [24, 43, 67, 94, 96, 98, 113, 127, 175, 211, 224, 227]


def require_files() -> None:
    for path in (MUPEN, ROM, HARNESS, BASE_MOVIE, BASE_STATE):
        if not path.is_file():
            raise FileNotFoundError(path)
    digest = hashlib.md5(ROM.read_bytes()).hexdigest()
    if digest != USA_MD5:
        raise RuntimeError(f"USA ROM MD5 mismatch: {digest}")


def final_hashes() -> list[tuple[str, int]]:
    if not MUPEN_LOG.is_file():
        return []
    text = MUPEN_LOG.read_text(encoding="utf-8", errors="replace")
    return [(match.group(1), int(match.group(2))) for match in FINAL_HASH_RE.finditer(text)]


def newest_csv_after(started: float) -> Path:
    candidates = [
        path
        for path in LOG_DIR.glob("run_us_*.csv")
        if path.stat().st_mtime >= started - 1
    ]
    if not candidates:
        raise RuntimeError("Lua harness did not create a CSV")
    return max(candidates, key=lambda path: path.stat().st_mtime)


def analyze_csv(path: Path) -> dict:
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise RuntimeError(f"empty CSV: {path}")
    star_rows = [row for row in rows if int(row["action"]) == STAR_ACTION]
    first_star = star_rows[0] if star_rows else None
    return {
        "csv": str(path),
        "rows": len(rows),
        "reached_star": first_star is not None,
        "star_sample": int(first_star["sample"]) if first_star else None,
        "star_vi": int(first_star["vi"]) if first_star else None,
        "star_global_timer": int(first_star["global_timer"]) if first_star else None,
        "end_action": int(rows[-1]["action"]),
        "end_x": float(rows[-1]["x"]),
        "end_y": float(rows[-1]["y"]),
        "end_z": float(rows[-1]["z"]),
    }


def run_movie(movie: Path, timeout: float) -> dict:
    baseline_hash_count = len(final_hashes())
    started = time.time()
    command = [
        str(MUPEN),
        "--rom",
        str(ROM),
        "--movie",
        str(movie),
        "--lua",
        str(HARNESS),
        "--parity-check",
        "--parity-check-interval",
        "10",
        "--close-on-movie-end",
    ]
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    process = subprocess.Popen(command, cwd=MUPEN_DIR, startupinfo=startupinfo)
    parity: tuple[str, int] | None = None
    try:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            hashes = final_hashes()
            if len(hashes) > baseline_hash_count:
                parity = hashes[-1]
                break
            if process.poll() is not None:
                break
            time.sleep(0.1)
        if parity is None:
            raise TimeoutError(f"no new parity hash within {timeout:g}s")
        time.sleep(0.75)
    finally:
        if process.poll() is None:
            process.kill()
        process.wait(timeout=5)
    result = analyze_csv(newest_csv_after(started))
    result["parity_hash"] = parity[0] if parity else None
    result["parity_checkpoints"] = parity[1] if parity else None
    return result


def make_deletion_candidate(frame: int) -> Path:
    data = bytearray(BASE_MOVIE.read_bytes())
    samples = struct.unpack_from("<I", data, LENGTH_SAMPLES_OFFSET)[0]
    if frame < 0 or frame >= samples:
        raise ValueError(f"frame {frame} outside 0..{samples - 1}")
    expected_size = HEADER_SIZE + samples * 4
    if len(data) != expected_size:
        raise RuntimeError(f"unexpected movie size {len(data)}; expected {expected_size}")
    del data[HEADER_SIZE + frame * 4 : HEADER_SIZE + (frame + 1) * 4]
    struct.pack_into("<I", data, LENGTH_SAMPLES_OFFSET, samples - 1)
    CANDIDATE_DIR.mkdir(parents=True, exist_ok=True)
    movie = CANDIDATE_DIR / f"delete_{frame:03}.m64"
    movie.write_bytes(data)
    shutil.copy2(BASE_STATE, movie.with_suffix(".st"))
    return movie


def write_results(results: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "results.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8"
    )
    baseline = results["baseline"]
    lines = [
        "# Wall Kicks Will Work frame-deletion experiment",
        "",
        f"Baseline star: sample {baseline['star_sample']}, VI {baseline['star_vi']}",
        "",
        "| Deleted sample | Reached star | Star sample | Star VI | VI delta | Result |",
        "|---:|:---:|---:|---:|---:|---|",
    ]
    for candidate in results["candidates"]:
        star_vi = candidate.get("star_vi")
        delta = star_vi - baseline["star_vi"] if star_vi is not None else None
        lines.append(
            f"| {candidate['deleted_sample']} | {candidate['reached_star']} | "
            f"{candidate.get('star_sample')} | {star_vi} | {delta} | {candidate['result']} |"
        )
    (OUTPUT_DIR / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frames", nargs="*", type=int, default=DEFAULT_FRAMES)
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()

    require_files()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Running baseline...")
    baseline = run_movie(BASE_MOVIE, args.timeout)
    if not baseline["reached_star"]:
        raise RuntimeError("baseline did not reach ACT_STAR_DANCE_EXIT")
    print(
        f"  baseline: star sample={baseline['star_sample']} VI={baseline['star_vi']} "
        f"hash={baseline['parity_hash']}"
    )

    candidates: list[dict] = []
    for frame in args.frames:
        print(f"Testing deletion at sample {frame}...")
        candidate = {"deleted_sample": frame}
        try:
            candidate.update(run_movie(make_deletion_candidate(frame), args.timeout))
            if not candidate["reached_star"]:
                candidate["result"] = "rejected: star not reached"
            elif candidate["star_vi"] < baseline["star_vi"]:
                candidate["result"] = "potential speedup"
            elif candidate["star_vi"] == baseline["star_vi"]:
                candidate["result"] = "tie: no VI saved"
            else:
                candidate["result"] = "slower"
            print(
                f"  {candidate['result']}; star sample={candidate.get('star_sample')} "
                f"VI={candidate.get('star_vi')}"
            )
        except Exception as exc:  # keep the batch running and report every candidate
            candidate.update({"reached_star": False, "result": f"error: {exc}"})
            print(f"  {candidate['result']}")
        candidates.append(candidate)
        write_results({"baseline": baseline, "candidates": candidates})

    speedups = [item for item in candidates if item["result"] == "potential speedup"]
    print(f"Search complete: {len(speedups)} potential speedup(s)")
    print(f"Results: {OUTPUT_DIR / 'README.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
