#!/usr/bin/env python3
"""Generate result graphs for the Wall Kicks Will Work speedup experiments."""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENTS = [
    (
        ROOT / "experiments/wall_kicks_frame_delete/results.json",
        ROOT / "experiments/wall_kicks_frame_delete/results.png",
        "One-sample deletion search",
        "deleted_sample",
    ),
    (
        ROOT / "experiments/wall_kicks_retime/results.json",
        ROOT / "experiments/wall_kicks_retime/results.png",
        "Final-approach input-retiming search",
        "candidate",
    ),
]
COLORS = {
    "potential speedup": "#2ca02c",
    "tie: no VI saved": "#1f77b4",
    "slower": "#ff7f0e",
    "rejected: star not reached": "#d62728",
}


def endpoint_distance(candidate: dict, baseline: dict) -> float | None:
    fields = ("end_x", "end_y", "end_z")
    if any(candidate.get(field) is None for field in fields):
        return None
    return math.sqrt(
        sum((float(candidate[field]) - float(baseline[field])) ** 2 for field in fields)
    )


def plot_experiment(source: Path, destination: Path, title: str, label_key: str) -> None:
    payload = json.loads(source.read_text(encoding="utf-8"))
    baseline = payload["baseline"]
    candidates = payload["candidates"]
    labels = [str(candidate[label_key]) for candidate in candidates]
    indexes = list(range(len(candidates)))

    plt.style.use("seaborn-v0_8-whitegrid")
    figure, (timing_axis, distance_axis) = plt.subplots(
        2,
        1,
        figsize=(13, 8),
        sharex=True,
        gridspec_kw={"height_ratios": [3, 2]},
    )
    figure.suptitle(f"SM64 WKW: {title}", fontsize=17, fontweight="bold")

    baseline_vi = int(baseline["star_vi"])
    timing_axis.axhline(
        baseline_vi,
        color="#222222",
        linewidth=1.5,
        linestyle="--",
        label=f"baseline star VI = {baseline_vi}",
    )
    for index, candidate in zip(indexes, candidates):
        result = candidate["result"]
        color = COLORS.get(result, "#7f7f7f")
        if candidate.get("reached_star"):
            timing_axis.scatter(
                index,
                candidate["star_vi"],
                color=color,
                s=90,
                zorder=3,
                edgecolor="white",
                linewidth=0.8,
            )
        else:
            timing_axis.scatter(
                index,
                baseline_vi + 2,
                color=color,
                marker="x",
                s=90,
                linewidth=2.2,
                zorder=3,
            )
    timing_axis.set_ylabel("Star-completion VI")
    timing_axis.set_ylim(baseline_vi - 2.5, baseline_vi + 3.5)
    timing_axis.legend(loc="lower right")
    timing_axis.text(
        0.01,
        0.93,
        "red x = route failed to reach the star",
        transform=timing_axis.transAxes,
        color=COLORS["rejected: star not reached"],
        fontsize=10,
        va="top",
    )

    distances = [endpoint_distance(candidate, baseline) for candidate in candidates]
    bar_colors = [COLORS.get(candidate["result"], "#7f7f7f") for candidate in candidates]
    distance_axis.bar(
        indexes,
        [distance if distance is not None else 0 for distance in distances],
        color=bar_colors,
        width=0.72,
    )
    distance_axis.set_ylabel("Final-state distance\nfrom baseline (units)")
    distance_axis.set_xlabel("Candidate mutation")
    distance_axis.set_yscale("symlog", linthresh=1)
    distance_axis.set_xticks(indexes, labels, rotation=38, ha="right")

    figure.text(
        0.5,
        0.015,
        "A speedup must reach ACT_STAR_DANCE_EXIT before baseline VI 546.",
        ha="center",
        fontsize=10,
        color="#444444",
    )
    figure.tight_layout(rect=(0, 0.055, 1, 0.95))
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(destination, dpi=180, bbox_inches="tight")
    plt.close(figure)
    print(destination)


def plot_next_search() -> None:
    source = ROOT / "experiments/wall_kicks_next_search/results.json"
    output = source.parent
    payload = json.loads(source.read_text(encoding="utf-8"))
    baseline = payload["baseline"]
    candidates = payload["candidates"]
    stages = ("route", "textbox", "air", "final")
    stage_colors = {
        "route": "#7c3aed",
        "textbox": "#0284c7",
        "air": "#16a34a",
        "final": "#ea580c",
    }

    plt.style.use("seaborn-v0_8-whitegrid")
    figure, (timing, outcomes) = plt.subplots(
        2, 1, figsize=(14, 8), gridspec_kw={"height_ratios": [3, 2]}
    )
    figure.suptitle(
        "Wall Kicks Will Work: automated search results",
        fontsize=18,
        fontweight="bold",
    )
    timing.axhline(
        baseline["star_touch_vi"], color="#111827", linestyle="--", linewidth=1.5,
        label=f"baseline touch: VI {baseline['star_touch_vi']}",
    )
    for index, candidate in enumerate(candidates):
        vi = candidate.get("star_touch_vi")
        if vi is None:
            timing.scatter(index, 542, marker="x", color="#dc2626", s=38)
        else:
            timing.scatter(
                index, vi, color=stage_colors[candidate["stage"]], s=45,
                edgecolor="white", linewidth=.5,
            )
    timing.set_ylim(536.5, 543)
    timing.set_ylabel("Star-touch video interrupt (VI)\nlower is earlier")
    timing.set_xticks([])
    timing.legend(loc="lower left")
    timing.text(
        .99, .08, "8 air-control variants touch at VI 538 (2 VI earlier)",
        transform=timing.transAxes, ha="right", color="#166534", fontweight="bold",
    )
    timing.text(
        .99, .92, "red × = star not reached", transform=timing.transAxes,
        ha="right", va="top", color="#b91c1c",
    )

    categories = ("potential speedup", "tie: no VI saved", "rejected: star not reached")
    category_colors = ("#16a34a", "#2563eb", "#dc2626")
    bottoms = [0] * len(stages)
    for category, color in zip(categories, category_colors):
        values = [
            sum(c["stage"] == stage and c["result"] == category for c in candidates)
            for stage in stages
        ]
        outcomes.bar(stages, values, bottom=bottoms, color=color, label=category)
        for index, (value, bottom) in enumerate(zip(values, bottoms)):
            if value:
                outcomes.text(index, bottom + value / 2, str(value), ha="center", va="center",
                              color="white", fontweight="bold")
        bottoms = [bottom + value for bottom, value in zip(bottoms, values)]
    outcomes.set_ylabel("Candidates")
    outcomes.set_xlabel("Search family")
    outcomes.legend(ncol=3, loc="upper center", bbox_to_anchor=(.5, -0.17))
    figure.text(
        .5, .012,
        "Touch improved from VI 540 to 538; the same candidates exit the star sequence at VI 548 instead of 546.",
        ha="center", fontsize=10, color="#374151",
    )
    figure.tight_layout(rect=(0, .06, 1, .94))
    figure.savefig(output / "results.png", dpi=180, bbox_inches="tight")
    plt.close(figure)

    best = next(c for c in candidates if c["candidate"] == "air_full_x100_y-128")
    figure, axis = plt.subplots(figsize=(13, 6.5))
    axis.set_xlim(0, 13)
    axis.set_ylim(0, 7)
    axis.axis("off")
    figure.patch.set_facecolor("#0b1020")
    axis.set_facecolor("#0b1020")
    axis.text(.4, 6.55, "EMULATOR TELEMETRY SNAPSHOT", color="#93c5fd", fontsize=11,
              fontweight="bold")
    axis.text(.4, 6.08, "One tiny stick change reaches the star one game update earlier",
              color="white", fontsize=20, fontweight="bold")

    def card(x: float, title: str, data: dict, accent: str) -> None:
        axis.add_patch(FancyBboxPatch(
            (x, 1.15), 5.85, 4.35, boxstyle="round,pad=0.16,rounding_size=.12",
            facecolor="#151d31", edgecolor=accent, linewidth=2,
        ))
        axis.text(x + .3, 5.05, title, color=accent, fontsize=16, fontweight="bold")
        lines = [
            ("First walking", f"sample {data['first_walking_sample']}  ·  VI {data['first_walking_vi']}"),
            ("Jump", f"sample {data['first_jump_sample']}  ·  VI {data['first_jump_vi']}"),
            ("Star touch", f"sample {data['star_touch_sample']}  ·  VI {data['star_touch_vi']}"),
            ("Star-sequence exit", f"sample {data['star_exit_sample']}  ·  VI {data['star_exit_vi']}"),
            ("Parity hash", data['parity_hash']),
        ]
        y = 4.47
        for label, value in lines:
            axis.text(x + .3, y, label.upper(), color="#94a3b8", fontsize=9)
            axis.text(x + 2.25, y, value, color="white", fontsize=11, fontfamily="monospace")
            y -= .7

    card(.4, "Baseline  (stick 98, −128)", baseline, "#60a5fa")
    card(6.75, "Candidate  (stick 100, −128)", best, "#4ade80")
    axis.text(.4, .55,
              "Result: touch −2 VI / −1 input sample  •  exit +2 VI / +1 input sample  •  verified 3/3 identical",
              color="#e2e8f0", fontsize=12, fontweight="bold")
    figure.savefig(output / "telemetry-snapshot.png", dpi=180, bbox_inches="tight",
                   facecolor=figure.get_facecolor())
    plt.close(figure)
    print(output / "results.png")
    print(output / "telemetry-snapshot.png")


def main() -> int:
    for source, destination, title, label_key in EXPERIMENTS:
        plot_experiment(source, destination, title, label_key)
    plot_next_search()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
