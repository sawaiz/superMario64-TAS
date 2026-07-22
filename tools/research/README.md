# Rules-safe TAS research tools

Python 3, stdlib only. Constants taken from **n64decomp/sm64** matching sources.

| Script | Purpose |
|--------|---------|
| `constants.py` | Shared engine constants |
| `pu_nav.py` | Parallel universe / QPU lattice |
| `air_physics.py` | Airborne + BLJ speed envelopes |
| `wall_punch.py` | Punch probe + 1 Key clock-punch table |
| `speedup_search.py` | CLI Mupen search over selected one-sample deletions |
| `speedup_retime.py` | CLI Mupen search over final-approach input retiming |
| `wkw_next_search.py` | Expanded WKW route, textbox, air-control, and final-approach search |
| `wkw_landing_search.py` | Layered WKW landing-recovery search on the first early-touch seed |
| `wkw_touch_search.py` | Coarse/fine analog grid and deterministic winner verification |
| `plot_speedup_results.py` | Rebuild experiment graphs from result JSON |
| `squish_scan.md` | Squish cancel conditions checklist |

```bash
python3 pu_nav.py pos 65536 0 0
python3 air_physics.py blj --start -16 --jumps 10
python3 wall_punch.py clock-table
```

Findings write-up: `../../notes/research/high-value-tas.md`

## Experiment verification

```bash
python verify_experiment.py tiers
python verify_experiment.py formula blj --start -20 --jumps 6
python check_log.py ../../logs/run_us_....csv --require-frames 100
python speedup_search.py
python speedup_retime.py
python wkw_next_search.py --stages route textbox air final
python wkw_next_search.py --stages verify --verify-runs 3
python wkw_landing_search.py
python wkw_touch_search.py
python wkw_touch_search.py --refine-only
python plot_speedup_results.py
```

### Windows in-emu harness

```text
tools/research/harness/tas_harness.lua   # drag onto Mupen after ROM load
tools/research/harness/harness_config.example.lua
```

Full Windows loop: [../../notes/windows-setup.md](../../notes/windows-setup.md)

| Tier | What | Automated? |
|------|------|------------|
| A | Formula sims | Yes (`*.py`) |
| B | Mupen + Lua CSV log | Harness + manual ROM/movie |
| C | Real N64 | Hardware |
