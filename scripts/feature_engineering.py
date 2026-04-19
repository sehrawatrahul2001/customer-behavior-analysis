from __future__ import annotations

import re

import pandas as pd


AGE_GROUP_LABELS = ["Young Adult", "Adult", "Middle-aged", "Senior"]
FREQUENCY_MAPPING = {
    "Fortnightly": 14,
    "Weekly": 7,
    "Monthly": 30,
    "Quarterly": 90,
    "Bi-Weekly": 14,
    "Annually": 365,
    "Every 3 Months": 90,
}


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned.columns = [
        re.sub(r"_+", "_", re.sub(r"[^0-9a-zA-Z]+", "_", column.strip().lower())).strip("_")
        for column in cleaned.columns
    ]
    return cleaned.rename(columns={"purchase_amount_usd": "purchase_amount"})


def impute_review_rating(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned["review_rating"] = pd.to_numeric(cleaned["review_rating"], errors="coerce")
    cleaned["review_rating"] = cleaned.groupby("category")["review_rating"].transform(
        lambda values: values.fillna(values.median())
    )
    cleaned["review_rating"] = cleaned["review_rating"].fillna(cleaned["review_rating"].median())
    return cleaned


def cast_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    for column in ["customer_id", "age", "purchase_amount", "previous_purchases"]:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="raise").astype(int)
    return cleaned


def add_age_group(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned["age_group"] = pd.qcut(cleaned["age"], q=4, labels=AGE_GROUP_LABELS)
    return cleaned


def add_purchase_frequency_days(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned["purchase_frequency_days"] = cleaned["frequency_of_purchases"].map(FREQUENCY_MAPPING)
    missing_labels = cleaned.loc[cleaned["purchase_frequency_days"].isna(), "frequency_of_purchases"].dropna()
    if not missing_labels.empty:
        unexpected = ", ".join(sorted(missing_labels.astype(str).unique()))
        raise ValueError(f"Unmapped frequency_of_purchases values found: {unexpected}")
    cleaned["purchase_frequency_days"] = cleaned["purchase_frequency_days"].astype(int)
    return cleaned


def add_customer_lifetime_segment(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()

    def classify_customer(row: pd.Series) -> str:
        if row["previous_purchases"] <= 2:
            return "New Customer"
        if row["previous_purchases"] >= 20 or row["purchase_amount"] >= 80:
            return "High-Value Customer"
        if row["previous_purchases"] >= 10 or row["subscription_status"] == "Yes":
            return "Loyal Customer"
        return "Growth Customer"

    cleaned["customer_lifetime_segment"] = cleaned.apply(classify_customer, axis=1)
    return cleaned


def add_rfm_proxy_segment(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned["recency_proxy"] = cleaned["purchase_frequency_days"].rank(pct=True, ascending=False)
    cleaned["frequency_score"] = pd.qcut(
        cleaned["previous_purchases"].rank(method="first"),
        q=4,
        labels=[1, 2, 3, 4],
    ).astype(int)
    cleaned["monetary_score"] = pd.qcut(
        cleaned["purchase_amount"].rank(method="first"),
        q=4,
        labels=[1, 2, 3, 4],
    ).astype(int)
    cleaned["recency_score"] = pd.qcut(
        cleaned["recency_proxy"].rank(method="first"),
        q=4,
        labels=[4, 3, 2, 1],
    ).astype(int)
    cleaned["rfm_score"] = (
        cleaned["recency_score"].astype(str)
        + cleaned["frequency_score"].astype(str)
        + cleaned["monetary_score"].astype(str)
    )
    cleaned["rfm_segment"] = "Mid-Value"
    cleaned.loc[cleaned["rfm_score"].isin({"444", "443", "434", "344"}), "rfm_segment"] = "Champions"
    cleaned.loc[cleaned["rfm_score"].isin({"144", "143", "244", "243"}), "rfm_segment"] = "New High Potential"
    cleaned.loc[cleaned["rfm_score"].isin({"111", "112", "121", "122"}), "rfm_segment"] = "At Risk"
    return cleaned


def add_customer_priority_fields(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    weighted_score = (
        cleaned["recency_score"] * 0.35
        + cleaned["frequency_score"] * 0.35
        + cleaned["monetary_score"] * 0.30
    )
    cleaned["customer_priority_score"] = (weighted_score / 4 * 100).round(2)
    cleaned["customer_priority_tier"] = pd.cut(
        cleaned["customer_priority_score"],
        bins=[0, 45, 65, 80, 100],
        labels=["Low Priority", "Nurture", "Retain", "Protect"],
        include_lowest=True,
    )
    cleaned["retention_risk_flag"] = "Normal"
    cleaned.loc[cleaned["rfm_segment"] == "At Risk", "retention_risk_flag"] = "High"
    cleaned.loc[
        (cleaned["rfm_segment"] == "New High Potential")
        | (cleaned["customer_lifetime_segment"] == "New Customer"),
        "retention_risk_flag",
    ] = "Medium"
    return cleaned


def drop_redundant_columns(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    if {"discount_applied", "promo_code_used"}.issubset(cleaned.columns):
        mismatch_count = (cleaned["discount_applied"] != cleaned["promo_code_used"]).sum()
        if mismatch_count:
            raise ValueError(
                "promo_code_used is not identical to discount_applied; refusing to drop the column."
            )
        cleaned = cleaned.drop(columns=["promo_code_used"])
    return cleaned


def clean_customer_behavior_data(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = standardize_columns(df)
    cleaned = impute_review_rating(cleaned)
    cleaned = cast_numeric_columns(cleaned)
    cleaned = add_age_group(cleaned)
    cleaned = add_purchase_frequency_days(cleaned)
    cleaned = add_customer_lifetime_segment(cleaned)
    cleaned = add_rfm_proxy_segment(cleaned)
    cleaned = add_customer_priority_fields(cleaned)
    cleaned = drop_redundant_columns(cleaned)
    return cleaned
