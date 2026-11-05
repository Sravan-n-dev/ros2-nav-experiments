"""Summarise experiment CSVs: success rate, time, path length, efficiency, recoveries."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    """One row per (scenario, world) with aggregate navigation metrics."""
    df = df.copy()
    df["success"] = (df["status"] == "SUCCEEDED").astype(int)
    ok = df[df["success"] == 1]
    out = df.groupby(["scenario", "world"]).agg(
        runs=("status", "size"),
        success_rate=("success", "mean"),
        mean_recoveries=("recoveries", "mean"),
        total_recoveries=("recoveries", "sum"),
    )
    out["mean_time_s"] = ok.groupby(["scenario", "world"])["duration_s"].mean()
    out["mean_path_m"] = ok.groupby(["scenario", "world"])["path_length_m"].mean()
    out["mean_efficiency"] = ok.groupby(["scenario", "world"])["path_efficiency"].mean()
    return out.round(3).reset_index()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", nargs="+", type=Path, help="result CSV file(s)")
    parser.add_argument("--out", type=Path, help="optional path to save the summary CSV")
    args = parser.parse_args()
    frame = pd.concat([pd.read_csv(p) for p in args.csv], ignore_index=True)
    table = summarize(frame)
    print(table.to_string(index=False))
    if args.out:
        table.to_csv(args.out, index=False)


if __name__ == "__main__":
    main()
