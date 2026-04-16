import os
import csv

def main():
    print("M3 Result Summarizer")

    input_csv = "summary.csv"
    output_dir = "tools/output"
    output_md = os.path.join(output_dir, "result_summary.md")

    if not os.path.exists(input_csv):
        print("summary.csv not found")
        return

    os.makedirs(output_dir, exist_ok=True)

    with open(input_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    with open(output_md, "w", encoding="utf-8") as f:
        f.write("# M3 Result Summary\n\n")
        f.write("| provider | scenario | success_rate | avg_latency_ms |\n")
        f.write("|----------|----------|--------------|----------------|\n")

        for r in rows[:10]:
            f.write(f"| {r.get('provider')} | {r.get('scenario')} | {r.get('success_rate')} | {r.get('avg_latency_ms')} |\n")

    print(f"Summary saved to {output_md}")

if __name__ == "__main__":
    main()