#!/usr/bin/env python3
"""Generate the WKW approach-search outcome, interaction, and route visuals."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "experiments/wall_kicks_approach_search"

BATCHES = (
    ("Approach + boundaries", "results.json"),
    ("Timing x analog", "interaction-results.json"),
    ("Earlier-kick recovery", "kick-recovery-results.json"),
)
CATEGORIES = (
    ("ties verified seed", "Tied VI 538 / 546", "#16803a"),
    ("slower", "Slower", "#e89019"),
    ("rejected: star not reached", "Missed star", "#c93b43"),
)


def load(name: str) -> dict:
    return json.loads((OUTPUT / name).read_text(encoding="utf-8"))


def plot_outcomes(payloads: list[dict]) -> None:
    labels = [label for label, _ in BATCHES] + ["All new tests"]
    counts = [Counter(item["result"] for item in payload["candidates"]) for payload in payloads]
    counts.append(sum(counts, Counter()))

    plt.style.use("seaborn-v0_8-whitegrid")
    figure, axis = plt.subplots(figsize=(13.5, 6.5))
    axis.set_title("301 additional WKW tests: no result beats VI 538 / 546", pad=18,
                   fontsize=18, fontweight="bold")
    left = [0] * len(labels)
    for key, display, color in CATEGORIES:
        values = [count[key] for count in counts]
        bars = axis.barh(labels, values, left=left, color=color, label=display, height=.58)
        for bar, value in zip(bars, values):
            if value:
                axis.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_y() + bar.get_height() / 2,
                    str(value),
                    ha="center",
                    va="center",
                    color="white",
                    fontweight="bold",
                    fontsize=11,
                )
        left = [start + value for start, value in zip(left, values)]

    totals = [sum(count.values()) for count in counts]
    for index, total in enumerate(totals):
        axis.text(total + 3, index, f"{total} tested", va="center", color="#374151")
    axis.set_xlim(0, max(totals) * 1.14)
    axis.set_xlabel("Candidate movies replayed from the same savestate")
    axis.invert_yaxis()
    axis.legend(loc="lower center", bbox_to_anchor=(.5, -0.22), ncol=3, frameon=False)
    axis.text(
        .98, .97,
        "Best observed: star touch VI 538, grounded exit VI 546 (94 candidates)",
        transform=axis.transAxes, ha="right", va="top", color="#166534",
        fontweight="bold",
    )
    figure.tight_layout(rect=(0, .08, 1, 1))
    figure.savefig(OUTPUT / "outcome-summary.png", dpi=190, bbox_inches="tight")
    plt.close(figure)


def plot_interactions(payload: dict) -> None:
    pattern = re.compile(r"interaction_start_(\d+)_x(-?\d+)_y(-?\d+)")
    records = {}
    for item in payload["candidates"]:
        match = pattern.fullmatch(item["candidate"])
        if match:
            records[(int(match.group(1)), int(match.group(2)), int(match.group(3)))] = item

    starts = [150, 151, 153, 154, 155, 156]
    points = [
        (94, -104), (112, -124), (118, -124), (90, -103), (91, -104),
        (93, -103), (97, -102), (98, -103), (109, -128), (109, -125),
        (110, -126), (110, -122), (111, -123), (115, -121), (116, -122),
        (117, -123), (119, -125), (120, -126),
    ]
    codes = {
        "ties verified seed": 0,
        "slower": 1,
        "rejected: star not reached": 2,
    }
    matrix = [
        [codes[records[(start, x, y)]["result"]] for x, y in points]
        for start in starts
    ]

    figure, axis = plt.subplots(figsize=(15, 5.8))
    cmap = ListedColormap(["#16803a", "#e89019", "#c93b43"])
    norm = BoundaryNorm([-.5, .5, 1.5, 2.5], cmap.N)
    axis.imshow(matrix, cmap=cmap, norm=norm, aspect="auto")
    axis.set_title("Delayed steering start changes which analog solutions survive",
                   pad=16, fontsize=18, fontweight="bold")
    axis.set_xlabel("Previously successful stick setting (X / Y)")
    axis.set_ylabel("First modified input sample")
    axis.set_xticks(range(len(points)), [f"{x}\n{y}" for x, y in points])
    axis.set_yticks(range(len(starts)), starts)
    for row, start in enumerate(starts):
        for column, point in enumerate(points):
            result = records[(start, *point)]["result"]
            symbol = "=" if result == "ties verified seed" else ("+" if result == "slower" else "x")
            axis.text(column, row, symbol, ha="center", va="center", color="white",
                      fontweight="bold", fontsize=11)
    axis.legend(
        handles=[
            Patch(facecolor=color, label=f"{symbol}  {display}")
            for (_, display, color), symbol in zip(CATEGORIES, ("=", "+", "x"))
        ],
        loc="lower center", bbox_to_anchor=(.5, -0.29), ncol=3, frameon=False,
    )
    figure.text(
        .5, .015,
        "No timing/value interaction reached VI 536; the viable region is fragmented into collision bins.",
        ha="center", color="#374151",
    )
    figure.tight_layout(rect=(0, .12, 1, 1))
    figure.savefig(OUTPUT / "interaction-map.png", dpi=190, bbox_inches="tight")
    plt.close(figure)


def plot_route_constraints() -> None:
    figure, axis = plt.subplots(figsize=(14, 4.8))
    axis.set_xlim(132, 232)
    axis.set_ylim(0, 4)
    axis.set_yticks([])
    axis.set_xlabel("Controller input sample")
    axis.set_title("What the new search says about the final route segment",
                   pad=16, fontsize=18, fontweight="bold")
    axis.axvspan(135, 148, ymin=.48, ymax=.72, color="#7c3aed", alpha=.78)
    axis.text(141.5, 2.48, "Authored launch\nchanges usually miss", ha="center", va="center",
              color="white", fontweight="bold")
    axis.axvspan(149, 201, ymin=.18, ymax=.42, color="#94a3b8", alpha=.5)
    axis.axvspan(156, 201, ymin=.18, ymax=.42, color="#16803a", alpha=.9)
    axis.text(178.5, 1.2, "Smallest equivalent steering window: 156-201",
              ha="center", va="center", color="white", fontweight="bold")
    axis.axvline(201, color="#111827", linewidth=2.2)
    axis.text(201, .45, "hard end", ha="center", va="bottom", fontweight="bold")
    for sample, label, color, text_x, text_y, horizontal, vertical in (
        (210, "final kick\ncan't move early", "#c93b43", 209.5, 2.98, "right", "top"),
        (213, "transition", "#2563eb", 213.5, 3.62, "left", "bottom"),
        (224, "star touch\nVI 538", "#16803a", 223.5, 2.98, "right", "top"),
        (228, "grounded exit\nVI 546", "#16803a", 228.5, 3.62, "left", "bottom"),
    ):
        axis.scatter(sample, 3.28, s=120, color=color, edgecolor="white", linewidth=1.2, zorder=3)
        axis.text(text_x, text_y, label, ha=horizontal, va=vertical, fontsize=10)
    axis.grid(axis="x", alpha=.25)
    for side in ("left", "right", "top"):
        axis.spines[side].set_visible(False)
    figure.tight_layout()
    figure.savefig(OUTPUT / "route-constraints.png", dpi=190, bbox_inches="tight")
    plt.close(figure)


def main() -> int:
    payloads = [load(name) for _, name in BATCHES]
    all_candidates = [item for payload in payloads for item in payload["candidates"]]
    if len(all_candidates) != 301:
        raise RuntimeError(f"expected 301 candidates, found {len(all_candidates)}")
    if any(item["result"].startswith("error:") for item in all_candidates):
        raise RuntimeError("results still contain emulator errors")
    if Counter(item["result"] for item in all_candidates) != Counter({
        "ties verified seed": 94,
        "slower": 60,
        "rejected: star not reached": 147,
    }):
        raise RuntimeError("aggregate outcome totals changed")
    plot_outcomes(payloads)
    plot_interactions(payloads[1])
    plot_route_constraints()
    print(OUTPUT / "outcome-summary.png")
    print(OUTPUT / "interaction-map.png")
    print(OUTPUT / "route-constraints.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
