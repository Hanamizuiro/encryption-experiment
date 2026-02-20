#!/usr/bin/env python
"""
Post-process experiment outputs for paper-ready statistical analysis.

Inputs (expected in out/):
- results_detail.csv
- results_summary.csv

Outputs (written to out/analysis/):
- paired_stats.csv
- bootstrap_ci.csv
- error_map_summary.csv
- conditioning_failure_summary.csv
- conditioning_vs_quality.png
"""

from __future__ import annotations

import csv
import math
import random
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
ANALYSIS = OUT / "analysis"
ANALYSIS.mkdir(parents=True, exist_ok=True)

DETAIL_CSV = OUT / "results_detail.csv"
SUMMARY_CSV = OUT / "results_summary.csv"


def read_csv(path: Path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def ffloat(v, default=float("nan")):
    try:
        return float(v)
    except Exception:
        return default


def paired_differences(rows, metric, baseline="np_solve"):
    # Pair key ensures same condition across solver variants.
    grouped = defaultdict(dict)
    for r in rows:
        key = (
            r.get("matrix_type"),
            r.get("sigma"),
            r.get("repeat"),
            r.get("image_idx"),
            r.get("data_source"),
        )
        grouped[key][r.get("solver")] = ffloat(r.get(metric))

    diffs = defaultdict(list)
    for _k, sols in grouped.items():
        b = sols.get(baseline)
        if b is None or (isinstance(b, float) and not math.isfinite(b)):
            continue
        for solver, v in sols.items():
            if solver == baseline:
                continue
            if v is None or (isinstance(v, float) and not math.isfinite(v)):
                continue
            diffs[solver].append(v - b)
    return diffs


def bootstrap_ci(values, n_boot=5000, alpha=0.05, seed=42):
    if not values:
        return float("nan"), float("nan"), float("nan")
    rng = random.Random(seed)
    n = len(values)
    means = []
    for _ in range(n_boot):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    lo_idx = int((alpha / 2) * len(means))
    hi_idx = int((1 - alpha / 2) * len(means)) - 1
    mean = sum(values) / len(values)
    return mean, means[max(0, lo_idx)], means[min(len(means) - 1, hi_idx)]


def sign_test_pvalue(diffs):
    # Simple non-parametric paired sign-test approximation.
    pos = sum(1 for d in diffs if d > 0)
    neg = sum(1 for d in diffs if d < 0)
    n = pos + neg
    if n == 0:
        return float("nan")
    # Two-sided exact binomial tail under p=0.5
    from math import comb

    k = min(pos, neg)
    tail = sum(comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def write_csv(path: Path, rows):
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main():
    if not DETAIL_CSV.exists() or not SUMMARY_CSV.exists():
        raise SystemExit("Missing out/results_detail.csv or out/results_summary.csv. Run code.ipynb first.")

    detail = read_csv(DETAIL_CSV)
    summary = read_csv(SUMMARY_CSV)

    # 1) Paired significance stats against baseline np_solve
    paired_stats_rows = []
    bootstrap_rows = []
    for metric in ["psnr_db", "time_ms"]:
        diffs_by_solver = paired_differences(detail, metric=metric, baseline="np_solve")
        for solver, diffs in sorted(diffs_by_solver.items()):
            mean, lo, hi = bootstrap_ci(diffs)
            pval = sign_test_pvalue(diffs)
            paired_stats_rows.append(
                {
                    "metric": metric,
                    "solver": solver,
                    "n_pairs": len(diffs),
                    "mean_delta_vs_np": mean,
                    "sign_test_pvalue": pval,
                }
            )
            bootstrap_rows.append(
                {
                    "metric": metric,
                    "solver": solver,
                    "n_pairs": len(diffs),
                    "mean_delta_vs_np": mean,
                    "ci95_low": lo,
                    "ci95_high": hi,
                }
            )

    write_csv(ANALYSIS / "paired_stats.csv", paired_stats_rows)
    write_csv(ANALYSIS / "bootstrap_ci.csv", bootstrap_rows)

    # 2) Error-map quantitative summary (from detail-level metrics)
    err_rows = []
    by_img = defaultdict(list)
    for r in detail:
        key = (r.get("image_name"), r.get("matrix_type"), r.get("solver"), r.get("sigma"))
        mse = ffloat(r.get("mse"))
        if math.isfinite(mse):
            by_img[key].append(mse)

    for (img, mtype, solver, sigma), vals in sorted(by_img.items()):
        vals_sorted = sorted(vals)
        err_rows.append(
            {
                "image_name": img,
                "matrix_type": mtype,
                "solver": solver,
                "sigma": sigma,
                "mse_mean": sum(vals) / len(vals),
                "mse_max": max(vals),
                "mse_median": vals_sorted[len(vals_sorted) // 2],
            }
        )

    write_csv(ANALYSIS / "error_map_summary.csv", err_rows)

    # 3) Conditioning vs failures/quality summary
    cond_rows = []
    grouped = defaultdict(list)
    for r in detail:
        key = (r.get("matrix_type"), r.get("solver"), r.get("sigma"))
        grouped[key].append(r)

    for (mtype, solver, sigma), rows in sorted(grouped.items()):
        cond = ffloat(rows[0].get("condition_number"))
        psnr_vals = [ffloat(r.get("psnr_db")) for r in rows]
        psnr_vals = [x for x in psnr_vals if math.isfinite(x)]
        fail_rate = sum(1 for r in rows if r.get("status") != "ok") / len(rows)
        cond_rows.append(
            {
                "matrix_type": mtype,
                "solver": solver,
                "sigma": sigma,
                "condition_number": cond,
                "sigma_min_proxy": (1.0 / cond) if cond and cond > 0 else float("nan"),
                "psnr_mean": (sum(psnr_vals) / len(psnr_vals)) if psnr_vals else float("nan"),
                "failure_rate": fail_rate,
            }
        )

    write_csv(ANALYSIS / "conditioning_failure_summary.csv", cond_rows)

    # Plot: conditioning proxy vs PSNR
    x = [ffloat(r["condition_number"]) for r in cond_rows]
    y = [ffloat(r["psnr_mean"]) for r in cond_rows]
    c = [ffloat(r["failure_rate"]) for r in cond_rows]

    if x and y:
        fig, ax = plt.subplots(figsize=(7, 4.5), constrained_layout=True)
        sc = ax.scatter(x, y, c=c, cmap="viridis", edgecolors="k", linewidths=0.4)
        ax.set_xscale("log")
        ax.set_xlabel("Condition number cond(K) [log]")
        ax.set_ylabel("Mean PSNR")
        ax.set_title("Conditioning vs Reconstruction Quality")
        cb = fig.colorbar(sc, ax=ax)
        cb.set_label("Failure rate")
        fig.savefig(ANALYSIS / "conditioning_vs_quality.png", dpi=220, bbox_inches="tight")
        plt.close(fig)

    print("Analysis artifacts written to:", ANALYSIS)


if __name__ == "__main__":
    main()
