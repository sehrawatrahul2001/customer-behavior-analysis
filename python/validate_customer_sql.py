from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from customer_behavior_revenue_insights import (
    DEFAULT_TABLE_NAME,
    PROCESSED_DATA_PATH,
    SQLITE_DB_PATH,
    clean_customer_behavior_data,
    load_raw_data,
    load_to_sqlite,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SQL_FILE_PATH = PROJECT_ROOT / "sql" / "customer_behavior_revenue_queries.sql"


def split_sql_queries(sql_text: str) -> list[str]:
    queries: list[str] = []
    current_lines: list[str] = []

    for line in sql_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        current_lines.append(line)
        if stripped.endswith(";"):
            query = "\n".join(current_lines).strip().rstrip(";")
            if query:
                queries.append(query)
            current_lines = []

    if current_lines:
        query = "\n".join(current_lines).strip().rstrip(";")
        if query:
            queries.append(query)

    return queries


def ensure_sqlite_database() -> Path:
    if PROCESSED_DATA_PATH.exists():
        df = pd.read_csv(PROCESSED_DATA_PATH)
    else:
        raw_df = load_raw_data()
        df = clean_customer_behavior_data(raw_df)
    return load_to_sqlite(df)


def main() -> None:
    sqlite_path = ensure_sqlite_database()
    queries = split_sql_queries(SQL_FILE_PATH.read_text())

    print(f"SQLite database ready: {sqlite_path}")
    print(f"Verifying {len(queries)} SQL queries from {SQL_FILE_PATH.name}")

    for index, query in enumerate(queries, start=1):
        preview = " ".join(query.split())[:120]
        with sqlite3.connect(sqlite_path) as connection:
            result = pd.read_sql_query(query, connection)
        print(f"\nQuery {index}: OK")
        print(f"Preview: {preview}")
        print(result.head(5).to_string(index=False))

    print(f"\nAll SQL queries executed successfully against the `{DEFAULT_TABLE_NAME}` table.")


if __name__ == "__main__":
    main()
