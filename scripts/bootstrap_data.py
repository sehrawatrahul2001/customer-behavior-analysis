from __future__ import annotations

from data_access import SAMPLE_DATA_PATH, bootstrap_customer_data


def main() -> None:
    data_path = bootstrap_customer_data()
    source_type = "sample" if data_path == SAMPLE_DATA_PATH else "raw"
    print(f"Customer dataset ready: {data_path} ({source_type})")


if __name__ == "__main__":
    main()
