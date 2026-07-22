# State-aware beam search for Wall Kicks Will Work

## What this does

A full emulator is accurate but slow: every input candidate has to boot the same
movie, replay it, and wait for the result. This experiment uses a small C++
physics model as a fast filter. It explores many analog-stick sequences, keeps a
diverse beam of promising Mario states, and sends only the shortlist to Mupen64.

The C++ result is **never accepted as a speedup by itself**. Mupen remains the
authority for collision, action transitions, star collection timing, and the
determinism/parity hash.

## Design

1. Run a verified seed movie in Mupen and log position, velocity, facing yaw,
   camera yaw, intended input, action state/timer, floor, ceiling, wall, and goal
   distance.
2. Reproduce the seed with SM64's stick and airborne formulas.
3. Apply the emulator-measured residual at every step. This differential model
   reproduces the seed with zero measured drift while cheaply estimating nearby
   inputs.
4. Quantize position and speed into state buckets, retaining the best path in
   each bucket instead of many nearly identical candidates.
5. Write the best paths as `.m64` movies and validate every shortlisted movie in
   Mupen.

This is deliberately a hybrid rather than a replacement emulator. A standalone
simulation would also need exact triangle collision, action code, object updates,
camera-dependent input, N64 floating-point behavior, and VI scheduling. A small
mistake in any of those can make a predicted frame save false.

## Results

The verified seed touches the star at **VI 538** and exits the collection at
**VI 546**.

| Search window | Beam | C++ time | Mupen shortlist | Result |
|---|---:|---:|---:|---|
| Samples 156-201, across wall contact | 2,500 | 4.574 s | 24 in 124.517 s | 0 faster, 19 slower, 5 misses |
| Samples 214-221, after wall contact | 5,000 | 0.236 s | 24 in 125.936 s | 0 faster, 24 exact timing ties |

The first pass exposed the important accuracy boundary: sub-unit changes before
the wall contact selected a different collision branch, so a smooth differential
prediction could not reliably rank the later trajectory. The second pass kept
the verified collision branch and optimized only the post-contact inputs. Its 24
shortlisted paths all collected the star at the seed's VI 538/546 timing, with no
misses or parity errors.

The corrected post-contact predictions put Mario about 14.1-15.6 horizontal
units from the final target at sample 222, but none moved collection to an earlier
game update. This means the tested post-contact window has positional slack, not
a demonstrated frame of timing slack. The measured potential speedup from these
two searches is therefore **0 VI**.

The performance case for the hybrid is still strong: ranking the post-contact
beam took 0.236 seconds, while authoritative validation of just 24 movies took
125.936 seconds (about 5.25 seconds per movie). Simulator ranking was roughly
534 times shorter than validating that small shortlist, before accounting for
the much larger set of paths pruned inside the beam.

Raw machine-readable records are in [results.json](results.json) and
[postcontact-results.json](postcontact-results.json).

## Reproduce

From the repository root on the configured Windows setup:

```powershell
python tools\research\wkw_beam_search.py `
  --beam-width 5000 --shortlist 24 --validate 24 `
  --start-sample 214 --end-sample 221 `
  --goal-sample 222 --target-sample 224 `
  --results-name postcontact-results.json
```

The runner compiles `tools/research/beam/wkw_beam_sim.cpp`, creates the seed,
captures fresh telemetry, performs the C++ search, and validates the shortlist.
ROMs, generated movies, savestates, emulator binaries, and telemetry logs remain
local and are excluded from Git.

## Next useful extension

Treat collision as a discrete branch instead of predicting through it. The
practical version is a segmented beam: stop at each floor/wall/action change,
ask Mupen to validate representative states at that frontier, then calibrate a
new differential segment from each surviving branch. That retains emulator
truth at discontinuities while letting C++ do the large continuous searches
between them.
