# Step-by-Step Process (Group Guide)

This guide explains how to run the full experiment in a consistent way using the benchmark dataset manifest.

## 1) Project Organization

Use this structure and keep each file in its role:

- `code.ipynb`
  - Main experiment notebook (data loading, encryption/decryption runs, metrics, plots, LaTeX tables).
- `scripts/download_benchmarks.py`
  - Downloads benchmark images listed in the manifest.
- `scripts/analyze_results.py`
  - Post-processing stats (paired tests, bootstrap CIs, conditioning summary, error-map summary).
- `scripts/run_ablation.py`
  - One-factor-at-a-time ablation runner (long run).
- `scripts/run_research_pipeline.ps1`
  - Convenience pipeline wrapper.
- `data/benchmark_manifests/dataset_manifest.csv`
  - Reproducible dataset definition (what files must exist).
- `data/benchmarks/`
  - Downloaded benchmark images (Kodak/BSDS).
- `out/`
  - All generated experiment outputs.
- `docs/`
  - Research notes: claim scope, reproducibility, figure plan, upgrade checklist.
- `requirements.txt`
  - Python dependency versions.

Recommended housekeeping:
- Treat `data/custom_images/` as optional only.
- Do not manually edit files inside `out/`; regenerate from notebook/scripts.
- Commit changes in this order: manifest/config -> notebook outputs -> analysis outputs -> docs.

## 2) Environment Setup (Each Groupmate)

From project root (`E:\Projects\Numerical-Analysis-Project`):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Verify interpreter:

```powershell
python -c "import sys; print(sys.executable)"
```

Expected: path should end with `.venv\Scripts\python.exe`.

## 3) Prepare Benchmark Data

1. Open `data/benchmark_manifests/dataset_manifest.csv`.
2. Confirm URLs and file IDs are correct.
3. Download the files:

```powershell
python .\scripts\download_benchmarks.py
```

4. Confirm files exist in:
- `data/benchmarks/kodak/`
- `data/benchmarks/bsds/`

## 4) Run Main Experiment (Notebook)

Open `code.ipynb` and make sure in `CONFIG`:

- `"data_source": "benchmark"`
- `"benchmark_manifest": "data/benchmark_manifests/dataset_manifest.csv"`
- `"benchmark_root": "data/benchmarks"`

Then run all cells from top to bottom.

Important behavior:
- Notebook now fails fast if any manifest-listed benchmark file is missing.
- This guarantees reproducible dataset usage.

## 5) Generate Statistical Analysis

After notebook finishes:

```powershell
python .\scripts\analyze_results.py
```

This creates `out/analysis/` with:
- `paired_stats.csv`
- `bootstrap_ci.csv`
- `error_map_summary.csv`
- `conditioning_failure_summary.csv`
- `conditioning_vs_quality.png`

## 6) Optional: Run Pipeline Script

If you want one wrapper command:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_research_pipeline.ps1
```

With options:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_research_pipeline.ps1 -DownloadBenchmarks
powershell -ExecutionPolicy Bypass -File .\scripts\run_research_pipeline.ps1 -RunAblation
```

Notes:
- `-RunAblation` is long.
- Pipeline sets thread pinning (`OMP/MKL/OPENBLAS=1`) for fairer timing comparisons.

## 7) Optional: Ablation Study

```powershell
python .\scripts\run_ablation.py
```

Outputs are copied under:
- `out/ablation_runs/<factor>_<value>/...`

## 8) Final Files for Paper

Main files to use in writing:
- Metrics and tables: `out/results_summary.csv`, `out/results_detail.csv`, `out/tables/*.tex`
- Core figures: `out/figures/metrics_dense.png`, `out/figures/metrics_sparse.png`, `out/figures/gs_convergence_traces.png`, selected `wall_*.png` and `wall_err_*.png`
- Statistical claims: `out/analysis/paired_stats.csv`, `out/analysis/bootstrap_ci.csv`
- Conditioning/failure evidence: `out/analysis/conditioning_failure_summary.csv`, `out/analysis/conditioning_vs_quality.png`

## 9) Troubleshooting

- `ModuleNotFoundError`:
  - You are not using `.venv` interpreter. Re-activate `.venv` and reinstall requirements.
- Benchmark file missing error:
  - Re-run `python .\scripts\download_benchmarks.py`.
  - Check `dataset_manifest.csv` paths and URLs.
- VS Code cannot resolve imports:
  - Select interpreter: `.venv\Scripts\python.exe`.
- `/usr/bin/env` errors on Windows:
  - Use PowerShell commands above, not Unix-style launcher commands.

## 10) What This Study Claims (Scope)

This project is a **numerical solver comparison** for matrix-based image encryption/decryption experiments.
It is **not** a formal proof of modern cryptographic security.

Use the results to discuss:
- numerical stability,
- conditioning,
- reconstruction quality,
- runtime/failure tradeoffs,

not real-world secure cryptosystem guarantees.
