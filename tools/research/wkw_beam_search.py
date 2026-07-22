#!/usr/bin/env python3
"""Run the calibrated C++ WKW beam search and validate its shortlist in Mupen."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

import wkw_next_search as wkw
from speedup_search import BASE_MOVIE, BASE_STATE, ROM, run_movie

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "experiments/wall_kicks_beam_search"
CANDIDATE_DIR = OUTPUT_DIR / "candidates"
RESULTS_PATH = OUTPUT_DIR / "results.json"
CPP_SOURCE = ROOT / "tools/research/beam/wkw_beam_sim.cpp"
SIMULATOR = CANDIDATE_DIR / "wkw_beam_sim.exe"
SHORTLIST_PATH = CANDIDATE_DIR / "shortlist.csv"
GOAL = (-1976.031860, -2281.780762, -2897.080078)
SUMMARY_RE = re.compile(
    r"controls=(\d+) beam_width=(\d+) shortlist=(\d+) "
    r"calibrated_seed_max_error=([0-9.eE+-]+) elapsed_seconds=([0-9.eE+-]+) "
    r"start_sample=(\d+) end_sample=(\d+) goal_sample=(\d+) target_sample=(\d+)"
)


def seed_edits(inputs: list[tuple[int, int, int]]) -> dict[int, tuple[int, int, int]]:
    return {
        sample: (inputs[sample][0], 94, -104)
        for sample in range(149, 202)
    }


def write(payload: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def build_simulator() -> dict:
    compiler = shutil.which("g++")
    if compiler is None:
        raise RuntimeError("g++ was not found on PATH")
    CANDIDATE_DIR.mkdir(parents=True, exist_ok=True)
    command = [
        compiler,
        "-std=c++20",
        "-O3",
        "-Wall",
        "-Wextra",
        "-Wpedantic",
        str(CPP_SOURCE),
        "-o",
        str(SIMULATOR),
    ]
    started = time.perf_counter()
    completed = subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
    return {
        "compiler": compiler,
        "command": command,
        "elapsed_seconds": time.perf_counter() - started,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def calibrate_seed(seed_movie: Path, timeout: float) -> dict:
    old_values = {name: os.environ.get(name) for name in (
        "SM64_TAS_GOAL_X", "SM64_TAS_GOAL_Y", "SM64_TAS_GOAL_Z"
    )}
    os.environ["SM64_TAS_GOAL_X"] = str(GOAL[0])
    os.environ["SM64_TAS_GOAL_Y"] = str(GOAL[1])
    os.environ["SM64_TAS_GOAL_Z"] = str(GOAL[2])
    try:
        return run_movie(seed_movie, timeout)
    finally:
        for name, value in old_values.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


def run_simulator(
    seed_movie: Path,
    telemetry: Path,
    beam_width: int,
    shortlist: int,
    start_sample: int,
    end_sample: int,
    goal_sample: int,
    target_sample: int,
) -> dict:
    command = [
        str(SIMULATOR),
        str(seed_movie),
        str(telemetry),
        str(CANDIDATE_DIR),
        str(beam_width),
        str(shortlist),
        str(start_sample),
        str(end_sample),
        str(goal_sample),
        str(target_sample),
    ]
    completed = subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
    match = SUMMARY_RE.search(completed.stdout)
    if not match:
        raise RuntimeError("C++ simulator did not emit its summary")
    return {
        "command": command,
        "controls_per_sample": int(match.group(1)),
        "beam_width": int(match.group(2)),
        "shortlist": int(match.group(3)),
        "calibrated_seed_max_error": float(match.group(4)),
        "elapsed_seconds": float(match.group(5)),
        "branch_start_sample": int(match.group(6)),
        "branch_end_sample": int(match.group(7)),
        "goal_sample": int(match.group(8)),
        "target_sample": int(match.group(9)),
        "stdout": completed.stdout,
    }


def read_shortlist() -> list[dict]:
    with SHORTLIST_PATH.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["rank"] = int(row["rank"])
        row["predicted_score"] = float(row["predicted_score"])
        for sample in (221, 222, 223):
            key = f"predicted_distance_{sample}"
            row[key] = float(row[key])
        row["edit_samples"] = int(row["edit_samples"])
    return rows


def classify(item: dict, seed: dict) -> str:
    touch = item.get("star_touch_vi")
    exit_vi = item.get("star_exit_vi")
    if touch is None:
        return "rejected: star not reached"
    if touch < seed["star_touch_vi"]:
        return "potential speedup"
    if touch == seed["star_touch_vi"] and exit_vi == seed["star_exit_vi"]:
        return "ties verified seed"
    return "slower"


def main() -> int:
    global RESULTS_PATH
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--beam-width", type=int, default=2500)
    parser.add_argument("--shortlist", type=int, default=24)
    parser.add_argument("--validate", type=int, default=12)
    parser.add_argument("--timeout", type=float, default=35.0)
    parser.add_argument("--start-sample", type=int, default=214)
    parser.add_argument("--end-sample", type=int, default=221)
    parser.add_argument("--goal-sample", type=int, default=222)
    parser.add_argument("--target-sample", type=int, default=224)
    parser.add_argument(
        "--results-name",
        default="results.json",
        help="output JSON basename inside experiments/wall_kicks_beam_search",
    )
    args = parser.parse_args()
    if Path(args.results_name).name != args.results_name or not args.results_name.endswith(".json"):
        parser.error("--results-name must be a .json basename")
    RESULTS_PATH = OUTPUT_DIR / args.results_name
    if args.validate < 0 or args.validate > args.shortlist:
        parser.error("--validate must be between zero and --shortlist")
    for path in (BASE_MOVIE, BASE_STATE, ROM, CPP_SOURCE):
        if not path.is_file():
            raise FileNotFoundError(path)

    wkw.CANDIDATE_DIR = CANDIDATE_DIR
    inputs = wkw.unpack_inputs(BASE_MOVIE.read_bytes())
    seed_movie = wkw.make_candidate("beam_seed_x94_y-104", seed_edits(inputs))

    print("Building C++ differential simulator...", flush=True)
    build = build_simulator()
    print("Capturing calibrated seed telemetry in Mupen...", flush=True)
    seed = calibrate_seed(seed_movie, args.timeout)
    telemetry = Path(seed["csv"])
    print(
        f"  seed touch={seed['star_touch_vi']} exit={seed['star_exit_vi']} "
        f"hash={seed['parity_hash']}",
        flush=True,
    )

    print(
        f"Searching with beam width {args.beam_width}; simulator shortlist {args.shortlist}...",
        flush=True,
    )
    simulator = run_simulator(
        seed_movie,
        telemetry,
        args.beam_width,
        args.shortlist,
        args.start_sample,
        args.end_sample,
        args.goal_sample,
        args.target_sample,
    )
    shortlist = read_shortlist()
    payload = {
        "method": "C++ decomp-formula differential beam search, Mupen authoritative validation",
        "accuracy_boundary": (
            "The simulator ranks candidates only. Collision, action transitions, VI timing, "
            "and acceptance come exclusively from Mupen telemetry and parity checks."
        ),
        "goal_position": {"x": GOAL[0], "y": GOAL[1], "z": GOAL[2]},
        "build": build,
        "seed": seed,
        "simulator": simulator,
        "shortlist": shortlist,
        "validated_candidates": [],
    }
    write(payload)
    print(
        f"  explored 153 controls/sample in {simulator['elapsed_seconds']:.3f}s; "
        f"seed calibration error={simulator['calibrated_seed_max_error']:.3g}",
        flush=True,
    )

    for index, prediction in enumerate(shortlist[: args.validate], 1):
        movie = CANDIDATE_DIR / prediction["candidate"]
        print(
            f"[Mupen {index}/{args.validate}] {movie.name} "
            f"predicted d222={prediction['predicted_distance_222']:.3f}",
            flush=True,
        )
        item = dict(prediction)
        started = time.perf_counter()
        try:
            item.update(run_movie(movie, args.timeout))
            item["result"] = classify(item, seed)
        except Exception as exc:
            item.update({"reached_star": False, "result": f"error: {exc}"})
        item["validation_elapsed_seconds"] = time.perf_counter() - started
        payload["validated_candidates"].append(item)
        write(payload)
        print(
            f"  {item['result']}; touch={item.get('star_touch_vi')} "
            f"exit={item.get('star_exit_vi')}",
            flush=True,
        )

    validated = payload["validated_candidates"]
    payload["summary"] = {
        "validated": len(validated),
        "potential_speedups": sum(item["result"] == "potential speedup" for item in validated),
        "ties": sum(item["result"] == "ties verified seed" for item in validated),
        "misses": sum(item["result"] == "rejected: star not reached" for item in validated),
        "errors": sum(item["result"].startswith("error:") for item in validated),
        "mupen_validation_seconds": sum(item["validation_elapsed_seconds"] for item in validated),
    }
    write(payload)
    print(json.dumps(payload["summary"], indent=2), flush=True)
    print(RESULTS_PATH, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
