from __future__ import annotations

import argparse
import os
import sqlite3
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
from sqlalchemy import create_engine

from data_access import PROCESSED_DATA_PATH, SQLITE_DB_PATH, resolve_source_path
from feature_engineering import clean_customer_behavior_data
from kpi_metrics import build_summary_tables


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TABLE_NAME = "customer"


def load_raw_data(path: Path | str | None = None, prefer_sample: bool = False) -> pd.DataFrame:
    source_path = Path(path) if path else resolve_source_path(prefer_sample=prefer_sample)
    return pd.read_csv(source_path)


def save_processed_data(df: pd.DataFrame, path: Path | str = PROCESSED_DATA_PATH) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return output_path


def save_summary_tables(summary_tables: dict[str, object], output_dir: Path = PROCESSED_DATA_PATH.parent) -> list[Path]:
    saved_paths: list[Path] = []
    output_dir.mkdir(parents=True, exist_ok=True)

    for table_name, value in summary_tables.items():
        if table_name == "kpis":
            kpi_df = pd.DataFrame(
                [{"metric": metric, "value": metric_value} for metric, metric_value in value.items()]
            )
            output_path = output_dir / "customer_kpis.csv"
            kpi_df.to_csv(output_path, index=False)
            saved_paths.append(output_path)
            continue

        if isinstance(value, pd.DataFrame):
            output_path = output_dir / f"{table_name}.csv"
            value.to_csv(output_path, index=False)
            saved_paths.append(output_path)

    return saved_paths


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
        connection_string = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
    elif db_type == "mysql":
        connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
    elif db_type == "sqlserver":
        driver_name = quote_plus(driver or "ODBC Driver 17 for SQL Server")
        connection_string = f"mssql+pyodbc://{username}:{password}@{host},{port}/{database}?driver={driver_name}"
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
        description="Clean, segment, and optionally load customer behavior data."
    )
    parser.add_argument("--source", default="", help="Optional explicit path to the raw CSV file.")
    parser.add_argument("--use-sample", action="store_true", help="Use the GitHub-safe sample dataset.")
    parser.add_argument("--output", default=str(PROCESSED_DATA_PATH), help="Path to save the cleaned dataset.")
    parser.add_argument("--skip-csv-export", action="store_true", help="Skip writing the cleaned CSV file.")
    parser.add_argument("--load-to-db", action="store_true", help="Load the cleaned dataset into a database table.")
    parser.add_argument("--load-to-sqlite", action="store_true", help="Load the cleaned dataset into local SQLite.")
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
    parser.add_argument("--db-table", default=os.getenv("CUSTOMER_DB_TABLE", DEFAULT_TABLE_NAME))
    parser.add_argument("--db-if-exists", choices=["fail", "replace", "append"], default="replace")
    parser.add_argument(
        "--db-driver",
        default=os.getenv("CUSTOMER_DB_DRIVER", "ODBC Driver 17 for SQL Server"),
        help="ODBC driver name used only for SQL Server connections.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_df = load_raw_data(args.source or None, prefer_sample=args.use_sample)
    cleaned_df = clean_customer_behavior_data(raw_df)
    summaries = build_summary_tables(cleaned_df)

    print("Customer Behavior & Revenue Insights Pipeline Summary")
    for key, value in summaries["kpis"].items():
        print(f"- {key}: {value}")

    if not args.skip_csv_export:
        output_path = save_processed_data(cleaned_df, args.output)
        print(f"- cleaned_csv: {output_path}")
        for saved_summary in save_summary_tables(summaries):
            print(f"- summary_output: {saved_summary}")

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
