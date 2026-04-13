param(
    [Parameter(Mandatory = $true)]
    [string]$NetLogoPath
)

$ErrorActionPreference = "Stop"
$scriptDir = $PSScriptRoot
$rootDir = [System.IO.Path]::GetFullPath((Join-Path $scriptDir ".."))

$models = @(
    @{ Name = "virus1"; Path = (Join-Path $rootDir "examples\virus1.nlogox") },
    @{ Name = "virus2"; Path = (Join-Path $rootDir "examples\virus2.nlogox") },
    @{ Name = "virus3"; Path = (Join-Path $rootDir "examples\virus3.nlogox") },
    @{ Name = "virus4"; Path = (Join-Path $rootDir "examples\virus4.nlogox") }
)

$outDir = Join-Path $rootDir "out"
if (-not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir | Out-Null
}

foreach ($m in $models) {
    $raw = Join-Path $outDir "$($m.Name)_baseline.csv"
    $summary = Join-Path $outDir "$($m.Name)_baseline_summary.csv"

    & (Join-Path $scriptDir "run_behaviorspace.ps1") `
        -NetLogoPath $NetLogoPath `
        -ModelPath $m.Path `
        -ExperimentName "baseline_auto" `
        -OutputCsv $raw

    python (Join-Path $scriptDir "aggregate_results.py") `
        --input $raw `
        --metrics "m_final_susceptible,m_final_exposed,m_final_infected,m_final_recovered,m_ever_infected,m_ticks,m_deaths,m_final_resources" `
        --output $summary
}

Write-Host "All baseline runs completed."
