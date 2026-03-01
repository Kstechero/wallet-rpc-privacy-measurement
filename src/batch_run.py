import glob
import os
import sys
from typing import List

from runner import run_from_config
from summarize import compute_stats, append_csv


def list_configs(pattern: str) -> List[str]:
    files = glob.glob(pattern)
    files.sort()
    return files


def main() -> None:
    # default: scan configs/m2
    pattern = sys.argv[1] if len(sys.argv) > 1 else "configs/m2/*.yaml"
    csv_path = sys.argv[2] if len(sys.argv) > 2 else "results/summary.csv"

    cfgs = list_configs(pattern)
    if not cfgs:
        print(f"No config files found: {pattern}")
        raise SystemExit(1)

    os.makedirs("results", exist_ok=True)

    print(f"Found {len(cfgs)} configs. Output CSV: {csv_path}\n")

    for idx, cfg in enumerate(cfgs, start=1):
        print(f"[{idx}/{len(cfgs)}] Running: {cfg}")
        out_log = run_from_config(cfg)
        stats = compute_stats(out_log)
        append_csv(stats, csv_path)
        print(f"  -> log: {out_log}")
        print(f"  -> appended CSV row\n")

    print("Batch run complete.")


if __name__ == "__main__":
    main()