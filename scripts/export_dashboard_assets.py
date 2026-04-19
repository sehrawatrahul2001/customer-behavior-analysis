from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    category_df = pd.read_csv(PROCESSED_DIR / "revenue_by_category.csv")
    rfm_df = pd.read_csv(PROCESSED_DIR / "rfm_segment_summary.csv")

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    axes[0].bar(
        category_df["category"],
        category_df["total_revenue"] / 1_000,
        color=["#1d4ed8", "#0f766e", "#d97706", "#9333ea"],
    )
    axes[0].set_title("Revenue by Category")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Revenue (USD Thousands)")
    axes[0].tick_params(axis="x", rotation=20)

    axes[1].bar(
        rfm_df["rfm_segment"],
        rfm_df["average_spend"],
        color=["#0f766e", "#1d4ed8", "#b91c1c", "#d97706"],
    )
    axes[1].set_title("Average Spend by RFM Segment")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("Average Spend (USD)")
    axes[1].tick_params(axis="x", rotation=20)

    fig.suptitle("Customer Revenue and Segmentation Overview", fontsize=16, fontweight="bold")
    fig.tight_layout()
    output_path = ASSETS_DIR / "customer_behavior_overview.png"
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved dashboard asset: {output_path}")


if __name__ == "__main__":
    main()
