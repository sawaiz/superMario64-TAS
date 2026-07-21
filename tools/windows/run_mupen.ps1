#Requires -Version 5.1
<#
.SYNOPSIS
  Launch Mupen64-rr from the repo on Windows.
#>
$ErrorActionPreference = "Stop"

$Root = if (Test-Path (Join-Path $PSScriptRoot "..\..\README.md")) {
  (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
} else {
  (Resolve-Path (Get-Location)).Path
}

$mupenDir = Join-Path $Root "tools\mupen64\repack-stable-main\stable"
$exe = Join-Path $mupenDir "mupen64.exe"
if (-not (Test-Path $exe)) {
  Write-Error "Mupen not found. Run: powershell -File tools\windows\setup.ps1"
}

# Stage ROM if present
$romUs = Join-Path $Root "roms\Super Mario 64 (USA).z64"
$dest = Join-Path $mupenDir "roms\Super Mario 64 (USA).z64"
if ((Test-Path $romUs) -and -not (Test-Path $dest)) {
  Copy-Item $romUs $dest -Force
}

Write-Host "Starting: $exe"
Write-Host "WorkingDirectory: $mupenDir"
Start-Process -FilePath $exe -WorkingDirectory $mupenDir
