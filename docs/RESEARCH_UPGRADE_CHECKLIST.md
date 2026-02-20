# Research Upgrade Checklist

Status legend: [x] implemented in repo, [ ] pending manual run

- [x] Use fixed benchmark manifest (Kodak + BSDS subset)
  - `data/benchmark_manifests/dataset_manifest.csv`
  - Downloader: `scripts/download_benchmarks.py`

- [x] Add statistical significance tests / bootstrap CIs
  - `scripts/analyze_results.py` -> `out/analysis/paired_stats.csv`, `bootstrap_ci.csv`

- [x] Separate numerical vs cryptographic claims
  - `docs/CLAIM_BOUNDARY.md`

- [x] Conditioning + spectrum proxy reporting
  - `scripts/analyze_results.py` -> `conditioning_failure_summary.csv`, `conditioning_vs_quality.png`
  - Includes sigma_min proxy = 1/cond(K)

- [x] Add ablation study runner (one-factor-at-a-time)
  - `scripts/run_ablation.py`

- [x] Improve fairness of timing in reproducibility pipeline
  - `scripts/run_research_pipeline.ps1` sets `OMP/MKL/OPENBLAS` thread envs to 1
  - Notebook already reports median/IQR

- [x] Add error-map quantitative summaries
  - `scripts/analyze_results.py` -> `error_map_summary.csv`

- [x] Add reproducibility package
  - `requirements.txt` (pinned)
  - `docs/REPRODUCIBILITY.md`
  - `scripts/run_research_pipeline.ps1`

- [x] Strengthen visual storytelling guidance
  - `docs/PAPER_FIGURE_PLAN.md`

## Suggested execution order
1. Run notebook end-to-end (`code.ipynb`)
2. `powershell -ExecutionPolicy Bypass -File scripts/run_research_pipeline.ps1`
3. (optional long run) `powershell -ExecutionPolicy Bypass -File scripts/run_research_pipeline.ps1 -RunAblation`
