from __future__ import annotations

import argparse
import os
import re
import sqlite3
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

import pandas as pd
from sqlalchemy import create_engine


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = PROJECT_ROOT / "data" / "customer_shopping_behavior.csv"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "customer_behavior_transformed.csv"
SQLITE_DB_PATH = PROJECT_ROOT / "data" / "processed" / "customer_behavior.db"
DEFAULT_TABLE_NAME = "customer"

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


def load_raw_data(path: Path | str = RAW_DATA_PATH) -> pd.DataFrame:
    return pd.read_csv(Path(path))


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned.columns = [
        re.sub(r"_+", "_", re.sub(r"[^0-9a-zA-Z]+", "_", column.strip().lower())).strip("_")
        for column in cleaned.columns
    ]
    cleaned = cleaned.rename(columns={"purchase_amount_usd": "purchase_amount"})
    return cleaned


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
    numeric_columns = ["customer_id", "age", "purchase_amount", "previous_purchases"]
    for column in numeric_columns:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="raise").astype(int)
    return cleaned


def add_age_group(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned["age_group"] = pd.qcut(cleaned["age"], q=4, labels=AGE_GROUP_LABELS)
    return cleaned


def add_purchase_frequency_days(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned["purchase_frequency_days"] = cleaned["frequency_of_purchases"].map(FREQUENCY_MAPPING)
    missing_frequency_labels = cleaned.loc[
        cleaned["purchase_frequency_days"].isna(), "frequency_of_purchases"
    ].dropna()
    if not missing_frequency_labels.empty:
        unexpected = ", ".join(sorted(missing_frequency_labels.astype(str).unique()))
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
    cleaned = drop_redundant_columns(cleaned)
    return cleaned


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
        "top_locations": top_locations,
        "customer_segments": segment_series.value_counts()
        .rename_axis("customer_segment")
        .reset_index(name="customer_count"),
    }


def save_processed_data(
    df: pd.DataFrame, path: Path | str = PROCESSED_DATA_PATH
) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return output_path


def build_database_engine(
    db_type: str,
    username: str,
    password: str,
    host: str,
    port: str,
    database: str,
    driver: str | None = None,
):
    if db_type == "postgresql":
        connection_string = (
            f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
        )
    elif db_type == "mysql":
        connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
    elif db_type == "sqlserver":
        driver_name = quote_plus(driver or "ODBC Driver 17 for SQL Server")
        connection_string = (
            f"mssql+pyodbc://{username}:{password}@{host},{port}/{database}?driver={driver_name}"
        )
    else:
        raise ValueError("db_type must be one of: postgresql, mysql, sqlserver")

    return create_engine(connection_string)


def load_to_database(
    df: pd.DataFrame,
    db_type: str,
    username: str,
    password: str,
    host: str,
    port: str,
    database: str,
    table_name: str = DEFAULT_TABLE_NAME,
    if_exists: str = "replace",
    driver: str | None = None,
) -> None:
    engine = build_database_engine(
        db_type=db_type,
        username=username,
        password=password,
        host=host,
        port=port,
        database=database,
        driver=driver,
    )
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)


def load_to_sqlite(
    df: pd.DataFrame,
    database_path: Path | str = SQLITE_DB_PATH,
    table_name: str = DEFAULT_TABLE_NAME,
    if_exists: str = "replace",
) -> Path:
    sqlite_path = Path(database_path)
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    if if_exists == "replace" and sqlite_path.exists():
        sqlite_path.unlink()
    with sqlite3.connect(sqlite_path) as connection:
        df.to_sql(table_name, connection, if_exists=if_exists, index=False)
    return sqlite_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clean, summarize, and optionally load customer behavior data into SQL."
    )
    parser.add_argument("--source", default=str(RAW_DATA_PATH), help="Path to the raw CSV file.")
    parser.add_argument(
        "--output",
        default=str(PROCESSED_DATA_PATH),
        help="Path to save the cleaned CSV file.",
    )
    parser.add_argument(
        "--skip-csv-export",
        action="store_true",
        help="Skip writing the cleaned dataset to a processed CSV file.",
    )
    parser.add_argument(
        "--load-to-db",
        action="store_true",
        help="Load the cleaned dataset into a database table.",
    )
    parser.add_argument(
        "--load-to-sqlite",
        action="store_true",
        help="Load the cleaned dataset into a local SQLite database for SQL verification.",
    )
    parser.add_argument(
        "--db-type",
        choices=["postgresql", "mysql", "sqlserver"],
        default=os.getenv("CUSTOMER_DB_TYPE", "postgresql"),
        help="Database backend used for the SQL layer.",
    )
    parser.add_argument("--db-host", default=os.getenv("CUSTOMER_DB_HOST", "localhost"))
    parser.add_argument("--db-port", default=os.getenv("CUSTOMER_DB_PORT", "5432"))
    parser.add_argument("--db-name", default=os.getenv("CUSTOMER_DB_NAME", "customer_behavior"))
    parser.add_argument("--db-user", default=os.getenv("CUSTOMER_DB_USER", ""))
    parser.add_argument("--db-password", default=os.getenv("CUSTOMER_DB_PASSWORD", ""))
    parser.add_argument(
        "--db-table",
        default=os.getenv("CUSTOMER_DB_TABLE", DEFAULT_TABLE_NAME),
        help="Destination table name for the cleaned dataset.",
    )
    parser.add_argument(
        "--db-if-exists",
        choices=["fail", "replace", "append"],
        default="replace",
        help="How pandas should behave if the table already exists.",
    )
    parser.add_argument(
        "--db-driver",
        default=os.getenv("CUSTOMER_DB_DRIVER", "ODBC Driver 17 for SQL Server"),
        help="ODBC driver name used only for SQL Server connections.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_df = load_raw_data(args.source)
    cleaned_df = clean_customer_behavior_data(raw_df)
    summaries = build_summary_tables(cleaned_df)

    print("Customer Behavior & Revenue Insights Pipeline Summary")
    for key, value in summaries["kpis"].items():
        print(f"- {key}: {value}")

    if not args.skip_csv_export:
        output_path = save_processed_data(cleaned_df, args.output)
        print(f"- cleaned_csv: {output_path}")

    if args.load_to_db:
        if not all([args.db_user, args.db_password, args.db_name]):
            raise ValueError(
                "Database credentials are required when --load-to-db is used. "
                "Set CLI arguments or CUSTOMER_DB_* environment variables."
            )
        load_to_database(
            cleaned_df,
            db_type=args.db_type,
            username=args.db_user,
            password=args.db_password,
            host=args.db_host,
            port=args.db_port,
            database=args.db_name,
            table_name=args.db_table,
            if_exists=args.db_if_exists,
            driver=args.db_driver,
        )
        print(f"- loaded_table: {args.db_table}")

    if args.load_to_sqlite:
        sqlite_path = load_to_sqlite(cleaned_df, table_name=args.db_table, if_exists=args.db_if_exists)
        print(f"- sqlite_database: {sqlite_path}")


if __name__ == "__main__":
    main()
