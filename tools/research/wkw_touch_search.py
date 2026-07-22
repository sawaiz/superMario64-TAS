#!/usr/bin/env python3
"""Refine WKW air control to find the earliest possible star touch."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import wkw_next_search as wkw
from speedup_search import BASE_MOVIE, BASE_STATE, ROM, run_movie

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "experiments/wall_kicks_touch_search"
CANDIDATE_DIR = OUTPUT_DIR / "candidates"
RESULTS_PATH = OUTPUT_DIR / "results.json"


def grid(inputs: list[tuple[int, int, int]]) -> list[tuple[str, dict]]:
    items = []
    for x in range(88, 121, 2):
        for y in range(-128, -103, 4):
            edits = {
                sample: (inputs[sample][0], x, y)
                for sample in range(149, 202)
            }
            items.append((f"grid_x{x}_y{y}", edits))
    return items


def refinement_grid(inputs: list[tuple[int, int, int]]) -> list[tuple[str, dict]]:
    points = set()
    for x in range(90, 99):
        for y in range(-108, -99):
            points.add((x, y))
    for x in range(108, 121):
        for y in range(-128, -119):
            points.add((x, y))
    return [
        (
            f"grid_x{x}_y{y}",
            {
                sample: (inputs[sample][0], x, y)
                for sample in range(149, 202)
            },
        )
        for x, y in sorted(points)
    ]


def write(payload: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--refine-only", action="store_true")
    parser.add_argument("--retry-errors", action="store_true")
    args = parser.parse_args()
    for path in (BASE_MOVIE, BASE_STATE, ROM):
        if not path.is_file():
            raise FileNotFoundError(path)
    wkw.CANDIDATE_DIR = CANDIDATE_DIR
    inputs = wkw.unpack_inputs(BASE_MOVIE.read_bytes())
    candidates = grid(inputs)
    refinements = refinement_grid(inputs)
    if args.retry_errors:
        payload = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
        all_edits = dict(candidates + refinements)
        for key in ("candidates", "refined_candidates"):
            for item in payload.get(key, []):
                if not item["result"].startswith("error:"):
                    continue
                name = item["candidate"]
                print(f"Retrying {name}...", flush=True)
                movie = wkw.make_candidate(name, all_edits[name])
                replacement = {"candidate": name, "edit_count": len(all_edits[name])}
                replacement.update(run_movie(movie, 35))
                touch = replacement.get("star_touch_vi")
                if touch is None:
                    replacement["result"] = "rejected: star not reached"
                elif touch < payload["baseline"]["star_touch_vi"]:
                    replacement["result"] = "potential speedup"
                elif touch == payload["baseline"]["star_touch_vi"]:
                    replacement["result"] = "tie"
                else:
                    replacement["result"] = "slower"
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
    if args.verify_only:
        payload = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
        reached = [item for item in payload["candidates"] if item.get("star_touch_vi")]
        best = min(
            reached,
            key=lambda item: (
                item["star_touch_vi"],
                item.get("star_exit_vi") or 999999,
                item["edit_count"],
            ),
        )
        movie = wkw.make_candidate(best["candidate"], dict(candidates)[best["candidate"]])
        print(f"Verifying {best['candidate']} 3 times...", flush=True)
        payload["verified_candidate"] = best["candidate"]
        payload["verification"] = [run_movie(movie, 30) for _ in range(3)]
        write(payload)
        print(RESULTS_PATH, flush=True)
        return 0

    if args.refine_only:
        payload = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
        already_run = {
            item["candidate"]
            for key in ("candidates", "refined_candidates")
            for item in payload.get(key, [])
        }
        pending = [(name, edits) for name, edits in refinements if name not in already_run]
        payload.setdefault("refined_candidates", [])
        for index, (name, edits) in enumerate(pending, 1):
            print(f"[refine {index}/{len(pending)}] {name}", flush=True)
            item = {"candidate": name, "edit_count": len(edits)}
            try:
                movie = wkw.make_candidate(name, edits)
                item.update(run_movie(movie, 25))
                touch = item.get("star_touch_vi")
                if touch is None:
                    item["result"] = "rejected: star not reached"
                elif touch < payload["baseline"]["star_touch_vi"]:
                    item["result"] = "potential speedup"
                elif touch == payload["baseline"]["star_touch_vi"]:
                    item["result"] = "tie"
                else:
                    item["result"] = "slower"
            except Exception as exc:
                item.update({"reached_star": False, "result": f"error: {exc}"})
            payload["refined_candidates"].append(item)
            print(
                f"  {item['result']}; touch={item.get('star_touch_vi')} "
                f"exit={item.get('star_exit_vi')}",
                flush=True,
            )
            write(payload)
        all_results = payload["candidates"] + payload["refined_candidates"]
        reached = [item for item in all_results if item.get("star_touch_vi")]
        best = min(
            reached,
            key=lambda item: (
                item["star_touch_vi"],
                item.get("star_exit_vi") or 999999,
                item["edit_count"],
            ),
        )
        all_edits = dict(candidates + refinements)
        movie = wkw.make_candidate(best["candidate"], all_edits[best["candidate"]])
        print(f"Verifying {best['candidate']} 3 times...", flush=True)
        payload["verified_candidate"] = best["candidate"]
        payload["verification"] = [run_movie(movie, 30) for _ in range(3)]
        write(payload)
        print(RESULTS_PATH, flush=True)
        return 0

    baseline = run_movie(BASE_MOVIE, 30)
    payload = {"baseline": baseline, "candidates": []}
    write(payload)
    for index, (name, edits) in enumerate(candidates, 1):
        print(f"[{index}/{len(candidates)}] {name}", flush=True)
        item = {"candidate": name, "edit_count": len(edits)}
        try:
            movie = wkw.make_candidate(name, edits)
            item.update(run_movie(movie, 25))
            touch = item.get("star_touch_vi")
            if touch is None:
                item["result"] = "rejected: star not reached"
            elif touch < baseline["star_touch_vi"]:
                item["result"] = "potential speedup"
            elif touch == baseline["star_touch_vi"]:
                item["result"] = "tie"
            else:
                item["result"] = "slower"
        except Exception as exc:
            item.update({"reached_star": False, "result": f"error: {exc}"})
        payload["candidates"].append(item)
        print(
            f"  {item['result']}; touch={item.get('star_touch_vi')} "
            f"exit={item.get('star_exit_vi')}",
            flush=True,
        )
        write(payload)

    reached = [item for item in payload["candidates"] if item.get("star_touch_vi")]
    best = min(
        reached,
        key=lambda item: (
            item["star_touch_vi"],
            item.get("star_exit_vi") or 999999,
            item["edit_count"],
        ),
    )
    edits = dict(candidates)[best["candidate"]]
    movie = wkw.make_candidate(best["candidate"], edits)
    print(f"Verifying {best['candidate']} 3 times...", flush=True)
    payload["verified_candidate"] = best["candidate"]
    payload["verification"] = [run_movie(movie, 30) for _ in range(3)]
    write(payload)
    print(RESULTS_PATH, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
