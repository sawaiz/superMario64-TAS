# Tools

## Downloaded on this machine (gitignored binaries)

| Tool | Path | Re-download |
|------|------|-------------|
| Mupen64 stable | `mupen64/repack-stable-main/stable/mupen64.exe` | `./scripts/download_tools.sh` |
| STROOP | `STROOP/net461/STROOP.exe` | same |
| SM64 Lua Redux | bundled under Mupen `stable/SM64LuaRedux/` | same |

These Windows binaries are **not** committed (see root `.gitignore`). Scripts re-fetch them.

## macOS

- `scripts/run_mupen_mac.sh` — tries Wine / guides Whisky / VM
- Optional: `brew install ares-emulator` for multi-system play (**not** for `.m64` TAS)
- Optional: `brew install mupen64plus` — different from Mupen64-rr; not the TAS standard
