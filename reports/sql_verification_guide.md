# SQL Verification Guide

## Local Validation Workflow

Run the full customer pipeline and validate the SQL pack locally:

```bash
python3 python/customer_behavior_revenue_insights.py --load-to-sqlite
python3 python/validate_customer_sql.py
```

## What The Workflow Does

- cleans and standardizes the raw customer dataset
- writes the processed file into `data/processed/`
- creates the local SQLite database at `data/processed/customer_behavior.db`
- executes every query in `sql/customer_behavior_revenue_queries.sql`

## Optional Export Step

To regenerate the query-level CSV and SQL outputs used in the reports:

```bash
python3 python/export_customer_sql_results.py
```

## Business Use

This verification flow keeps the SQL layer reliable for portfolio review, recruiter demonstrations, and future dashboard refreshes.
