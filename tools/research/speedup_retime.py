#!/usr/bin/env python3
"""Test one-sample input retiming candidates near the WKW star approach."""

from __future__ import annotations

import json
import shutil
import struct
from pathlib import Path

from speedup_search import (
    BASE_MOVIE,
    BASE_STATE,
    HEADER_SIZE,
    LENGTH_SAMPLES_OFFSET,
    require_files,
    run_movie,
)

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "experiments/wall_kicks_retime"
CANDIDATE_DIR = OUTPUT_DIR / "candidates"


def input_at(data: bytes | bytearray, sample: int) -> bytes:
    offset = HEADER_SIZE + sample * 4
    return bytes(data[offset : offset + 4])


def set_input(data: bytearray, sample: int, value: bytes) -> None:
    offset = HEADER_SIZE + sample * 4
    data[offset : offset + 4] = value


def make_candidate(name: str, edits: list[tuple[int, bytes]]) -> Path:
    data = bytearray(BASE_MOVIE.read_bytes())
    samples = struct.unpack_from("<I", data, LENGTH_SAMPLES_OFFSET)[0]
    if len(data) != HEADER_SIZE + samples * 4:
        raise RuntimeError("unexpected baseline movie size")
    for sample, value in edits:
        set_input(data, sample, value)
    CANDIDATE_DIR.mkdir(parents=True, exist_ok=True)
    movie = CANDIDATE_DIR / f"{name}.m64"
    movie.write_bytes(data)
    shutil.copy2(BASE_STATE, movie.with_suffix(".st"))
    return movie


def main() -> int:
    require_files()
    original = BASE_MOVIE.read_bytes()
    neutral_209 = input_at(original, 209)
    input_210 = input_at(original, 210)
    neutral_212 = input_at(original, 212)
    input_213 = input_at(original, 213)

    candidates: list[tuple[str, list[tuple[int, bytes]]]] = [
        ("copy_210_to_209", [(209, input_210)]),
        ("move_210_to_209", [(209, input_210), (210, neutral_209)]),
        ("copy_213_to_212", [(212, input_213)]),
        ("move_213_to_212", [(212, input_213), (213, neutral_212)]),
        ("stick_38_at_224", [(224, struct.pack("<Hbb", 0, 38, -127))]),
        ("stick_40_at_224", [(224, struct.pack("<Hbb", 0, 40, -127))]),
    ]
    for start, end in ((209, 227), (212, 227)):
        edits = [(sample, input_at(original, sample + 1)) for sample in range(start, end + 1)]
        candidates.append((f"shift_{start}_{end}_early", edits))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Running retiming baseline...", flush=True)
    baseline = run_movie(BASE_MOVIE, 30)
    print(
        f"  baseline: star sample={baseline['star_sample']} VI={baseline['star_vi']}",
        flush=True,
    )
    results: list[dict] = []
    for name, edits in candidates:
        print(f"Testing {name}...", flush=True)
        result = {"candidate": name}
        try:
            result.update(run_movie(make_candidate(name, edits), 30))
            if not result["reached_star"]:
                result["result"] = "rejected: star not reached"
            elif result["star_vi"] < baseline["star_vi"]:
                result["result"] = "potential speedup"
            elif result["star_vi"] == baseline["star_vi"]:
                result["result"] = "tie: no VI saved"
            else:
                result["result"] = "slower"
            print(
                f"  {result['result']}; star sample={result.get('star_sample')} "
                f"VI={result.get('star_vi')}",
                flush=True,
            )
        except Exception as exc:
            result.update({"reached_star": False, "result": f"error: {exc}"})
            print(f"  {result['result']}", flush=True)
        results.append(result)
        payload = {"baseline": baseline, "candidates": results}
        (OUTPUT_DIR / "results.json").write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )

    lines = [
        "# Wall Kicks Will Work input-retiming experiment",
        "",
        f"Baseline star: sample {baseline['star_sample']}, VI {baseline['star_vi']}",
        "",
        "| Candidate | Reached star | Star sample | Star VI | VI delta | Result |",
        "|---|:---:|---:|---:|---:|---|",
    ]
    for result in results:
        star_vi = result.get("star_vi")
        delta = star_vi - baseline["star_vi"] if star_vi is not None else None
        lines.append(
            f"| {result['candidate']} | {result['reached_star']} | "
            f"{result.get('star_sample')} | {star_vi} | {delta} | {result['result']} |"
        )
    (OUTPUT_DIR / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    speedups = [result for result in results if result["result"] == "potential speedup"]
    print(f"Retiming search complete: {len(speedups)} potential speedup(s)", flush=True)
    print(f"Results: {OUTPUT_DIR / 'README.md'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
