# Raw Data

The full customer dataset is stored locally in this folder and is intentionally excluded from GitHub.

Supported bootstrap paths:

- Local-first: keep the full CSV locally and set `CUSTOMER_BEHAVIOR_DATA_PATH`, or copy `data/data_sources.example.json` to `data/data_sources.json` and list your preferred file paths there.
- Google Drive: add the file ID to `data/data_sources.json` and run `python3 scripts/bootstrap_data.py`.
- Kaggle: add the dataset slug to `data/data_sources.json` and run `python3 scripts/bootstrap_data.py`.
- Sample fallback: if no full dataset is available, the pipeline will run using `data/sample/customer_shopping_behavior_sample.csv`.
