param(
    [Parameter(Mandatory = $true)]
    [string]$NetLogoPath
)

$ErrorActionPreference = "Stop"
$scriptDir = $PSScriptRoot

& (Join-Path $scriptDir "run_all_baselines.ps1") -NetLogoPath $NetLogoPath
& (Join-Path $scriptDir "run_extended_experiments.ps1") -NetLogoPath $NetLogoPath

Write-Host "All experiments and aggregations completed."
