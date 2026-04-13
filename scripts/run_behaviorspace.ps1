param(
    [Parameter(Mandatory = $true)]
    [string]$NetLogoPath,

    [Parameter(Mandatory = $true)]
    [string]$ModelPath,

    [Parameter(Mandatory = $true)]
    [string]$ExperimentName,

    [Parameter(Mandatory = $true)]
    [string]$OutputCsv
)

$ErrorActionPreference = "Stop"

$modelFull = (Resolve-Path $ModelPath).Path
$outDir = Split-Path -Parent $OutputCsv
if ($outDir -and -not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir | Out-Null
}

function Resolve-HeadlessLauncher {
    param([string]$InputPath)

    $resolved = (Resolve-Path $InputPath).Path

    if ($resolved.ToLower().EndsWith("netlogo-headless.bat")) {
        return $resolved
    }

    $parent = Split-Path -Parent $resolved
    $candidate = Join-Path $parent "netlogo-headless.bat"
    if (Test-Path $candidate) {
        return $candidate
    }

    throw "Cannot find netlogo-headless.bat next to: $resolved"
}

$headlessLauncher = Resolve-HeadlessLauncher -InputPath $NetLogoPath
$stdoutLog = [System.IO.Path]::ChangeExtension($OutputCsv, ".stdout.log")
$stderrLog = [System.IO.Path]::ChangeExtension($OutputCsv, ".stderr.log")

if (Test-Path $OutputCsv) {
    Remove-Item $OutputCsv -Force
}

Write-Host "Running BehaviorSpace experiment..."
Write-Host "Model: $modelFull"
Write-Host "Experiment: $ExperimentName"
Write-Host "Output: $OutputCsv"
Write-Host "Launcher: $headlessLauncher"

& "$headlessLauncher" `
  --headless `
  --model "$modelFull" `
  --experiment "$ExperimentName" `
  --table "$OutputCsv" `
  1> "$stdoutLog" `
  2> "$stderrLog"

if (-not (Test-Path $OutputCsv)) {
    throw "BehaviorSpace did not create output CSV: $OutputCsv`nSee logs: $stdoutLog and $stderrLog"
}

$lineCount = (Get-Content $OutputCsv | Measure-Object -Line).Lines
if ($lineCount -lt 2) {
    throw "BehaviorSpace output has no data rows: $OutputCsv`nSee logs: $stdoutLog and $stderrLog"
}

Write-Host "Done."
