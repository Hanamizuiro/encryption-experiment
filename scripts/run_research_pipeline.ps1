param(
    [switch]$RunAblation = $false,
    [switch]$DownloadBenchmarks = $false
)

$ErrorActionPreference = 'Stop'

Write-Host '=== Numerical Analysis Research Pipeline ==='

$python = Join-Path $PSScriptRoot '..\.venv\Scripts\python.exe'
$python = (Resolve-Path $python).Path

if ($DownloadBenchmarks) {
    Write-Host 'Downloading fixed benchmark subset...'
    & $python (Join-Path $PSScriptRoot 'download_benchmarks.py')
}

# Fairer timing conditions: fixed thread envs
$env:OMP_NUM_THREADS = '1'
$env:MKL_NUM_THREADS = '1'
$env:OPENBLAS_NUM_THREADS = '1'
Write-Host 'Thread pinning set: OMP/MKL/OPENBLAS = 1'

Write-Host 'Run code.ipynb manually (or via nbconvert) before analysis to refresh out/*.csv'
Write-Host 'Running post-processing significance/analysis...'
& $python (Join-Path $PSScriptRoot 'analyze_results.py')

if ($RunAblation) {
    Write-Host 'Running one-factor-at-a-time ablation sweep (long run)...'
    & $python (Join-Path $PSScriptRoot 'run_ablation.py')
}

Write-Host 'Pipeline complete.'
Write-Host 'See docs/REPRODUCIBILITY.md and docs/PAPER_FIGURE_PLAN.md'
