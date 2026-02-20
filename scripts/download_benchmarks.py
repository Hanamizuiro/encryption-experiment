#!/usr/bin/env python
"""
Download fixed benchmark images listed in data/benchmark_manifests/dataset_manifest.csv
into data/benchmarks/<dataset>/
"""

from __future__ import annotations

import csv
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "benchmark_manifests" / "dataset_manifest.csv"
TARGET_ROOT = ROOT / "data" / "benchmarks"


def main():
    if not MANIFEST.exists():
        raise SystemExit(f"Missing manifest: {MANIFEST}")

    with MANIFEST.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    for r in rows:
        dataset = r["dataset"].strip()
        base = r["source_url"].strip().rstrip("/")
        file_id = r["file_id"].strip()
        url = f"{base}/{file_id}"

        out_dir = TARGET_ROOT / dataset
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / file_id
        if out_path.exists():
            continue

        print("Downloading", url)
        try:
            urllib.request.urlretrieve(url, out_path)
        except Exception as exc:
            print("Failed:", url, "|", exc)

    print("Done. Dataset root:", TARGET_ROOT)


if __name__ == "__main__":
    main()
