from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from urllib.request import urlretrieve


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
SAMPLE_DIR = DATA_DIR / "sample"
PROCESSED_DIR = DATA_DIR / "processed"
SOURCE_CONFIG_PATH = DATA_DIR / "data_sources.json"

RAW_DATASET_NAME = "customer_shopping_behavior.csv"
SAMPLE_DATASET_NAME = "customer_shopping_behavior_sample.csv"

RAW_DATA_PATH = RAW_DIR / RAW_DATASET_NAME
SAMPLE_DATA_PATH = SAMPLE_DIR / SAMPLE_DATASET_NAME
PROCESSED_DATA_PATH = PROCESSED_DIR / "customer_behavior_transformed.csv"
SQLITE_DB_PATH = PROCESSED_DIR / "customer_behavior.db"


def ensure_directory_layout() -> None:
    for directory in (RAW_DIR, SAMPLE_DIR, PROCESSED_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def load_source_config() -> dict[str, object]:
    if not SOURCE_CONFIG_PATH.exists():
        return {}
    return json.loads(SOURCE_CONFIG_PATH.read_text())


def get_local_candidates() -> list[Path]:
    config = load_source_config()
    config_paths = [Path(path).expanduser() for path in config.get("local_file_paths", []) if path]
    candidates = [
        RAW_DATA_PATH,
        DATA_DIR / RAW_DATASET_NAME,
        Path(os.getenv("CUSTOMER_BEHAVIOR_DATA_PATH", "")).expanduser(),
        Path("/Users/rahulsehrawat/Desktop/FINAL  MAIN PROJECTS/End-to-End Analytics Projects/Customer Behavior & Revenue Insights Analysis/data/raw/customer_shopping_behavior.csv"),
        *config_paths,
    ]
    return [path for path in candidates if str(path)]


def download_from_google_drive(file_id: str, destination: Path) -> bool:
    if not file_id:
        return False

    drive_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    try:
        urlretrieve(drive_url, destination)
        return destination.exists()
    except Exception:
        result = subprocess.run(
            ["python3", "-m", "gdown", "--fuzzy", drive_url, "-O", str(destination)],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0 and destination.exists()


def try_kaggle_download() -> None:
    config = load_source_config()
    kaggle_config = config.get("kaggle", {})
    if not isinstance(kaggle_config, dict):
        return

    dataset = str(kaggle_config.get("dataset", "")).strip()
    if not dataset:
        return

    subprocess.run(
        ["kaggle", "datasets", "download", "-d", dataset, "-p", str(RAW_DIR), "--unzip", "--force"],
        capture_output=True,
        text=True,
        check=False,
    )


def bootstrap_customer_data() -> Path:
    ensure_directory_layout()
    config = load_source_config()

    if RAW_DATA_PATH.exists():
        return RAW_DATA_PATH

    for candidate in get_local_candidates():
        if candidate.exists() and candidate != RAW_DATA_PATH:
            shutil.copy2(candidate, RAW_DATA_PATH)
            return RAW_DATA_PATH

    source_url = os.getenv("CUSTOMER_BEHAVIOR_DATA_URL", "").strip()
    if source_url:
        urlretrieve(source_url, RAW_DATA_PATH)
        return RAW_DATA_PATH

    google_drive_file_id = str(config.get("google_drive_file_id", "")).strip()
    if google_drive_file_id and download_from_google_drive(google_drive_file_id, RAW_DATA_PATH):
        return RAW_DATA_PATH

    config_url = str(config.get("direct_url", "")).strip()
    if config_url:
        urlretrieve(config_url, RAW_DATA_PATH)
        return RAW_DATA_PATH

    try_kaggle_download()
    if RAW_DATA_PATH.exists():
        return RAW_DATA_PATH

    if SAMPLE_DATA_PATH.exists():
        return SAMPLE_DATA_PATH

    raise FileNotFoundError(
        "Customer dataset not found. Provide a local path, direct URL, Google Drive file ID, "
        "Kaggle dataset slug, or keep the sample dataset in data/sample/."
    )


def resolve_source_path(prefer_sample: bool = False) -> Path:
    ensure_directory_layout()
    if prefer_sample and SAMPLE_DATA_PATH.exists():
        return SAMPLE_DATA_PATH
    return bootstrap_customer_data()
