"""HeartGuard centralized configuration.

Loads all environment variables and provides a single source of truth
for application settings. Sensitive values are never hard-coded here.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env file if present (development only; production uses real env vars)
load_dotenv()

# ---------------------------------------------------------------------------
# Project metadata
# ---------------------------------------------------------------------------
PROJECT_NAME = "HeartGuard"
PROJECT_VERSION = "0.1.0"

# ---------------------------------------------------------------------------
# Risk scoring weights (Phase 7 — must not change)
# ---------------------------------------------------------------------------
CLINICAL_WEIGHT = 0.70
LIFESTYLE_WEIGHT = 0.30

# Risk thresholds (percentage)
RISK_THRESHOLD_LOW = 60
RISK_THRESHOLD_MODERATE = 75
RISK_THRESHOLD_HIGH = 85
RISK_THRESHOLD_CRITICAL = 85

# ---------------------------------------------------------------------------
# Base directory (project root)
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Directory paths
# ---------------------------------------------------------------------------
MODEL_DIRECTORY = BASE_DIR / "models"
DATA_DIRECTORY = BASE_DIR / "data"
RAW_DATA_DIRECTORY = DATA_DIRECTORY / "raw"
PROCESSED_DATA_DIRECTORY = DATA_DIRECTORY / "processed"
ALERT_DIRECTORY = DATA_DIRECTORY / "alerts"
AUTH_DATA_DIRECTORY = DATA_DIRECTORY / "auth"
SECURITY_DATA_DIRECTORY = DATA_DIRECTORY / "security"
ASSESSMENT_DATA_DIRECTORY = DATA_DIRECTORY / "assessments"
REPORT_DIRECTORY = BASE_DIR / "reports"
NOTEBOOK_DIRECTORY = BASE_DIR / "notebooks"
ASSETS_DIRECTORY = BASE_DIR / "assets"

# ---------------------------------------------------------------------------
# Database paths (Phase 9 + Phase 10)
# ---------------------------------------------------------------------------
AUTH_DB_PATH = AUTH_DATA_DIRECTORY / "heartguard_auth.db"
AUDIT_DB_PATH = SECURITY_DATA_DIRECTORY / "audit.db"
ALERTS_DB_PATH = ALERT_DIRECTORY / "alerts.db"
ASSESSMENTS_DB_PATH = ASSESSMENT_DATA_DIRECTORY / "assessments.db"
REVIEWS_DB_PATH = ASSESSMENT_DATA_DIRECTORY / "reviews.db"
RECOMMENDATIONS_DB_PATH = ASSESSMENT_DATA_DIRECTORY / "recommendations.db"
RECOMMENDATION_ENGINE_VERSION = "1.0.0"

# ---------------------------------------------------------------------------
# Evaluation configuration (Phase 14)
# ---------------------------------------------------------------------------
EVALUATION_DATA_DIRECTORY = DATA_DIRECTORY / "evaluations"
EVALUATION_DB_PATH = EVALUATION_DATA_DIRECTORY / "evaluation.db"
EVALUATION_ARTIFACTS_DIR = BASE_DIR / "artifacts" / "evaluation"
EVALUATION_RANDOM_STATE: int = 42
EVALUATION_TEST_SIZE: float = 0.20
EVALUATION_CV_FOLDS: int = 5
EVALUATION_ENGINE_VERSION: str = "1.0.0"

# ---------------------------------------------------------------------------
# Ensure directories exist
# ---------------------------------------------------------------------------
MODEL_DIRECTORY.mkdir(exist_ok=True)
PROCESSED_DATA_DIRECTORY.mkdir(exist_ok=True)
ALERT_DIRECTORY.mkdir(exist_ok=True)
AUTH_DATA_DIRECTORY.mkdir(exist_ok=True)
SECURITY_DATA_DIRECTORY.mkdir(exist_ok=True)
ASSESSMENT_DATA_DIRECTORY.mkdir(exist_ok=True)
REPORT_DIRECTORY.mkdir(exist_ok=True)
EVALUATION_DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
EVALUATION_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Twilio / Alert configuration (Phase 8)
# ---------------------------------------------------------------------------
TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")
DOCTOR_PHONE_NUMBER: str = os.getenv("DOCTOR_PHONE_NUMBER", "")
EMERGENCY_CONTACT_PHONE_NUMBER: str = os.getenv("EMERGENCY_CONTACT_PHONE_NUMBER", "")
ALERTS_ENABLED: bool = os.getenv("ALERTS_ENABLED", "false").lower() == "true"

# ---------------------------------------------------------------------------
# Application mode (Phase 9)
# ---------------------------------------------------------------------------
DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

# Demo mode: active when alerts are disabled (default safe state)
DEMO_MODE: bool = not ALERTS_ENABLED

# Secret key — used for any future signed-token needs; never displayed
SECRET_KEY: str = os.getenv("SECRET_KEY", "heartguard-change-in-production")

# ---------------------------------------------------------------------------
# Input limits (Phase 9)
# ---------------------------------------------------------------------------
LIFESTYLE_TEXT_MAX_LENGTH: int = 2000   # Characters; also enforced in NLP module
PASSWORD_MIN_LENGTH: int = 8
NAME_MAX_LENGTH: int = 100
EMAIL_MAX_LENGTH: int = 254             # RFC 5321

# ---------------------------------------------------------------------------
# Rate limiting (Phase 9) — Streamlit session-state based
# ---------------------------------------------------------------------------
LOGIN_MAX_ATTEMPTS: int = 5            # Per session
LOGIN_COOLDOWN_SECONDS: int = 60       # Cooldown period after max attempts

# ---------------------------------------------------------------------------
# User roles (Phase 9 / Phase 11)
# ---------------------------------------------------------------------------
ROLE_PATIENT = "PATIENT"
ROLE_ADMIN = "ADMIN"
ROLE_REVIEWER = "REVIEWER"   # Phase 11 — authorized professional reviewer
VALID_ROLES = {ROLE_PATIENT, ROLE_ADMIN, ROLE_REVIEWER}
