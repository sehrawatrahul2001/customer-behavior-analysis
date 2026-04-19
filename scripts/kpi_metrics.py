from __future__ import annotations

from typing import Any

import pandas as pd


def build_summary_tables(df: pd.DataFrame) -> dict[str, Any]:
    segment_series = pd.cut(
        df["previous_purchases"],
        bins=[0, 1, 10, float("inf")],
        labels=["New", "Returning", "Loyal"],
        include_lowest=True,
    )

    revenue_by_subscription_status = (
        df.groupby("subscription_status")
        .agg(
            average_spend=("purchase_amount", "mean"),
            total_revenue=("purchase_amount", "sum"),
            customer_count=("customer_id", "count"),
        )
        .reset_index()
        .sort_values("total_revenue", ascending=False)
    )

    customer_lifetime_segments = (
        df.groupby("customer_lifetime_segment")
        .agg(
            customer_count=("customer_id", "count"),
            average_spend=("purchase_amount", "mean"),
            average_review_rating=("review_rating", "mean"),
        )
        .reset_index()
        .sort_values(["customer_count", "average_spend"], ascending=[False, False])
    )

    rfm_segment_summary = (
        df.groupby("rfm_segment")
        .agg(
            customer_count=("customer_id", "count"),
            total_revenue=("purchase_amount", "sum"),
            average_spend=("purchase_amount", "mean"),
        )
        .reset_index()
        .sort_values("total_revenue", ascending=False)
    )

    top_locations = (
        df.groupby("location")
        .agg(
            total_revenue=("purchase_amount", "sum"),
            average_spend=("purchase_amount", "mean"),
            customer_count=("customer_id", "count"),
        )
        .reset_index()
        .sort_values("total_revenue", ascending=False)
        .head(10)
    )

    priority_tiers = (
        df.groupby("customer_priority_tier", dropna=False)
        .agg(
            customer_count=("customer_id", "count"),
            total_revenue=("purchase_amount", "sum"),
            average_spend=("purchase_amount", "mean"),
        )
        .reset_index()
        .sort_values("total_revenue", ascending=False)
    )

    payment_summary = (
        df.groupby("payment_method")
        .agg(
            total_orders=("customer_id", "count"),
            total_revenue=("purchase_amount", "sum"),
            average_spend=("purchase_amount", "mean"),
        )
        .reset_index()
        .sort_values("total_revenue", ascending=False)
    )

    return {
        "kpis": {
            "total_customers": int(df["customer_id"].nunique()),
            "average_purchase_amount": round(float(df["purchase_amount"].mean()), 2),
            "average_review_rating": round(float(df["review_rating"].mean()), 2),
            "total_revenue": round(float(df["purchase_amount"].sum()), 2),
        },
        "revenue_by_category": df.groupby("category", as_index=False)["purchase_amount"]
        .sum()
        .rename(columns={"purchase_amount": "total_revenue"})
        .sort_values("total_revenue", ascending=False),
        "revenue_by_subscription_status": revenue_by_subscription_status,
        "customer_lifetime_segments": customer_lifetime_segments,
        "rfm_segment_summary": rfm_segment_summary,
        "top_locations": top_locations,
        "priority_tier_summary": priority_tiers,
        "payment_summary": payment_summary,
        "customer_segments": segment_series.value_counts()
        .rename_axis("customer_segment")
        .reset_index(name="customer_count"),
    }
