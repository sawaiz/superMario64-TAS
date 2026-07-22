#Requires -Version 5.1
<#
.SYNOPSIS
  Windows setup for superMario64-TAS (Mupen + tools + folders).

.DESCRIPTION
  Run from repo root OR from tools\windows:
    powershell -ExecutionPolicy Bypass -File tools\windows\setup.ps1

  - Creates roms\, logs\
  - Downloads Mupen64 stable repack + STROOP if missing
  - Verifies Python3 for check_log / research scripts
  - Does NOT download ROMs (place your own dumps)

.NOTES
  Console-first: automation is for authoring; real N64 is acceptance.
#>

$ErrorActionPreference = "Stop"

function Get-RepoRoot {
  $here = $PSScriptRoot
  if (Test-Path (Join-Path $here "..\..\README.md")) {
    return (Resolve-Path (Join-Path $here "..\..")).Path
  }
  if (Test-Path (Join-Path (Get-Location) "README.md")) {
    return (Resolve-Path (Get-Location)).Path
  }
  throw "Run from repo root or tools\windows"
}

$Root = Get-RepoRoot
Set-Location $Root
Write-Host "==> Repo: $Root"

# Folders
@(
  "roms",
  "logs",
  "tools\mupen64",
  "tools\STROOP",
  "tools\research\harness"
) | ForEach-Object {
  $p = Join-Path $Root $_
  if (-not (Test-Path $p)) {
    New-Item -ItemType Directory -Path $p | Out-Null
    Write-Host "    mkdir $_"
  }
}

# Copy example harness config if missing
$ex = Join-Path $Root "tools\research\harness\harness_config.example.lua"
$cfg = Join-Path $Root "tools\research\harness\harness_config.lua"
if ((Test-Path $ex) -and -not (Test-Path $cfg)) {
  Copy-Item $ex $cfg
  Write-Host "    created tools\research\harness\harness_config.lua (edit me)"
}

# Mupen
$mupenExe = Join-Path $Root "tools\mupen64\repack-stable-main\stable\mupen64.exe"
if (-not (Test-Path $mupenExe)) {
  Write-Host "==> Downloading Mupen64 stable repack..."
  $zip = Join-Path $Root "tools\mupen64\mupen64-repack-stable.zip"
  Invoke-WebRequest -Uri "https://github.com/mupen64/repack-stable/archive/refs/heads/main.zip" -OutFile $zip
  Expand-Archive -Path $zip -DestinationPath (Join-Path $Root "tools\mupen64") -Force
  Write-Host "    Mupen extracted"
} else {
  Write-Host "==> Mupen already present"
}

# Stage ROM folder for Mupen
$mupenRoms = Join-Path $Root "tools\mupen64\repack-stable-main\stable\roms"
if (-not (Test-Path $mupenRoms)) {
  New-Item -ItemType Directory -Path $mupenRoms | Out-Null
}

# Copy US ROM from repo root / roms if present
$candidates = @(
  (Join-Path $Root "Super Mario 64 (USA).z64"),
  (Join-Path $Root "roms\Super Mario 64 (USA).z64")
)
foreach ($c in $candidates) {
  if (Test-Path $c) {
    Copy-Item $c (Join-Path $mupenRoms "Super Mario 64 (USA).z64") -Force
    $repoRom = Join-Path $Root "roms\Super Mario 64 (USA).z64"
    if ([IO.Path]::GetFullPath($c) -ne [IO.Path]::GetFullPath($repoRom)) {
      Copy-Item $c $repoRom -Force
    }
    Write-Host "==> Staged USA ROM into roms\ and Mupen roms\"
    break
  }
}

# STROOP (optional large download)
$stroopExe = Join-Path $Root "tools\STROOP\net461\STROOP.exe"
if (-not (Test-Path $stroopExe)) {
  Write-Host "==> Downloading STROOP vDev (large)..."
  $szip = Join-Path $Root "tools\STROOP\STROOP-vDev.zip"
  try {
    Invoke-WebRequest -Uri "https://github.com/SM64-TAS-ABC/STROOP/releases/download/vDev/STROOP.zip" -OutFile $szip
    Expand-Archive -Path $szip -DestinationPath (Join-Path $Root "tools\STROOP") -Force
    Write-Host "    STROOP extracted"
  } catch {
    Write-Warning "STROOP download failed: $_ (optional - install later)"
  }
} else {
  Write-Host "==> STROOP already present"
}

# Python
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command python3 -ErrorAction SilentlyContinue }
if ($py) {
  Write-Host "==> Python: $($py.Source)"
  & $py.Source --version
} else {
  Write-Warning "Python not found. Install Python 3 and add to PATH for check_log.py / research tools."
}

# Write local config
$configPath = Join-Path $Root "tools\windows\config.local.json"
if (-not (Test-Path $configPath)) {
  $example = Get-Content (Join-Path $Root "tools\windows\config.example.json") -Raw
  $example = $example -replace '"repo_root": null', "`"repo_root`": `"$($Root -replace '\\','\\')`""
  Set-Content -Path $configPath -Value $example -Encoding UTF8
  Write-Host "==> Wrote tools\windows\config.local.json"
}

Write-Host ""
Write-Host "=== Setup complete ==="
Write-Host "1. Place legal ROMs in:  $Root\roms\"
Write-Host "   USA MD5: 20b854b239203baf6c961b850a4a51a2"
Write-Host "   JP  MD5: 85d61f5525af708c9f1e84dce6dc10e9"
Write-Host "2. Start Mupen:  powershell -File tools\windows\run_mupen.ps1"
Write-Host "3. Read:         notes\windows-setup.md"
Write-Host "4. Full loop:    notes\windows-setup.md  (harness + check_log)"
Write-Host "5. Smoke test:   powershell -File tools\windows\smoke_test.ps1"
Write-Host ""
Write-Host "Console-first: Mupen automation is for experiments; real N64 is acceptance."
