#Requires -Version 5.1
<#
.SYNOPSIS
  Run a short, fully automated Mupen + movie + Lua logging smoke test.

.DESCRIPTION
  Requires a verified USA ROM under roms\. Runs a 342-input archive movie
  through Mupen's supported CLI, waits for the parity-check final hash, checks
  the generated CSV, and cleans up Mupen if its legacy GUI lingers on shutdown.
#>
param(
  [int]$TimeoutSeconds = 60,
  [switch]$Visible
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$Mupen = Join-Path $Root "tools\mupen64\repack-stable-main\stable\mupen64.exe"
$MupenDir = Split-Path -Parent $Mupen
$Rom = Join-Path $Root "roms\Super Mario 64 (USA).z64"
$Movie = Join-Path $Root "tas\archive\SM64TASArchive\Individual Levels\SM64\CCM - Cool, Cool Mountain\Wall Kicks Will Work\6s10ms (Textboxes)\Wall Kicks Will Work (U).m64"
$State = [IO.Path]::ChangeExtension($Movie, ".st")
$Harness = Join-Path $Root "tools\research\harness\tas_harness.lua"
$RepoLogs = Join-Path $Root "logs"
$MupenLog = Join-Path $MupenDir "logs\mupen.log"
$CheckLog = Join-Path $Root "tools\research\check_log.py"

foreach ($path in @($Mupen, $Rom, $Movie, $State, $Harness, $CheckLog)) {
  if (-not (Test-Path -LiteralPath $path)) {
    throw "Required file missing: $path"
  }
}

$romHash = (Get-FileHash -Algorithm MD5 -LiteralPath $Rom).Hash.ToLower()
if ($romHash -ne "20b854b239203baf6c961b850a4a51a2") {
  throw "USA ROM MD5 mismatch: $romHash"
}

$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command python3 -ErrorAction SilentlyContinue }
if (-not $py) { throw "Python 3 is required" }

$cliArgs = @(
  "--rom", ('"{0}"' -f $Rom),
  "--movie", ('"{0}"' -f $Movie),
  "--lua", ('"{0}"' -f $Harness),
  "--parity-check",
  "--parity-check-interval", "10",
  "--close-on-movie-end"
)

$parityPattern = "Final hash: ([0-9a-f]+) \(([0-9]+) checkpoints\)"
$baselineHashCount = 0
if (Test-Path -LiteralPath $MupenLog) {
  $baselineMatches = Select-String -LiteralPath $MupenLog -Pattern $parityPattern -AllMatches
  $baselineHashCount = ($baselineMatches.Matches | Measure-Object).Count
}

$started = Get-Date
$startParams = @{
  FilePath = $Mupen
  WorkingDirectory = $MupenDir
  ArgumentList = $cliArgs
  PassThru = $true
}
if (-not $Visible) { $startParams.WindowStyle = "Hidden" }

Write-Host "Starting automated Mupen smoke test..."
$proc = Start-Process @startParams
$deadline = $started.AddSeconds($TimeoutSeconds)
$finalHash = $null

try {
  while ((Get-Date) -lt $deadline) {
    $proc.Refresh()
    if (Test-Path -LiteralPath $MupenLog) {
      $matches = Select-String -LiteralPath $MupenLog -Pattern $parityPattern -AllMatches
      $allHashMatches = @($matches.Matches)
      if ($allHashMatches.Count -gt $baselineHashCount) {
        $newMatch = $allHashMatches[-1]
        $finalHash = $newMatch.Groups[1].Value
        $checkpoints = $newMatch.Groups[2].Value
        break
      }
    }
    if ($proc.HasExited) { break }
    Start-Sleep -Milliseconds 250
  }

  if (-not $finalHash) {
    throw "Mupen did not produce a parity final hash within $TimeoutSeconds seconds"
  }

  Start-Sleep -Seconds 1
  $proc.Refresh()
  if (-not $proc.HasExited) {
    Stop-Process -Id $proc.Id -Force
    $proc.WaitForExit()
    Write-Host "Cleaned up lingering Mupen GUI process"
  }
} catch {
  $proc.Refresh()
  if (-not $proc.HasExited) {
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
  }
  throw
}

$csv = Get-ChildItem -LiteralPath $RepoLogs -Filter "run_us_*.csv" |
  Where-Object LastWriteTime -ge $started.AddSeconds(-1) |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1
if (-not $csv) { throw "The Lua harness did not create a new USA CSV log" }

& $py.Source $CheckLog $csv.FullName --require-frames 300 --qpu-speed-check
if ($LASTEXITCODE -ne 0) { throw "CSV verification failed with exit code $LASTEXITCODE" }

Write-Host "SMOKE TEST PASS"
Write-Host "Parity hash: $finalHash ($checkpoints checkpoints)"
Write-Host "CSV: $($csv.FullName)"
