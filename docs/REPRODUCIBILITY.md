# Reproducibility Package

## Environment
1. Create venv and install pinned dependencies:
   - `python -m venv .venv`
   - `.\\.venv\\Scripts\\Activate.ps1`
   - `python -m pip install -r requirements.txt`

## Seed Policy
- Global study seed is defined in `code.ipynb` (`CONFIG["seed"]`).
- Keep this fixed for all paper-reported runs.

## Dataset Policy
- Custom dataset: `data/custom_images/`
- Fixed academic benchmark: `data/benchmark_manifests/dataset_manifest.csv`
  - Kodak 24 + BSDS test subset (10 IDs)

## Experiment Execution
1. Run `code.ipynb` fully.
2. Verify outputs in `out/`:
   - `results_detail.csv`
   - `results_summary.csv`
   - `results_solver_ranking.csv`
   - `results_delta_vs_np_solve.csv`
   - `traces/gs_convergence_traces.csv`
   - `figures/*`
3. Run post-processing stats script:
   - `python scripts/analyze_results.py`

## Timing Fairness Requirements
- Keep thread count fixed during main runs (see pipeline script).
- Use notebook median/IQR as primary timing metric.
- Report machine/OS from `out/run_info.json`.

## Appendix Artifacts to include
- `out/config.json`
- `out/run_info.json`
- `requirements.txt`
- benchmark manifest file
- exact commands used (`scripts/run_research_pipeline.ps1`)
