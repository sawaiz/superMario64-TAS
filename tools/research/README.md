# Rules-safe TAS research tools

Python 3, stdlib only. Constants taken from **n64decomp/sm64** matching sources.

| Script | Purpose |
|--------|---------|
| `constants.py` | Shared engine constants |
| `pu_nav.py` | Parallel universe / QPU lattice |
| `air_physics.py` | Airborne + BLJ speed envelopes |
| `wall_punch.py` | Punch probe + 1 Key clock-punch table |
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
