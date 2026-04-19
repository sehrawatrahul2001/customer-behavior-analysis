from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from customer_behavior_revenue_insights import SQLITE_DB_PATH
from validate_customer_sql import ensure_sqlite_database, split_sql_queries


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SQL_FILE_PATH = PROJECT_ROOT / "scripts" / "sql" / "customer_behavior_revenue_queries.sql"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "sql_query_results"
MARKDOWN_REPORT_PATH = PROJECT_ROOT / "reports" / "sql_validation_report.md"

QUERY_TITLES = [
    "Revenue by Gender",
    "Discounted Customers Spending Above Average",
    "Top Rated Products",
    "Average Purchase Amount by Shipping Type",
    "Subscriber vs Non-Subscriber Spend",
    "Products with Highest Discount Usage",
    "Customer Segmentation by Previous Purchases",
    "Top Products Within Each Category",
    "Subscription Mix Among Repeat Buyers",
    "Revenue Contribution by Age Group",
    "Payment Method Revenue Performance",
    "Top Revenue Locations with Subscription Share",
    "Customer Lifetime Segments by Shipping Behavior",
]


def dataframe_to_markdown_table(df: pd.DataFrame, max_rows: int = 12) -> str:
    display_df = df.copy()
    if display_df.empty:
        display_df = pd.DataFrame({"message": ["No rows returned"]})

    display_df = display_df.head(max_rows)
    headers = [str(column) for column in display_df.columns]
    separator = ["---"] * len(headers)
    rows = [[str(value) for value in row] for row in display_df.values.tolist()]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(separator) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def main() -> None:
    ensure_sqlite_database()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    queries = split_sql_queries(SQL_FILE_PATH.read_text())
    markdown_sections: list[str] = [
        "# SQL Validation Report",
        "",
        "These outputs were generated from the validated local SQLite database created from the cleaned `customer` table.",
        "",
    ]

    with sqlite3.connect(SQLITE_DB_PATH) as connection:
        for index, query in enumerate(queries, start=1):
            title = QUERY_TITLES[index - 1] if index - 1 < len(QUERY_TITLES) else f"Query {index}"
            slug = f"query_{index:02d}"
            result = pd.read_sql_query(query, connection)

            csv_path = OUTPUT_DIR / f"{slug}.csv"
            sql_path = OUTPUT_DIR / f"{slug}.sql"

            result.to_csv(csv_path, index=False)
            sql_path.write_text(query.strip() + ";\n")

            rel_csv = csv_path.relative_to(PROJECT_ROOT)
            rel_sql = sql_path.relative_to(PROJECT_ROOT)
            markdown_table = dataframe_to_markdown_table(result)

            markdown_sections.extend(
                [
                    f"## Query {index}. {title}",
                    "",
                    "```sql",
                    query.strip() + ";",
                    "```",
                    "",
                    f"CSV output: `{rel_csv}`  ",
                    f"SQL file: `{rel_sql}`",
                    "",
                    markdown_table,
                    "",
                ]
            )

    MARKDOWN_REPORT_PATH.write_text("\n".join(markdown_sections).strip() + "\n")
    print(f"Exported SQL results to: {OUTPUT_DIR}")
    print(f"Markdown report created at: {MARKDOWN_REPORT_PATH}")


if __name__ == "__main__":
    main()
