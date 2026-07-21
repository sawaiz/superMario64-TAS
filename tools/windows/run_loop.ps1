#Requires -Version 5.1
<#
.SYNOPSIS
  Windows full-loop helper: open Mupen, print harness steps, optionally check latest log.

.PARAMETER CheckOnly
  Only run check_log.py on the newest CSV in logs\

.PARAMETER Movie
  Path to .m64 to remind you to play (auto-play requires harness_config.lua movie_path)

.EXAMPLE
  powershell -File tools\windows\run_loop.ps1
  powershell -File tools\windows\run_loop.ps1 -CheckOnly
#>
param(
  [switch]$CheckOnly,
  [string]$Movie = "",
  [string]$Region = "us"
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $Root

$logs = Join-Path $Root "logs"
if (-not (Test-Path $logs)) { New-Item -ItemType Directory -Path $logs | Out-Null }

$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command python3 -ErrorAction SilentlyContinue }

if ($CheckOnly) {
  $latest = Get-ChildItem $logs -Filter "run_*.csv" -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
  if (-not $latest) {
    Write-Error "No run_*.csv in logs\. Run the Lua harness first."
  }
  if (-not $py) { Write-Error "Python required for check_log.py" }
  Write-Host "Checking $($latest.FullName)"
  & $py.Source (Join-Path $Root "tools\research\check_log.py") $latest.FullName --require-frames 1
  exit $LASTEXITCODE
}

$harness = Join-Path $Root "tools\research\harness\tas_harness.lua"
Write-Host @"

=== SM64 TAS Windows loop ===
Repo: $Root

STEP 1 — Start Mupen
  powershell -File tools\windows\run_mupen.ps1

STEP 2 — Load ROM ($Region)
  Double-click Super Mario 64 in the rom browser
  (USA for most archive ILs; Japan for classic 1-key)

STEP 3 — Load harness
  Drag onto Mupen window:
    $harness
  Or: Lua → New Instance → select tas_harness.lua

STEP 4 — Play movie (optional)
  Movie → Play → choose a .m64 from tas\
  Or set movie_path in harness_config.lua

STEP 5 — When finished
  Close Lua / stop movie
  Logs appear in: $logs

STEP 6 — Check log
  powershell -File tools\windows\run_loop.ps1 -CheckOnly

Console-first: only claim a result after hardware-safe design
  (see notes\console-first.md)

"@

if ($Movie -ne "") {
  Write-Host "Suggested movie: $Movie"
}

$launch = Read-Host "Start Mupen now? [Y/n]"
if ($launch -eq "" -or $launch -match '^[Yy]') {
  & (Join-Path $PSScriptRoot "run_mupen.ps1")
}
