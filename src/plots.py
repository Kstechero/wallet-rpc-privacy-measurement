import os
import sys
import pandas as pd
import matplotlib.pyplot as plt


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def load_summary(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    numeric_cols = [
        "interval_s",
        "duration_s",
        "repeat_id",
        "ok_rate",
        "avg_latency_ms",
        "median_latency_ms",
        "p95_latency_ms",
        "min_latency_ms",
        "max_latency_ms",
        "has_address_ratio",
    ]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df


def grouped_mean(df: pd.DataFrame, value_col: str) -> pd.DataFrame:
    return (
        df.groupby(["scenario", "provider_id"], as_index=False)[value_col]
        .mean()
        .sort_values(["scenario", "provider_id"])
    )


def save_bar_chart(df: pd.DataFrame, value_col: str, ylabel: str, out_path: str) -> None:
    pivot = df.pivot(index="scenario", columns="provider_id", values=value_col)
    ax = pivot.plot(kind="bar", figsize=(10, 5))
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Scenario")
    ax.set_title(ylabel + " by Scenario and Provider")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()


def main() -> None:
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "results/summary.csv"
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "results/figures"

    ensure_dir(out_dir)

    df = load_summary(csv_path)
    if df.empty:
        print(f"No data in {csv_path}")
        raise SystemExit(1)

    median_df = grouped_mean(df, "median_latency_ms")
    p95_df = grouped_mean(df, "p95_latency_ms")
    addr_df = grouped_mean(df, "has_address_ratio")
    ok_df = grouped_mean(df, "ok_rate")

    save_bar_chart(
        median_df,
        "median_latency_ms",
        "Mean of Median Latency (ms)",
        os.path.join(out_dir, "latency_median.png"),
    )
    save_bar_chart(
        p95_df,
        "p95_latency_ms",
        "Mean of P95 Latency (ms)",
        os.path.join(out_dir, "latency_p95.png"),
    )
    save_bar_chart(
        addr_df,
        "has_address_ratio",
        "Mean has_address_ratio",
        os.path.join(out_dir, "has_address_ratio.png"),
    )
    save_bar_chart(
        ok_df,
        "ok_rate",
        "Mean ok_rate",
        os.path.join(out_dir, "ok_rate.png"),
    )

    print(f"Saved figures to {out_dir}")


if __name__ == "__main__":
    main()