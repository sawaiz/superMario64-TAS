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
python3 verify_experiment.py tiers
python3 verify_experiment.py formula blj --start -20 --jumps 6
python3 verify_experiment.py formula pu --x 40000 --z 0 --speed 262144
python3 verify_experiment.py m64 ../../tas/full-game/1-key/*.m64
python3 verify_experiment.py play --movie ../../tas/full-game/from-archive/120-stars-01h20m41s52ms-U.m64 --launch
```

| Tier | What | Automated here? |
|------|------|-----------------|
| A | Decomp formula sims | Yes |
| B | Mupen GUI movie play | Launch + you watch |
| C | Real N64 | Hardware / TASbot |
