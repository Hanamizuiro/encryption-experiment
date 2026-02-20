#!/usr/bin/env python
"""
Run one-factor-at-a-time ablations by editing CONFIG in code.ipynb and executing it.

Requires:
- jupyter (for nbconvert execution)

Outputs:
- out/ablation_runs/<factor>_<value>/... copied run artifacts
"""

from __future__ import annotations

import copy
import json
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NB_PATH = ROOT / "code.ipynb"
OUT_DIR = ROOT / "out"
ABLATION_DIR = OUT_DIR / "ablation_runs"
ABLATION_DIR.mkdir(parents=True, exist_ok=True)

FACTORS = {
    "noise_sigmas": [
        [0.0, 0.01, 0.03],
        [0.0, 0.03, 0.07, 0.12],
        [0.0, 0.05, 0.10, 0.20],
    ],
    "sparse_density": [0.20, 0.08, 0.03],
    "dense_diag_boost": [32.0, 24.0, 12.0],
    "gs_tol": [1e-6, 1e-4, 1e-3],
    "gs_max_iters": [400, 200, 60],
}


def load_nb(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_nb(path: Path, nb):
    path.write_text(json.dumps(nb, indent=1), encoding="utf-8")


def update_config_cell(nb, key, value):
    for cell in nb["cells"]:
        if cell.get("cell_type") != "code":
            continue
        src = "".join(cell.get("source", []))
        if "CONFIG = {" not in src:
            continue
        lines = src.splitlines()
        out = []
        replaced = False
        for line in lines:
            if f'"{key}":' in line:
                json_value = json.dumps(value)
                indent = line[: len(line) - len(line.lstrip(" "))]
                out.append(f'{indent}"{key}": {json_value},')
                replaced = True
            else:
                out.append(line)
        if not replaced:
            raise RuntimeError(f"Could not update CONFIG key: {key}")
        cell["source"] = [ln + "\n" for ln in out]
        return
    raise RuntimeError("CONFIG cell not found")


def run_notebook(nb_path: Path):
    cmd = [
        "jupyter",
        "nbconvert",
        "--to",
        "notebook",
        "--execute",
        "--inplace",
        str(nb_path),
    ]
    subprocess.run(cmd, check=True, cwd=str(ROOT))


def copy_outputs(target: Path):
    target.mkdir(parents=True, exist_ok=True)
    for rel in [
        "results_summary.csv",
        "results_detail.csv",
        "results_solver_ranking.csv",
        "results_delta_vs_np_solve.csv",
        "run_info.json",
        "config.json",
    ]:
        src = OUT_DIR / rel
        if src.exists():
            shutil.copy2(src, target / rel)


def main():
    original = load_nb(NB_PATH)

    try:
        for factor, values in FACTORS.items():
            for value in values:
                nb = copy.deepcopy(original)
                update_config_cell(nb, factor, value)
                save_nb(NB_PATH, nb)

                tag = str(value).replace(" ", "").replace("[", "").replace("]", "").replace(",", "-")
                run_name = f"{factor}_{tag}"
                print("Running ablation:", run_name)

                run_notebook(NB_PATH)
                copy_outputs(ABLATION_DIR / run_name)

        print("Ablation finished. Outputs in:", ABLATION_DIR)

    finally:
        save_nb(NB_PATH, original)


if __name__ == "__main__":
    main()
