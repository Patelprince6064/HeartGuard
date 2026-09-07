"""HeartGuard centralized configuration."""

from pathlib import Path

# Project metadata
PROJECT_NAME = "HeartGuard"
PROJECT_VERSION = "0.1.0"

# Risk scoring weights
CLINICAL_WEIGHT = 0.70
LIFESTYLE_WEIGHT = 0.30

# Risk thresholds (percentage)
RISK_THRESHOLD_LOW = 60
RISK_THRESHOLD_MODERATE = 75
RISK_THRESHOLD_HIGH = 85
RISK_THRESHOLD_CRITICAL = 85

# Base directory (project root)
BASE_DIR = Path(__file__).resolve().parent.parent

# Directory paths
MODEL_DIRECTORY = BASE_DIR / "models"
DATA_DIRECTORY = BASE_DIR / "data"
RAW_DATA_DIRECTORY = DATA_DIRECTORY / "raw"
PROCESSED_DATA_DIRECTORY = DATA_DIRECTORY / "processed"
ALERT_DIRECTORY = DATA_DIRECTORY / "alerts"
REPORT_DIRECTORY = BASE_DIR / "reports"
NOTEBOOK_DIRECTORY = BASE_DIR / "notebooks"
ASSETS_DIRECTORY = BASE_DIR / "assets"

# Ensure directories exist
MODEL_DIRECTORY.mkdir(exist_ok=True)
PROCESSED_DATA_DIRECTORY.mkdir(exist_ok=True)
ALERT_DIRECTORY.mkdir(exist_ok=True)
REPORT_DIRECTORY.mkdir(exist_ok=True)
