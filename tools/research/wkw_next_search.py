#!/usr/bin/env python3
"""Run higher-value Wall Kicks Will Work timing and trajectory searches."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import struct
from pathlib import Path

from speedup_search import (
    BASE_MOVIE,
    BASE_STATE,
    HEADER_SIZE,
    LENGTH_SAMPLES_OFFSET,
    ROM,
    run_movie,
)

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "experiments/wall_kicks_next_search"
CANDIDATE_DIR = OUTPUT_DIR / "candidates"
JP_ROM = ROOT / "roms/Super Mario 64 (Japan).z64"
ARCHIVE_DIR = (
    ROOT
    / "tas/archive/SM64TASArchive/Individual Levels/SM64"
    / "CCM - Cool, Cool Mountain/Wall Kicks Will Work"
)
FAST_US = ARCHIVE_DIR / "05s53ms/Wall Kicks Will Work (U).m64"
FAST_JP = ARCHIVE_DIR / "5s53ms/Wall Kicks Will Work (J).m64"


def unpack_inputs(data: bytes | bytearray) -> list[tuple[int, int, int]]:
    count = struct.unpack_from("<I", data, LENGTH_SAMPLES_OFFSET)[0]
    return [
        struct.unpack_from("<Hbb", data, HEADER_SIZE + sample * 4)
        for sample in range(count)
    ]


def make_candidate(name: str, edits: dict[int, tuple[int, int, int]]) -> Path:
    data = bytearray(BASE_MOVIE.read_bytes())
    count = struct.unpack_from("<I", data, LENGTH_SAMPLES_OFFSET)[0]
    if len(data) != HEADER_SIZE + count * 4:
        raise RuntimeError("unexpected baseline movie size")
    for sample, value in edits.items():
        if not 0 <= sample < count:
            raise ValueError(f"sample {sample} outside movie")
        struct.pack_into("<Hbb", data, HEADER_SIZE + sample * 4, *value)
    CANDIDATE_DIR.mkdir(parents=True, exist_ok=True)
    movie = CANDIDATE_DIR / f"{name}.m64"
    movie.write_bytes(data)
    shutil.copy2(BASE_STATE, movie.with_suffix(".st"))
    return movie


def textbox_candidates(inputs: list[tuple[int, int, int]]) -> list[tuple[str, dict]]:
    candidates = []
    for source, radius in ((95, 4), (99, 3)):
        button = inputs[source][0]
        for offset in range(-radius, radius + 1):
            if offset == 0:
                continue
            target = source + offset
            edits = {
                source: (0, inputs[source][1], inputs[source][2]),
                target: (inputs[target][0] | button, inputs[target][1], inputs[target][2]),
            }
            candidates.append((f"textbox_move_{source}_{offset:+d}", edits))
        for offset in range(-radius, 0):
            target = source + offset
            edits = {
                target: (inputs[target][0] | button, inputs[target][1], inputs[target][2])
            }
            candidates.append((f"textbox_copy_{source}_{offset:+d}", edits))
    for amount in (1, 2):
        edits = {sample: inputs[sample + amount] for sample in range(100, 228 - amount)}
        candidates.append((f"movement_block_early_{amount}", edits))
    return candidates


def route_candidates(inputs: list[tuple[int, int, int]]) -> list[tuple[str, dict]]:
    candidates = []
    for label, movie, source_start, source_end in (
        ("us", FAST_US, 69, 200),
        ("jp", FAST_JP, 86, 217),
    ):
        donor_inputs = unpack_inputs(movie.read_bytes())
        for destination_start in (100, 101, 102):
            edits = {
                destination_start + offset: donor_inputs[source]
                for offset, source in enumerate(range(source_start, source_end + 1))
            }
            candidates.append(
                (f"route_{label}_walk_to_{destination_start}", edits)
            )
    return candidates


def air_candidates(inputs: list[tuple[int, int, int]]) -> list[tuple[str, dict]]:
    candidates = []
    for x in (94, 96, 98, 100, 102):
        for y in (-128, -126, -124):
            if (x, y) == (98, -128):
                continue
            edits = {sample: (inputs[sample][0], x, y) for sample in range(149, 202)}
            candidates.append((f"air_full_x{x}_y{y}", edits))
    for start, end, label in ((149, 175, "early"), (176, 201, "late")):
        for dx in (-4, -2, 2, 4):
            edits = {
                sample: (
                    inputs[sample][0],
                    max(-128, min(127, inputs[sample][1] + dx)),
                    inputs[sample][2],
                )
                for sample in range(start, end + 1)
            }
            candidates.append((f"air_{label}_dx{dx:+d}", edits))
    return candidates


def final_candidates(inputs: list[tuple[int, int, int]]) -> list[tuple[str, dict]]:
    candidates = []
    first_button = inputs[210][0]
    second_button = inputs[213][0]
    for first_offset in (-1, 0, 1):
        for second_offset in (-1, 0, 1):
            if first_offset == 0 and second_offset == 0:
                continue
            edits = {
                210: (0, inputs[210][1], inputs[210][2]),
                213: (0, inputs[213][1], inputs[213][2]),
            }
            first_target = 210 + first_offset
            second_target = 213 + second_offset
            edits[first_target] = (
                edits.get(first_target, inputs[first_target])[0] | first_button,
                inputs[first_target][1],
                inputs[first_target][2],
            )
            edits[second_target] = (
                edits.get(second_target, inputs[second_target])[0] | second_button,
                inputs[second_target][1],
                inputs[second_target][2],
            )
            candidates.append(
                (f"final_buttons_{first_offset:+d}_{second_offset:+d}", edits)
            )
    for x in (-8, -4, 4, 8):
        for y in (-127, -124):
            edits = {sample: (inputs[sample][0], x, y) for sample in range(214, 225)}
            candidates.append((f"final_line_x{x}_y{y}", edits))
    for x in (-8, 0, 8):
        for y in (124, 127):
            edits = {213: (inputs[213][0], x, y)}
            candidates.append((f"final_launch_x{x}_y{y}", edits))
    return candidates


def classify(result: dict, baseline: dict) -> str:
    touch = result.get("star_touch_vi")
    if touch is None:
        return "rejected: star not reached"
    delta = touch - baseline["star_touch_vi"]
    if delta < 0:
        return "potential speedup"
    if delta == 0:
        return "tie: no VI saved"
    return "slower"


def run_candidates(stage: str, candidates: list[tuple[str, dict]], baseline: dict) -> list[dict]:
    results = []
    for index, (name, edits) in enumerate(candidates, 1):
        print(f"[{stage} {index}/{len(candidates)}] {name}", flush=True)
        item = {"stage": stage, "candidate": name, "edit_count": len(edits)}
        try:
            item.update(run_movie(make_candidate(name, edits), 25))
            item["result"] = classify(item, baseline)
        except Exception as exc:
            item.update({"reached_star": False, "result": f"error: {exc}"})
        print(
            f"  {item['result']}; touch={item.get('star_touch_vi')} "
            f"exit={item.get('star_exit_vi')}",
            flush=True,
        )
        results.append(item)
    return results


def donor(movie: Path, *, rom: Path, region: str) -> dict:
    result = {
        "movie": str(movie.relative_to(ROOT)),
        "region": region,
        "declared_samples": struct.unpack_from("<I", movie.read_bytes(), 0x18)[0],
        "rom_md5": hashlib.md5(rom.read_bytes()).hexdigest(),
    }
    result.update(run_movie(movie, 30, rom=rom, region=region))
    return result


def write_results(payload: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "results.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stages",
        nargs="+",
        choices=("route", "textbox", "air", "final", "verify"),
        default=("route", "textbox", "air", "final"),
    )
    parser.add_argument("--verify-runs", type=int, default=3)
    args = parser.parse_args()

    for path in (BASE_MOVIE, BASE_STATE, ROM, JP_ROM, FAST_US, FAST_JP):
        if not path.is_file():
            raise FileNotFoundError(path)

    original = BASE_MOVIE.read_bytes()
    inputs = unpack_inputs(original)

    if args.stages == ["verify"]:
        results_path = OUTPUT_DIR / "results.json"
        payload = json.loads(results_path.read_text(encoding="utf-8"))
        chosen_name = "air_full_x100_y-128"
        edits = dict(air_candidates(inputs))[chosen_name]
        movie = make_candidate(chosen_name, edits)
        print(f"Replaying {chosen_name} {args.verify_runs} times...", flush=True)
        payload["verification"] = [
            run_movie(movie, 30) for _ in range(args.verify_runs)
        ]
        payload["verified_candidate"] = chosen_name
        write_results(payload)
        print(OUTPUT_DIR / "results.json", flush=True)
        return 0

    print("Running corrected-metric baseline...", flush=True)
    baseline = run_movie(BASE_MOVIE, 30)
    print(
        f"  touch sample={baseline['star_touch_sample']} VI={baseline['star_touch_vi']}; "
        f"exit sample={baseline['star_exit_sample']} VI={baseline['star_exit_vi']}",
        flush=True,
    )
    payload = {"baseline": baseline, "route_donors": [], "candidates": []}
    write_results(payload)

    if "route" in args.stages:
        for movie, rom, region in ((FAST_US, ROM, "us"), (FAST_JP, JP_ROM, "jp")):
            print(f"Running route donor {movie.parent.name} ({region})...", flush=True)
            try:
                payload["route_donors"].append(donor(movie, rom=rom, region=region))
            except Exception as exc:
                payload["route_donors"].append(
                    {"movie": str(movie.relative_to(ROOT)), "region": region, "error": str(exc)}
                )
            write_results(payload)
        payload["candidates"].extend(
            run_candidates("route", route_candidates(inputs), baseline)
        )
        write_results(payload)

    for stage, candidates in (
        ("textbox", textbox_candidates(inputs)),
        ("air", air_candidates(inputs)),
        ("final", final_candidates(inputs)),
    ):
        if stage in args.stages:
            payload["candidates"].extend(run_candidates(stage, candidates, baseline))
            write_results(payload)

    speedups = [item for item in payload["candidates"] if item["result"] == "potential speedup"]
    print(f"Complete: {len(speedups)} potential speedup(s)", flush=True)
    print(OUTPUT_DIR / "results.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
