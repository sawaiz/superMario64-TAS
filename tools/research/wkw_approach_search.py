#!/usr/bin/env python3
"""Search WKW run-up, launch, and steering-window optimizations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import wkw_next_search as wkw
from speedup_search import BASE_MOVIE, BASE_STATE, ROM, run_movie

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "experiments/wall_kicks_approach_search"
CANDIDATE_DIR = OUTPUT_DIR / "candidates"
RESULTS_PATH = OUTPUT_DIR / "results.json"
INTERACTION_RESULTS_PATH = OUTPUT_DIR / "interaction-results.json"
RECOVERY_RESULTS_PATH = OUTPUT_DIR / "kick-recovery-results.json"

WINNER_X = 94
WINNER_Y = -104


def clamp(value: int) -> int:
    return max(-128, min(127, value))


def winner_edits(inputs: list[tuple[int, int, int]]) -> dict[int, tuple[int, int, int]]:
    return {
        sample: (inputs[sample][0], WINNER_X, WINNER_Y)
        for sample in range(149, 202)
    }


def change_stick(
    inputs: list[tuple[int, int, int]],
    edits: dict[int, tuple[int, int, int]],
    samples: range,
    *,
    dx: int = 0,
    dy: int = 0,
) -> None:
    for sample in samples:
        buttons, x, y = edits.get(sample, inputs[sample])
        edits[sample] = (buttons, clamp(x + dx), clamp(y + dy))


def move_button_bit(
    inputs: list[tuple[int, int, int]],
    edits: dict[int, tuple[int, int, int]],
    source: int,
    target: int,
    bit: int,
) -> None:
    source_value = edits.get(source, inputs[source])
    edits[source] = (source_value[0] & ~bit, source_value[1], source_value[2])
    target_value = edits.get(target, inputs[target])
    edits[target] = (target_value[0] | bit, target_value[1], target_value[2])


def candidates(inputs: list[tuple[int, int, int]]) -> list[tuple[str, dict]]:
    items: list[tuple[str, dict]] = []

    # Find whether the successful long steering edit can begin later or end at
    # a better phase boundary. This dimension was not covered by the value grid.
    for start in range(136, 161):
        if start == 149:
            continue
        edits = {
            sample: (inputs[sample][0], WINNER_X, WINNER_Y)
            for sample in range(start, 202)
        }
        items.append((f"window_start_{start}", edits))
    for end in range(186, 214):
        if end == 201:
            continue
        edits = {
            sample: (inputs[sample][0], WINNER_X, WINNER_Y)
            for sample in range(149, end + 1)
        }
        items.append((f"window_end_{end}", edits))

    # Perturb the carefully authored launch inputs without flattening them.
    # Additive edits preserve their changing direction while varying entry state.
    for dx, dy in ((-4, 0), (-2, 0), (2, 0), (4, 0), (0, -8), (0, -4), (0, 4), (0, 8)):
        edits = winner_edits(inputs)
        change_stick(inputs, edits, range(135, 149), dx=dx, dy=dy)
        items.append((f"launch_full_dx{dx:+d}_dy{dy:+d}", edits))
    for start in (137, 140, 143, 145, 147):
        for dx, dy in ((-2, 0), (2, 0), (0, -4), (0, 4)):
            edits = winner_edits(inputs)
            change_stick(inputs, edits, range(start, 149), dx=dx, dy=dy)
            items.append((f"launch_suffix_{start}_dx{dx:+d}_dy{dy:+d}", edits))

    # Change the two ground-acceleration blocks independently. Small analog
    # changes can alter the quarter-step collision state at the launch edge.
    for start, end, label in ((100, 106, "runup_1"), (106, 133, "runup_2")):
        for dx, dy in ((-4, 0), (-2, 0), (2, 0), (4, 0), (0, -3)):
            edits = winner_edits(inputs)
            change_stick(inputs, edits, range(start, end), dx=dx, dy=dy)
            items.append((f"{label}_dx{dx:+d}_dy{dy:+d}", edits))

    # B is 0x40 and A is 0x80 in the movie input word. Test first-possible-frame
    # kick timing and the launch jump separately, retaining all analog inputs.
    for source in (105, 119):
        for offset in (-1, 1):
            edits = winner_edits(inputs)
            move_button_bit(inputs, edits, source, source + offset, 0x40)
            items.append((f"kick_{source}_{offset:+d}", edits))
    for offset in (-1, 1):
        edits = winner_edits(inputs)
        move_button_bit(inputs, edits, 134, 134 + offset, 0x80)
        items.append((f"jump_134_{offset:+d}", edits))
    for first_offset in (-1, 1):
        for second_offset in (-1, 1):
            edits = winner_edits(inputs)
            move_button_bit(inputs, edits, 105, 105 + first_offset, 0x40)
            move_button_bit(inputs, edits, 119, 119 + second_offset, 0x40)
            items.append((f"kicks_{first_offset:+d}_{second_offset:+d}", edits))

    return items


def interaction_candidates(inputs: list[tuple[int, int, int]]) -> list[tuple[str, dict]]:
    """Cross delayed starts with the analog values that already tie VI 538/546."""
    items: list[tuple[str, dict]] = []
    neutral_starts = (150, 151, 153, 154, 155, 156)
    proven_points = (
        (94, -104), (112, -124), (118, -124), (90, -103), (91, -104),
        (93, -103), (97, -102), (98, -103), (109, -128), (109, -125),
        (110, -126), (110, -122), (111, -123), (115, -121), (116, -122),
        (117, -123), (119, -125), (120, -126),
    )
    for start in neutral_starts:
        for x, y in proven_points:
            edits = {
                sample: (inputs[sample][0], x, y)
                for sample in range(start, 202)
            }
            items.append((f"interaction_start_{start}_x{x}_y{y}", edits))

    # Cross the four neutral launch-suffix changes with delayed steering starts.
    for start in neutral_starts:
        for suffix_start in (145, 147):
            for dy in (-4, 4):
                edits = {
                    sample: (inputs[sample][0], WINNER_X, WINNER_Y)
                    for sample in range(start, 202)
                }
                change_stick(inputs, edits, range(suffix_start, 149), dy=dy)
                items.append(
                    (f"interaction_start_{start}_suffix_{suffix_start}_dy{dy:+d}", edits)
                )
    return items


def kick_recovery_candidates(inputs: list[tuple[int, int, int]]) -> list[tuple[str, dict]]:
    """Retune analog control around a one-sample-earlier final jump kick."""
    items: list[tuple[str, dict]] = []

    def early_kick(*, hold: bool = False) -> dict[int, tuple[int, int, int]]:
        edits = winner_edits(inputs)
        if hold:
            buttons, x, y = inputs[209]
            edits[209] = (buttons | 0x40, x, y)
        else:
            move_button_bit(inputs, edits, 210, 209, 0x40)
        return edits

    # Re-aim the approach into the kick. The original movie is near (127,-107)
    # here, so search a bounded speed/direction neighborhood.
    for x in (112, 120, 127):
        for y in (-128, -120, -112, -104, -96):
            edits = early_kick()
            for sample in range(202, 210):
                edits[sample] = (inputs[sample][0], x, y)
            items.append((f"early_kick_prekick_x{x}_y{y}", edits))

    # Re-aim the descent after the earlier kick. Search both a moved B press and
    # a one-sample B hold because they can enter different action substates.
    for hold, label in ((False, "move"), (True, "hold")):
        for x in (-16, -8, 0, 8, 16):
            for y in (-128, -124, -120, -112):
                edits = early_kick(hold=hold)
                for sample in range(210, 225):
                    edits[sample] = (edits.get(sample, inputs[sample])[0], x, y)
                items.append((f"early_kick_{label}_tail_x{x}_y{y}", edits))

    # Sample 213 contains the next discrete transition and a sharp stick flip.
    # Tune that single launch input while leaving the successful descent intact.
    for x in (-16, -8, 0, 8, 16):
        for y in (120, 124, 127):
            edits = early_kick()
            edits[213] = (inputs[213][0], x, y)
            items.append((f"early_kick_transition_x{x}_y{y}", edits))
    return items


def classify(result: dict, seed: dict) -> str:
    touch = result.get("star_touch_vi")
    exit_vi = result.get("star_exit_vi")
    if touch is None:
        return "rejected: star not reached"
    if touch < seed["star_touch_vi"] and exit_vi is not None and exit_vi < seed["star_exit_vi"]:
        return "improved touch and exit"
    if touch < seed["star_touch_vi"]:
        return "improved touch"
    if touch == seed["star_touch_vi"] and exit_vi is not None and exit_vi < seed["star_exit_vi"]:
        return "improved exit"
    if touch == seed["star_touch_vi"] and exit_vi == seed["star_exit_vi"]:
        return "ties verified seed"
    return "slower"


def write(payload: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    global RESULTS_PATH
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=25.0)
    parser.add_argument("--retry-errors", action="store_true")
    parser.add_argument("--interaction-only", action="store_true")
    parser.add_argument("--kick-recovery-only", action="store_true")
    args = parser.parse_args()

    for path in (BASE_MOVIE, BASE_STATE, ROM):
        if not path.is_file():
            raise FileNotFoundError(path)

    wkw.CANDIDATE_DIR = CANDIDATE_DIR
    inputs = wkw.unpack_inputs(BASE_MOVIE.read_bytes())
    if args.kick_recovery_only:
        RESULTS_PATH = RECOVERY_RESULTS_PATH
        all_candidates = kick_recovery_candidates(inputs)
    elif args.interaction_only:
        RESULTS_PATH = INTERACTION_RESULTS_PATH
        all_candidates = interaction_candidates(inputs)
    else:
        all_candidates = candidates(inputs)
    edits_by_name = dict(all_candidates)

    if args.retry_errors:
        payload = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
        pending = [item for item in payload["candidates"] if item["result"].startswith("error:")]
        for index, item in enumerate(pending, 1):
            name = item["candidate"]
            print(f"[retry {index}/{len(pending)}] {name}", flush=True)
            replacement = {"candidate": name, "edit_count": len(edits_by_name[name])}
            replacement.update(run_movie(wkw.make_candidate(name, edits_by_name[name]), args.timeout))
            replacement["result"] = classify(replacement, payload["seed"])
            item.clear()
            item.update(replacement)
            print(f"  {item['result']}; touch={item.get('star_touch_vi')} exit={item.get('star_exit_vi')}", flush=True)
            write(payload)
        return 0

    baseline = run_movie(BASE_MOVIE, 30)
    seed_movie = wkw.make_candidate("verified_x94_y-104", winner_edits(inputs))
    seed = run_movie(seed_movie, 30)
    payload = {"baseline": baseline, "seed": seed, "candidates": []}
    write(payload)
    print(
        f"Seed: touch={seed['star_touch_vi']} exit={seed['star_exit_vi']}; "
        f"testing {len(all_candidates)} candidates",
        flush=True,
    )

    for index, (name, edits) in enumerate(all_candidates, 1):
        print(f"[{index}/{len(all_candidates)}] {name}", flush=True)
        item = {"candidate": name, "edit_count": len(edits)}
        try:
            item.update(run_movie(wkw.make_candidate(name, edits), args.timeout))
            item["result"] = classify(item, seed)
        except Exception as exc:
            item.update({"reached_star": False, "result": f"error: {exc}"})
        payload["candidates"].append(item)
        print(
            f"  {item['result']}; touch={item.get('star_touch_vi')} "
            f"exit={item.get('star_exit_vi')}",
            flush=True,
        )
        write(payload)

    improvements = [item for item in payload["candidates"] if item["result"].startswith("improved")]
    ties = [item for item in payload["candidates"] if item["result"] == "ties verified seed"]
    print(f"Complete: {len(improvements)} improvements, {len(ties)} ties", flush=True)
    print(RESULTS_PATH, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
