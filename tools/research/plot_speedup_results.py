#!/usr/bin/env python3
"""Generate result graphs for the Wall Kicks Will Work speedup experiments."""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

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


def main() -> int:
    for source, destination, title, label_key in EXPERIMENTS:
        plot_experiment(source, destination, title, label_key)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
