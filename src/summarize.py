import os
import sys
import json
import csv
from collections import Counter
from statistics import mean, median
from typing import Dict, Any, List, Optional


def percentile(sorted_vals: List[int], p: float) -> Optional[float]:
    if not sorted_vals:
        return None
    # p in [0,1]
    n = len(sorted_vals)
    idx = int((n - 1) * p)
    return float(sorted_vals[idx])


def compute_stats(path: str) -> Dict[str, Any]:
    total = 0
    ok = 0
    err = 0
    latencies: List[int] = []
    has_addr = 0
    methods = Counter()
    errors = Counter()
    scenarios = Counter()

    # experiment meta (read from first line if present)
    meta: Dict[str, Any] = {}

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            r = json.loads(line)
            total += 1

            if not meta:
                # copy some meta keys if present
                for k in ["provider_id", "rpc_url", "chain_id", "scenario", "duration_s", "interval_s", "repeat_id"]:
                    if k in r:
                        meta[k] = r.get(k)

            status = r.get("status")
            if status == "ok":
                ok += 1
            else:
                err += 1
                errors[r.get("error") or "unknown_error"] += 1

            m = r.get("method") or "unknown_method"
            methods[m] += 1

            sc = r.get("scenario") or "unknown_scenario"
            scenarios[sc] += 1

            if r.get("has_address") is True:
                has_addr += 1

            lm = r.get("latency_ms")
            if isinstance(lm, int):
                latencies.append(lm)

    lat_sorted = sorted(latencies)
    stats: Dict[str, Any] = {}
    stats.update(meta)
    stats.update(
        {
            "file": path,
            "total": total,
            "ok": ok,
            "err": err,
            "ok_rate": (ok / total) if total else 0.0,
            "has_address_ratio": (has_addr / total) if total else 0.0,
            "avg_latency_ms": float(mean(latencies)) if latencies else None,
            "median_latency_ms": float(median(latencies)) if latencies else None,
            "p95_latency_ms": percentile(lat_sorted, 0.95) if lat_sorted else None,
            "min_latency_ms": int(min(lat_sorted)) if lat_sorted else None,
            "max_latency_ms": int(max(lat_sorted)) if lat_sorted else None,
            "scenario_counts": dict(scenarios),
            "method_counts": dict(methods),
            "error_counts": dict(errors),
        }
    )
    return stats


def print_stats(stats: Dict[str, Any]) -> None:
    path = stats["file"]
    total = stats["total"]
    ok = stats["ok"]
    err = stats["err"]
    ok_rate = stats["ok_rate"]

    print(f"file: {path}")
    print(f"total={total} ok={ok} err={err} ok_rate={ok_rate:.3f}")

    if stats["avg_latency_ms"] is None:
        print("latency_ms: NA")
    else:
        print(
            "latency_ms: "
            f"avg={stats['avg_latency_ms']:.1f} "
            f"median={stats['median_latency_ms']:.1f} "
            f"p95={stats['p95_latency_ms']:.1f} "
            f"min={stats['min_latency_ms']} "
            f"max={stats['max_latency_ms']}"
        )

    print(f"has_address_ratio={stats['has_address_ratio']:.3f}")

    print("\nscenarios:")
    for k, v in sorted(stats["scenario_counts"].items(), key=lambda x: (-x[1], x[0])):
        print(f"  {k}: {v}")

    print("\nmethods:")
    for k, v in sorted(stats["method_counts"].items(), key=lambda x: (-x[1], x[0])):
        print(f"  {k}: {v}")

    if stats["error_counts"]:
        print("\nerrors:")
        for k, v in sorted(stats["error_counts"].items(), key=lambda x: (-x[1], x[0]))[:10]:
            print(f"  {k}: {v}")

    print("\n" + "-" * 60 + "\n")


def append_csv(stats: Dict[str, Any], csv_path: str) -> None:
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    # Flatten minimal fields for CSV
    row = {
        "file": stats.get("file"),
        "provider_id": stats.get("provider_id"),
        "scenario": stats.get("scenario"),
        "interval_s": stats.get("interval_s"),
        "duration_s": stats.get("duration_s"),
        "repeat_id": stats.get("repeat_id"),
        "total": stats.get("total"),
        "ok": stats.get("ok"),
        "err": stats.get("err"),
        "ok_rate": stats.get("ok_rate"),
        "avg_latency_ms": stats.get("avg_latency_ms"),
        "median_latency_ms": stats.get("median_latency_ms"),
        "p95_latency_ms": stats.get("p95_latency_ms"),
        "max_latency_ms": stats.get("max_latency_ms"),
        "has_address_ratio": stats.get("has_address_ratio"),
        # store top error (if any)
        "top_error": None,
        "top_error_count": 0,
    }

    if stats.get("error_counts"):
        top_err = max(stats["error_counts"].items(), key=lambda x: x[1])
        row["top_error"] = top_err[0]
        row["top_error_count"] = top_err[1]

    fieldnames = list(row.keys())
    write_header = not os.path.exists(csv_path)

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            w.writeheader()
        w.writerow(row)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python src/summarize.py <log1.jsonl> [<log2.jsonl> ...] [--csv results/summary.csv]")
        raise SystemExit(1)

    args = sys.argv[1:]
    csv_path = None
    if "--csv" in args:
        i = args.index("--csv")
        csv_path = args[i + 1] if i + 1 < len(args) else "results/summary.csv"
        args = args[:i] + args[i + 2 :]

    for p in args:
        s = compute_stats(p)
        print_stats(s)
        if csv_path:
            append_csv(s, csv_path)


if __name__ == "__main__":
    main()