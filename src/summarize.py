import sys
import json
from collections import Counter
from statistics import mean, median

def summarize(path: str) -> None:
    total = 0
    ok = 0
    err = 0
    latencies = []
    has_addr = 0
    methods = Counter()
    errors = Counter()
    scenarios = Counter()

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            r = json.loads(line)
            total += 1

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

    print(f"file: {path}")
    print(f"total={total} ok={ok} err={err} ok_rate={(ok/total if total else 0):.3f}")
    if latencies:
        print(f"latency_ms: avg={mean(latencies):.1f} median={median(latencies):.1f} min={min(latencies)} max={max(latencies)}")
    else:
        print("latency_ms: NA")

    print(f"has_address_ratio={(has_addr/total if total else 0):.3f} ({has_addr}/{total})")

    print("\nscenarios:")
    for k, v in scenarios.most_common():
        print(f"  {k}: {v}")

    print("\nmethods:")
    for k, v in methods.most_common():
        print(f"  {k}: {v}")

    if errors:
        print("\nerrors (top 10):")
        for k, v in errors.most_common(10):
            print(f"  {k}: {v}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python src/summarize.py <path_to_jsonl> [<path_to_jsonl> ...]")
        raise SystemExit(1)

    for p in sys.argv[1:]:
        summarize(p)
        print("\n" + "-" * 60 + "\n")

if __name__ == "__main__":
    main()
