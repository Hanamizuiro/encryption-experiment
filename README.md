# Numerical Analysis Project: Matrix-Based Image Encryption Solver Study

A research-focused repository that benchmarks numerical solvers for matrix-based image encryption/decryption under noise, conditioning stress, and sparse/dense key settings.

## Project Overview

This project investigates a central numerical analysis question:

**When encrypted image reconstruction depends on solving linear systems, which solvers remain accurate, stable, and efficient as problem conditions become harder?**

Instead of treating encryption as a black box, the study explicitly measures solver behavior (quality, runtime, failure rate, and convergence) across controlled perturbations.

## Research Scope

- Domain: numerical linear algebra for matrix-based image schemes.
- Focus: solver robustness and reconstruction behavior.
- Not in scope: formal modern-cryptography security proofs.

## What This Repository Produces

From a single experimental pipeline, the repo generates:

- Per-run and aggregate metrics (`CSV`)
- Publication-ready plots (`PNG`)
- LaTeX-ready tables (`.tex`)
- Statistical comparison artifacts (paired tests + bootstrap CIs)
- Conditioning vs. quality/failure diagnostics
- Ablation results for factor-isolation analysis

## Experimental Design Summary

The notebook and scripts evaluate solvers over:

- Dense and sparse key matrices
- Multiple Gaussian noise levels
- Repeated runs for timing/quality robustness
- Benchmark image sets (Kodak + BSDS subset)
- Baseline comparison against `np_solve`

Primary outputs are interpreted through:

- PSNR / MSE / runtime behavior
- Solver ranking tables
- Convergence traces (Gauss-Seidel)
- Error-map summaries
- Conditioning proxies (including `cond(K)` trends)

## Reproducibility

This repository is designed for team reproducibility with:

- Fixed benchmark manifest
- Strict benchmark file existence checks in notebook loading
- Dependency pinning via `requirements.txt`
- Thread pinning in pipeline wrapper for fairer timing conditions
- Run metadata saved to `out/config.json` and `out/run_info.json`
