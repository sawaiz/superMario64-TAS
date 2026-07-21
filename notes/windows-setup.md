# Windows setup — full TAS automation loop

**Primary environment for closed-loop experiments.**  
Mac/Whisky is optional for casual use only.

**Hard rule:** [console-first.md](console-first.md) — Mupen proves sync and collects data; **real N64** is acceptance.

---

## What you get

| Path | Role |
|------|------|
| `tools/windows/setup.ps1` | Install Mupen + STROOP, create folders |
| `tools/windows/run_mupen.ps1` | Launch Mupen from repo |
| `tools/windows/run_loop.ps1` | Guided loop + log check |
| `tools/research/harness/tas_harness.lua` | Per-frame CSV logger (Lua) |
| `tools/research/check_log.py` | Assert / summarize harness logs |
| `tools/research/*.py` | Offline formula sims (PU, BLJ, …) |
| `logs/` | Harness output (gitignored) |

---

## One-time setup (Windows 10/11)

### Requirements

- Windows 10/11 **x64**
- **Git**
- **Python 3.10+** on PATH (`python --version`)
- Optional: **.NET Framework 4.6.1+** for STROOP
- Legal **Super Mario 64** dumps (USA and/or Japan)

### Clone and setup

```powershell
git clone git@github.com:sawaiz/superMario64-TAS.git
cd superMario64-TAS

# Allow local scripts if needed
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

powershell -ExecutionPolicy Bypass -File tools\windows\setup.ps1
```

`setup.ps1` will:

1. Create `roms\`, `logs\`
2. Download **Mupen64** stable repack → `tools\mupen64\repack-stable-main\stable\`
3. Download **STROOP** (optional, large) → `tools\STROOP\`
4. Copy `harness_config.example.lua` → `harness_config.lua`
5. Write `tools\windows\config.local.json` (gitignored)

### Place ROMs (never commit)

```text
roms\Super Mario 64 (USA).z64
roms\Super Mario 64 (Japan).z64   # for classic 1-key TAS
```

| Region | MD5 (big-endian .z64) |
|--------|------------------------|
| USA | `20b854b239203baf6c961b850a4a51a2` |
| Japan | `85d61f5525af708c9f1e84dce6dc10e9` |

Copy the same files into:

```text
tools\mupen64\repack-stable-main\stable\roms\
```

(`setup.ps1` / `run_mupen.ps1` also stage USA if found under `roms\`.)

---

## Daily: start Mupen

```powershell
powershell -File tools\windows\run_mupen.ps1
```

Or double-click `tools\mupen64\repack-stable-main\stable\mupen64.exe`.

---

## Full experiment loop

### A. Offline formula check (no emu)

```powershell
cd tools\research
python verify_experiment.py formula blj --start -20 --jumps 8
python verify_experiment.py formula pu --x 40000 --z 0 --speed 262144
python air_physics.py longjump --speed -48
```

### B. In-emulator log (harness)

1. Start Mupen, **load ROM** (US or JP matching your movie).
2. Drag onto Mupen:

   ```text
   tools\research\harness\tas_harness.lua
   ```

3. Optional: edit `tools\research\harness\harness_config.lua`:

   ```lua
   return {
     region = "us",  -- or "jp"
     log_every = 1,
     max_frames = 0,
     -- movie_path = [[C:\full\path\to\movie.m64]],
   }
   ```

4. **Movie → Play** a `.m64` from `tas\`  
   - USA ILs / 120 archive → USA ROM  
   - Classic 1-key → **Japan** ROM  

5. When finished, stop movie / close Lua.  
   Logs: `logs\run_<region>_<timestamp>.csv`

### C. Check log

```powershell
powershell -File tools\windows\run_loop.ps1 -CheckOnly

# or explicitly:
python tools\research\check_log.py logs\run_us_YYYYMMDD_HHMMSS.csv --require-frames 100
python tools\research\check_log.py logs\run_us_....csv --min-speed -50
```

### D. Guided loop (prints steps + optional Mupen launch)

```powershell
powershell -File tools\windows\run_loop.ps1
```

### E. Console acceptance

Before calling a TAS “done”:

- [ ] Console-safety checklist in [console-first.md](console-first.md)  
- [ ] No emu-only PU TRUNC abuse  
- [ ] Fixed cam + R for PU segments  
- [ ] Prefer console lag over pure Mupen frame count  

---

## STROOP (optional, powerful)

1. Run `tools\STROOP\net461\STROOP.exe`
2. Start Mupen with ROM loaded
3. STROOP → connect to Mupen process  
4. Watch Mario / objects / triangles while harness logs

---

## Movie catalog (local)

| Content | Path |
|---------|------|
| 1 Key (published) | `tas\full-game\1-key\` |
| 120 / 70 / 16 | `tas\full-game\` |
| Archive ILs | `tas\archive\SM64TASArchive\` |

Refresh:

```powershell
# Git Bash or WSL, or re-clone archive:
bash tools/scripts/download_tases.sh
```

On pure Windows without bash, re-download TASVideos files manually from links in `notes\tas-catalog.md`.

---

## Recommended Windows layout

```text
C:\dev\superMario64-TAS\          (git clone)
  roms\                           YOUR dumps only
  logs\                           harness CSV (gitignored)
  tools\mupen64\...\mupen64.exe
  tools\STROOP\net461\STROOP.exe
  tools\research\harness\
  tas\
  notes\
```

Pin `run_mupen.ps1` to taskbar / Start if useful.

---

## Plugin / sync notes

- Keep **one** Mupen repack; don’t mix plugins mid-movie.  
- Document Mupen version for collaborators.  
- Same region ROM as movie header.  
- Fast-forward is OK for logging if you only care about state series; for lag studies use real-time / known speed.

---

## What is / isn’t automated on Windows

| Step | Automated? |
|------|------------|
| Download tools | `setup.ps1` |
| Launch Mupen | `run_mupen.ps1` |
| Load ROM | Manual (double-click in browser) |
| Load Lua harness | Manual drag-drop (once per session) |
| Play movie | Manual or `movie_path` in harness config |
| Log RAM each frame | **Automatic** (harness) |
| Assert CSV | `check_log.py` / `run_loop.ps1 -CheckOnly` |
| Console verify | Hardware / TASbot |

Fully headless “CI exits 0 without GUI” is possible later with more work; this stack is the **practical SM64 TAS full loop** used by the community.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Mupen missing | `setup.ps1` again |
| Movie desync | Wrong region ROM; wrong plugins |
| Log empty | ROM not loaded before harness; or addresses wrong region |
| JP addresses look wrong | Confirm with STROOP; set `region = "jp"` in harness config |
| Python not found | Install from python.org, tick “Add to PATH” |
| Execution policy | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |

---

## Related docs

- [console-first.md](console-first.md)  
- [rules-and-decomp.md](rules-and-decomp.md)  
- [research/high-value-tas.md](research/high-value-tas.md)  
- [emulators-and-tools.md](emulators-and-tools.md)  
