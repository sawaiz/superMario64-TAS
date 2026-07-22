#!/usr/bin/env python3
"""Search for a WKW trajectory that keeps the early touch and lands sooner."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import wkw_next_search as wkw
from speedup_search import BASE_MOVIE, BASE_STATE, ROM, run_movie

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "experiments/wall_kicks_landing_search"
CANDIDATE_DIR = OUTPUT_DIR / "candidates"
RESULTS_PATH = OUTPUT_DIR / "results.json"


def seed_edits(inputs: list[tuple[int, int, int]]) -> dict[int, tuple[int, int, int]]:
    return {
        sample: (inputs[sample][0], 100, -128)
        for sample in range(149, 202)
    }


def moved_button(
    inputs: list[tuple[int, int, int]],
    edits: dict[int, tuple[int, int, int]],
    source: int,
    offset: int,
) -> None:
    if offset == 0:
        return
    button = inputs[source][0]
    source_value = edits.get(source, inputs[source])
    edits[source] = (source_value[0] & ~button, source_value[1], source_value[2])
    target = source + offset
    target_value = edits.get(target, inputs[target])
    edits[target] = (target_value[0] | button, target_value[1], target_value[2])


def candidates(inputs: list[tuple[int, int, int]]) -> list[tuple[str, dict]]:
    items: list[tuple[str, dict]] = []
    base = seed_edits(inputs)

    # The jump kick resets vertical speed. Moving either discrete transition is
    # the most direct way to lower the VI 538 touch enough to land at VI 546.
    for kick_offset in (-2, -1, 0, 1, 2):
        for transition_offset in (-2, -1, 0, 1, 2):
            if kick_offset == 0 and transition_offset == 0:
                continue
            edits = dict(base)
            moved_button(inputs, edits, 210, kick_offset)
            moved_button(inputs, edits, 213, transition_offset)
            items.append(
                (f"buttons_k{kick_offset:+d}_t{transition_offset:+d}", edits)
            )

    # Try holding the transition for an adjacent sample rather than moving it.
    for source, label in ((210, "kick"), (213, "transition")):
        button = inputs[source][0]
        for offset in (-2, -1, 1, 2):
            edits = dict(base)
            target = source + offset
            old = inputs[target]
            edits[target] = (old[0] | button, old[1], old[2])
            items.append((f"hold_{label}_{offset:+d}", edits))

    # Counter-steer after the wall interaction to vary horizontal contact and
    # the floor triangle without disturbing the successful early air segment.
    for x in (-16, -8, 0, 8, 16):
        for y in (-128, -126, -124, -120):
            edits = dict(base)
            edits.update(
                {
                    sample: (inputs[sample][0], x, y)
                    for sample in range(214, 224)
                }
            )
            items.append((f"tail_x{x}_y{y}", edits))

    for x in (-16, -8, 0, 8, 16):
        for y in (120, 124, 127):
            edits = dict(base)
            edits[213] = (inputs[213][0], x, y)
            items.append((f"launch_x{x}_y{y}", edits))

    # Find whether the successful 53-sample edit can end earlier. A shorter
    # mutation gives the original final approach more opportunity to recover.
    for end in range(190, 202):
        edits = {
            sample: (inputs[sample][0], 100, -128)
            for sample in range(149, end + 1)
        }
        items.append((f"seed_until_{end}", edits))

    # Test the other seven known VI 538 seeds with a one-sample-earlier kick.
    for x, y in (
        (96, -124),
        (98, -126),
        (98, -124),
        (100, -126),
        (100, -124),
        (102, -126),
        (102, -124),
    ):
        edits = {
            sample: (inputs[sample][0], x, y)
            for sample in range(149, 202)
        }
        moved_button(inputs, edits, 210, -1)
        items.append((f"seed_x{x}_y{y}_kick-1", edits))
    return items


def classify(result: dict, baseline: dict) -> str:
    touch = result.get("star_touch_vi")
    exit_vi = result.get("star_exit_vi")
    if touch is None or exit_vi is None:
        return "rejected: star not reached"
    if touch < baseline["star_touch_vi"] and exit_vi < baseline["star_exit_vi"]:
        return "confirmed speedup"
    if touch < baseline["star_touch_vi"] and exit_vi == baseline["star_exit_vi"]:
        return "early touch, baseline exit"
    if touch < baseline["star_touch_vi"]:
        return "early touch, slower exit"
    if exit_vi == baseline["star_exit_vi"]:
        return "tie: no exit VI saved"
    return "slower"


def write(payload: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-runs", type=int, default=3)
    parser.add_argument("--retry-errors", action="store_true")
    args = parser.parse_args()
    for path in (BASE_MOVIE, BASE_STATE, ROM):
        if not path.is_file():
            raise FileNotFoundError(path)

    wkw.CANDIDATE_DIR = CANDIDATE_DIR
    inputs = wkw.unpack_inputs(BASE_MOVIE.read_bytes())
    all_candidates = candidates(inputs)
    if args.retry_errors:
        payload = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
        edits_by_name = dict(all_candidates)
        for item in payload["candidates"]:
            if not item["result"].startswith("error:"):
                continue
            name = item["candidate"]
            print(f"Retrying {name}...", flush=True)
            movie = wkw.make_candidate(name, edits_by_name[name])
            replacement = {"candidate": name, "edit_count": len(edits_by_name[name])}
            replacement.update(run_movie(movie, 35))
            replacement["result"] = classify(replacement, payload["baseline"])
            item.clear()
            item.update(replacement)
            print(
                f"  {item['result']}; touch={item.get('star_touch_vi')} "
                f"exit={item.get('star_exit_vi')}",
                flush=True,
            )
            write(payload)
        print(RESULTS_PATH, flush=True)
        return 0

    baseline = run_movie(BASE_MOVIE, 30)
    seed_movie = wkw.make_candidate("seed_x100_y-128", seed_edits(inputs))
    seed = run_movie(seed_movie, 30)
    payload = {"baseline": baseline, "seed": seed, "candidates": []}
    write(payload)

    for index, (name, edits) in enumerate(all_candidates, 1):
        print(f"[{index}/{len(all_candidates)}] {name}", flush=True)
        item = {"candidate": name, "edit_count": len(edits)}
        try:
            movie = wkw.make_candidate(name, edits)
            item.update(run_movie(movie, 25))
            item["result"] = classify(item, baseline)
        except Exception as exc:
            item.update({"reached_star": False, "result": f"error: {exc}"})
        payload["candidates"].append(item)
        print(
            f"  {item['result']}; touch={item.get('star_touch_vi')} "
            f"exit={item.get('star_exit_vi')}",
            flush=True,
        )
        write(payload)

    viable = [
        item for item in payload["candidates"]
        if item["result"] in ("confirmed speedup", "early touch, baseline exit")
    ]
    if viable:
        best = min(
            viable,
            key=lambda item: (item["star_exit_vi"], item["star_touch_vi"], item["edit_count"]),
        )
        edits = dict(all_candidates)[best["candidate"]]
        movie = wkw.make_candidate(best["candidate"], edits)
        print(f"Verifying {best['candidate']} {args.verify_runs} times...", flush=True)
        payload["verified_candidate"] = best["candidate"]
        payload["verification"] = [
            run_movie(movie, 30) for _ in range(args.verify_runs)
        ]
        write(payload)

    print(RESULTS_PATH, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
