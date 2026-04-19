from __future__ import annotations

from bootstrap_data import main as bootstrap_main
from customer_behavior_revenue_insights import main as pipeline_main
from export_customer_sql_results import main as export_main
from validate_customer_sql import main as validate_main


def main() -> None:
    bootstrap_main()
    pipeline_main()
    validate_main()
    export_main()


if __name__ == "__main__":
    main()
