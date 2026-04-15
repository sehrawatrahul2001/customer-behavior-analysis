# Customer Behavior & Revenue Insights Analysis

This project evaluates retail customer behavior through the lens of revenue quality, repeat-purchase momentum, subscription engagement, and category demand. It was developed by **Rahul Sehrawat**, **Assistant Manager (Operations)**, as part of a transition into Data Analytics with a clear focus on business storytelling rather than generic dashboard output.

## Business Objective

The goal is to convert transaction-level customer data into decisions a retail leadership team can act on:

- which customer segments deserve stronger retention investment
- where subscription behavior signals higher engagement
- which categories and locations create the strongest revenue contribution
- how discounts, shipping, and payment choices influence commercial outcomes

## Project Snapshot

| Area | Details |
|---|---|
| Project Name | Customer Behavior & Revenue Insights Analysis |
| Domain | Retail customer analytics |
| Data Scale | 3,900 customer shopping records |
| Tools Used | Python, Pandas, SQL, SQLite, Power BI |
| Positioning | Revenue analysis, customer segmentation, retention strategy, operational storytelling |

## Workflow

1. Raw customer shopping data is cleaned and standardized in Python.
2. Analytical fields such as `age_group`, `purchase_frequency_days`, and `customer_lifetime_segment` are engineered for business use.
3. SQL queries translate the cleaned dataset into decision-ready customer and revenue views.
4. Dashboard notes and reports convert the analysis into stakeholder-facing recommendations.

## Headline Insights

- Revenue is concentrated in customers with stronger purchase history, reinforcing the value of retention over one-time acquisition.
- Subscription status acts as a strong engagement marker and should be treated as a practical proxy for customer value.
- Clothing and accessories lead revenue contribution, making them strong candidates for targeted campaigns and inventory support.
- Discount usage influences demand, but broad discounting is less effective than segment-specific pricing action.
- Location, shipping preference, and payment behavior reveal clear opportunities for more precise commercial targeting.

## Repository Structure

```text
Customer Behavior & Revenue Insights Analysis/
├── data/
├── python/
├── sql/
├── dashboard/
├── reports/
├── README.md
└── project_storyline.md
```

## Key Files

- `python/customer_behavior_revenue_insights.py`
- `python/validate_customer_sql.py`
- `python/export_customer_sql_results.py`
- `python/customer_behavior_revenue_insights.ipynb`
- `sql/customer_behavior_revenue_queries.sql`
- `dashboard/dashboard_brief.md`
- `reports/business_problem_report.md`
- `reports/final_insights_report.md`
- `reports/sql_validation_report.md`

## How To Run

```bash
python3 python/customer_behavior_revenue_insights.py --load-to-sqlite
python3 python/validate_customer_sql.py
python3 python/export_customer_sql_results.py
```

## Why This Project Stands Out

This case study is intentionally framed like a retail decision-support engagement. It reflects Rahul Sehrawat's operations background by focusing on retention economics, customer quality, and practical business action instead of only descriptive charts.
