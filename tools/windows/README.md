# Windows automation scripts

| Script | Purpose |
|--------|---------|
| `setup.ps1` | Download Mupen/STROOP, create folders, local config |
| `run_mupen.ps1` | Launch Mupen from this repo |
| `run_loop.ps1` | Print full-loop steps; optional Mupen start; `-CheckOnly` for logs |
| `smoke_test.ps1` | Automated short ROM + movie + Lua + CSV parity test |
| `config.example.json` | Template (copy becomes `config.local.json`, gitignored) |

**Full documentation:** [../../notes/windows-setup.md](../../notes/windows-setup.md)

```powershell
powershell -ExecutionPolicy Bypass -File tools\windows\setup.ps1
powershell -File tools\windows\run_mupen.ps1
powershell -File tools\windows\run_loop.ps1
powershell -File tools\windows\run_loop.ps1 -CheckOnly
powershell -File tools\windows\smoke_test.ps1
```
