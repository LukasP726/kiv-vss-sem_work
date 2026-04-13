param(
    [Parameter(Mandatory = $true)]
    [string]$NetLogoPath
)

$ErrorActionPreference = "Stop"
$scriptDir = $PSScriptRoot
$rootDir = [System.IO.Path]::GetFullPath((Join-Path $scriptDir ".."))
$outDir = Join-Path $rootDir "out"

if (-not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir | Out-Null
}

& (Join-Path $scriptDir "run_behaviorspace.ps1") -NetLogoPath $NetLogoPath -ModelPath (Join-Path $rootDir "examples\virus1.nlogox") -ExperimentName "ofat_transmission_auto" -OutputCsv (Join-Path $outDir "virus1_ofat_transmission.csv")
python (Join-Path $scriptDir "aggregate_results.py") --input (Join-Path $outDir "virus1_ofat_transmission.csv") --group-by "transmission-prob" --metrics "m_ticks,m_deaths,m_final_infected" --output (Join-Path $outDir "virus1_ofat_transmission_summary.csv")

& (Join-Path $scriptDir "run_behaviorspace.ps1") -NetLogoPath $NetLogoPath -ModelPath (Join-Path $rootDir "examples\virus2.nlogox") -ExperimentName "capacity_overload_grid_auto" -OutputCsv (Join-Path $outDir "virus2_capacity_grid.csv")
python (Join-Path $scriptDir "aggregate_results.py") --input (Join-Path $outDir "virus2_capacity_grid.csv") --group-by "healthcare-capacity,overload-multiplier" --metrics "m_deaths,m_final_infected" --output (Join-Path $outDir "virus2_capacity_grid_summary.csv")

& (Join-Path $scriptDir "run_behaviorspace.ps1") -NetLogoPath $NetLogoPath -ModelPath (Join-Path $rootDir "examples\virus3.nlogox") -ExperimentName "resources_grid_auto" -OutputCsv (Join-Path $outDir "virus3_resources_grid.csv")
python (Join-Path $scriptDir "aggregate_results.py") --input (Join-Path $outDir "virus3_resources_grid.csv") --group-by "resource-stock,resource-regeneration,treatment-cost" --metrics "m_deaths,m_final_resources,m_final_infected" --output (Join-Path $outDir "virus3_resources_grid_summary.csv")

& (Join-Path $scriptDir "run_behaviorspace.ps1") -NetLogoPath $NetLogoPath -ModelPath (Join-Path $rootDir "examples\virus4.nlogox") -ExperimentName "strategy_grid_auto" -OutputCsv (Join-Path $outDir "virus4_strategy_grid.csv")
python (Join-Path $scriptDir "aggregate_results.py") --input (Join-Path $outDir "virus4_strategy_grid.csv") --group-by "strategy-mode,high-risk-share,vaccination-rate" --metrics "m_deaths,m_final_infected" --output (Join-Path $outDir "virus4_strategy_grid_summary.csv")

Write-Host "Extended experiments completed."
