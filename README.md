# HeartGuard

## Overview

HeartGuard is an academic/research prototype for early heart disease risk prediction using Explainable AI. The system combines clinical data analysis, machine learning, and lifestyle text analysis to provide comprehensive heart disease risk assessments.

## Project Objective

To develop a multimodal heart disease risk prediction system that:

1. Analyzes clinical patient data using machine learning
2. Provides explainable predictions using SHAP
3. Assesses lifestyle risk factors through NLP
4. Combines clinical and lifestyle risk into a unified score
5. Sends emergency alerts for critical risk cases

## Planned Modules

| Module | Description | Phase |
|--------|-------------|-------|
| Risk Prediction Engine | ML-based clinical risk assessment | 4-6 |
| Explainability Module | SHAP-based prediction explanations | 7 |
| Lifestyle Analyzer | NLP-based lifestyle risk analysis | 8 |
| Multimodal Risk Engine | Combined clinical + lifestyle scoring | 9 |
| Emergency Alert System | Twilio SMS notifications | 10 |
| Streamlit Dashboard | Interactive web interface | 11-12 |
| PDF Reports | Generated patient reports | 13 |

## Technology Stack

- **Language:** Python 3.12+
- **Web Framework:** Streamlit
- **ML Libraries:** scikit-learn, XGBoost, TensorFlow
- **Explainability:** SHAP
- **NLP:** NLTK
- **Visualization:** Matplotlib, Plotly
- **Notifications:** Twilio
- **Testing:** pytest

## Project Structure

```
HeartGuard/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── config/
│   └── settings.py           # Centralized configuration
├── data/
│   ├── raw/                  # Original datasets
│   ├── processed/            # Cleaned datasets
│   └── alerts/               # Alert logs
├── docs/                     # Documentation
├── models/                   # Trained model artifacts
├── reports/                  # Evaluation reports
├── notebooks/                # Jupyter notebooks
├── src/
│   ├── data/                 # Data loading & preprocessing
│   ├── ml/                   # ML training & prediction
│   ├── explainability/       # SHAP implementation
│   ├── nlp/                  # Lifestyle text analysis
│   ├── alerts/               # Emergency notifications
│   └── utils/                # Shared utilities
├── pages/                    # Streamlit pages
├── assets/                   # Static assets
└── tests/                    # Automated tests
```

## Installation

1. Clone the repository
2. Create virtual environment: `python -m venv .venv`
3. Activate virtual environment (Windows: `.venv\Scripts\activate`)
4. Install dependencies: `pip install -r requirements.txt`
5. Configure environment variables: copy `.env.example` `.env`
6. Run the application: `streamlit run app.py`

---

## Phase 1: Project Foundation (DONE)

- Project structure created
- Configuration system implemented
- Logging foundation established
- Validation utilities created
- Streamlit application scaffolded
- Testing foundation set up

## Phase 2: Dataset Integration & Preprocessing (DONE)

### Datasets

| Dataset | Role | Source |
|---------|------|--------|
| Cleveland Heart Disease | PRIMARY | UCI ML Repository / Kaggle |
| Framingham Heart Study | SECONDARY | Framingham Study |

### Canonical Schema

The Cleveland dataset is mapped to a canonical HeartGuard schema:

| Canonical Name | Source Name(s) | Type |
|---------------|----------------|------|
| `age` | `age` | Numerical |
| `sex` | `sex` | Categorical |
| `chest_pain_type` | `cp` | Categorical |
| `resting_bp` | `trestbps` | Numerical |
| `cholesterol` | `chol` | Numerical |
| `fasting_blood_sugar` | `fbs` | Categorical |
| `resting_ecg` | `restecg` | Categorical |
| `max_heart_rate` | `thalach` | Numerical |
| `exercise_angina` | `exang` | Categorical |
| `st_depression` | `oldpeak` | Numerical |
| `num_major_vessels` | `ca` | Numerical |
| `target` | `target` | Binary (0/1) |

### Data Validation

- **Schema validation:** Verifies all required columns are present after mapping
- **Missing value analysis:** Reports per-column missing counts and percentages
- **Duplicate analysis:** Detects and reports exact duplicate rows
- **Invalid value detection:** Checks clinical ranges (age, BP, cholesterol, etc.)
- **Outlier detection:** IQR-based detection reported but not auto-removed

### Target Processing

The Cleveland target is normalized to binary:
- `0` = absence of heart disease
- `1` = presence of heart disease

Original severity values (0-4) are mapped: `0 -> 0`, `1+ -> 1`.

### Preprocessing Pipeline

- **Numerical features:** Median imputation + MinMaxScaler
- **Categorical features:** Most-frequent imputation + OneHotEncoder
- **No data leakage:** Preprocessor is fit ONLY on training data after train/test split
- **Unknown categories:** Handled gracefully via `handle_unknown="ignore"`

### Train/Test Split

- 80/20 split with stratification on the target variable
- Random state: 42 (reproducible)

### Data Leakage Prevention

```
Raw dataset
    ↓
Train/test split (80/20, stratified)
    ↓
Fit preprocessor on training data ONLY
    ↓
Transform training data
    ↓
Transform test data (using fitted preprocessor)
```

### Key API

```python
from src.data.loader import load_cleveland_dataset, prepare_cleveland_dataset
from src.data.preprocessing import (
    split_dataset,
    create_preprocessor,
    fit_preprocessor,
    transform_data,
)

df = prepare_cleveland_dataset()
X_train, X_test, y_train, y_test = split_dataset(df)
preprocessor = fit_preprocessor(X_train)
X_train_t, X_test_t = transform_data(preprocessor, X_train, X_test)
```

### Running Tests

```bash
pytest -q
```

## Phase 3: Data Pipeline & Exploratory Data Analysis (DONE)

### End-to-End Pipeline

The pipeline module provides a single entry point that handles the complete data preparation flow:

```python
from src.data.pipeline import prepare_cleveland_pipeline

result = prepare_cleveland_pipeline()

X_train = result.X_train
X_test  = result.X_test
y_train = result.y_train
y_test  = result.y_test
preprocessor = result.preprocessor
feature_names = result.feature_names
metadata = result.metadata
```

### Pipeline Steps

1. Load raw dataset
2. Normalise columns and validate schema
3. Clean duplicates and analyse missing values
4. Prepare target (binary 0/1)
5. Split 80/20 stratified
6. Fit preprocessor on training data ONLY
7. Transform train and test data
8. Save artefacts (preprocessor, processed CSVs, reports)
9. Return ML-ready datasets + metadata

### Preprocessing

| Component | Strategy |
|-----------|----------|
| Numerical imputation | Median (fitted on train only) |
| Numerical scaling | **MinMaxScaler** (fitted on train only) |
| Categorical imputation | Most-frequent (fitted on train only) |
| Categorical encoding | OneHotEncoder(handle_unknown='ignore') |

### Deterministic Feature Ordering

A fixed feature order (`HEARTGUARD_FEATURES`) is used across training, evaluation, prediction, SHAP, and Streamlit input:

```
age, sex, chest_pain_type, resting_bp, cholesterol,
fasting_blood_sugar, resting_ecg, max_heart_rate,
exercise_angina, st_depression, num_major_vessels
```

### Cross-Validation Utility

```python
from src.ml.cross_validation import create_cv_strategy

cv = create_cv_strategy()  # StratifiedKFold, 5 folds
```

### Artefacts Generated

| Artefact | Location |
|----------|----------|
| Training data | `data/processed/cleveland_train.csv` |
| Test data | `data/processed/cleveland_test.csv` |
| Clean data | `data/processed/cleveland_clean.csv` |
| Fitted preprocessor | `models/preprocessor.pkl` |
| Data quality report | `reports/data_quality/cleveland_data_quality.json` |
| EDA summary | `reports/data_quality/cleveland_eda_summary.json` |
| Dataset metadata | `reports/data_quality/dataset_metadata.json` |
| Leakage check | `reports/data_quality/data_leakage_check.json` |

### Documentation

- `docs/data_dictionary.md` — Feature definitions, types, ranges
- `docs/data_pipeline.md` — Pipeline flow and architecture

### Running Tests

```bash
# Full test suite (114 tests)
pytest -q

# Pipeline tests only
pytest tests/test_pipeline.py -v
```

---

## Phase 4: Machine Learning Models & Evaluation (DONE)

### Models Implemented

| Model | Class | Hyperparameter Tuning | Explainer Compatibility |
|-------|-------|----------------------|-------------------------|
| Logistic Regression | `LogisticRegression` | Grid search (C, penalty, solver) | LinearExplainer |
| Random Forest | `RandomForestClassifier` | Grid search (n_estimators, max_depth) | TreeExplainer |
| XGBoost | `XGBClassifier` | Grid search (learning_rate, max_depth) | TreeExplainer |
| Neural Network (MLP) | `MLPClassifier` | Grid search (hidden_layer_sizes, alpha) | KernelExplainer |

### Cross-Validation & Model Selection

- 5-fold Stratified K-Fold cross-validation
- ROC-AUC metric optimization with secondary F1 evaluation
- Artifacts: models saved to `models/`, evaluation metrics in `reports/model_results.json`, confusion matrices and ROC curves in `reports/figures/`

---

## Phase 5: Explainable AI with SHAP (DONE)

HeartGuard incorporates explainable artificial intelligence (XAI) using SHAP (SHapley Additive exPlanations) to provide mathematical transparency and clinical interpretability for heart disease predictions.

### Key Capabilities

1. **TreeExplainer & Model-Specific Explainers**:
   - `TreeExplainer` for tree-based models (XGBoost, Random Forest) with exact Shapley value computation
   - `LinearExplainer` for linear models (Logistic Regression)
   - `KernelExplainer` fallback for arbitrary model architectures
   - Dynamic explainer selection via `create_shap_explainer()`

2. **Global Feature Importance**:
   - Computes mean absolute SHAP values across the training population
   - Exports ranked feature importance table to `reports/explainability/shap_global_importance.csv`
   - Generates global importance horizontal bar chart (`reports/figures/shap_global_importance.png`)
   - Generates SHAP beeswarm summary plot (`reports/figures/shap_summary.png`)

3. **Local Patient-Level Explanations**:
   - Exact per-feature attribution for individual patient predictions
   - **SHAP Waterfall Plot**: Visualizes how each clinical attribute pushes risk above or below baseline log-odds/probability (`reports/figures/shap_waterfall.png`)
   - **Feature Contribution Plot**: Visualizes local feature importance and direction (`reports/figures/shap_local_importance.png`)
   - Structured JSON export for EHR integration (`reports/explainability/shap_local_explanation.json`)

4. **Human-Readable Clinical Explanations**:
   - Translates numerical Shapley values into clear, plain-language clinical narratives
   - Identifies top risk-increasing and risk-mitigating factors with clinical labels
   - Disclaimers highlighting model interpretation vs clinical diagnosis

5. **Top Risk Factors**:
   - Extracts top $N$ (default 3) features driving positive risk for targeted clinical review

6. **Interactive Streamlit Interface**:
   - Accessible via the "Explainable AI" page (`pages/explainable_ai.py`)
   - Interactive patient input sliders and inputs
   - Real-time prediction, probability, waterfall plot, and top risk breakdown
   - One-click global population importance computation

7. **Offline CLI Tool**:
   - `python scripts/generate_shap_reports.py` generates all global artifacts without starting the UI

### Artefacts Generated

| Artefact | Path |
|----------|------|
| Global Importance CSV | `reports/explainability/shap_global_importance.csv` |
| Explainer Metadata JSON | `reports/explainability/explainer_metadata.json` |
| Local Explanation JSON | `reports/explainability/shap_local_explanation.json` |
| Global Feature Importance Plot | `reports/figures/shap_global_importance.png` |
| SHAP Summary Beeswarm Plot | `reports/figures/shap_summary.png` |
| Waterfall Plot | `reports/figures/shap_waterfall.png` |
| Local Importance Plot | `reports/figures/shap_local_importance.png` |

### Running Tests

```bash
# Run all tests (196 passing)
pytest -q

# Run Phase 5 SHAP tests only (40 passing)
pytest tests/test_shap.py -v
```

---

## Phase 6: Lifestyle Text Analyzer / NLP Module (DONE)

HeartGuard provides an explainable, rule-based NLP module that analyzes free-text patient lifestyle descriptions to identify cardiovascular risk signals and calculate a quantified lifestyle score (0–100).

### Key Capabilities

1. **Predefined Risk Lexicon & Scoring**:
   - Centralized risk weights and severities across 6 key lifestyle domains:
     - **Smoking**: +25 points (High severity)
     - **Family History**: +20 points (High severity)
     - **Unhealthy Diet**: +18 points (Moderate severity)
     - **Physical Inactivity**: +15 points (High severity)
     - **Poor Sleep**: +12 points (Moderate severity)
     - **Alcohol Use**: +10 points (Low severity)
   - **Score Cap**: Mathematically capped at 100 points
   - **Risk Categories**: `LOW` (0–29), `MODERATE` (30–59), `HIGH` (60–84), `CRITICAL` (85–100)

2. **NLTK Text Preprocessing & Fallbacks**:
   - Text normalization, punctuation preservation for decimals (e.g. *5.5 hours*), and whitespace standardization
   - NLTK `punkt`/`punkt_tab` tokenization with offline regex fallback

3. **Intelligent Rule-Based Matching**:
   - **Multi-Word Phrase Matching**: Prioritizes longer phrases (*"no regular exercise"*, *"family history of heart attack"*)
   - **Negation Detection**: Recognizes preceding negation cues (*"do not smoke"*, *"don't drink alcohol"*, *"avoid junk food"*)
   - **Alcohol Disambiguation**: Prevents non-alcoholic drinks (*"drink 3 liters of water"*, *"drink coffee"*) from triggering alcohol risk
   - **Quantitative Sleep Detection**: Parses numeric sleep duration (< 6 hours triggers Poor Sleep; ≥ 6 hours is adequate)
   - **Positive Exercise Recognition**: Counters false-positive inactivity flags when active exercise habits are noted

4. **Streamlit Lifestyle Analyzer**:
   - Interactive UI at `pages/lifestyle_analyzer.py`
   - Real-time score meter, category badges, detected risk factor evidence table, and risk breakdown charts
   - Patient-friendly clinical narratives and top 3 risk factors

### Running Tests

```bash
# Full test suite (222 passing)
pytest -q

# Phase 6 Lifestyle NLP tests only (26 passing)
pytest tests/test_lifestyle_analyzer.py -v
```

---

## Phase 7: Multimodal Risk Integration (DONE)

HeartGuard unifies objective clinical machine learning predictions with qualitative lifestyle text analysis into a single multimodal cardiovascular risk assessment engine.

### Key Capabilities

1. **70/30 Multimodal Weighting**:
   - **Formula**: $\text{Overall Risk} = (\text{Clinical Risk} \times 0.70) + (\text{Lifestyle Risk} \times 0.30)$
   - **Clinical ML Risk (70%)**: Positive-class probability from the best trained clinical model (e.g. Logistic Regression, XGBoost, Random Forest, or MLP), scaled to $0 - 100\%$.
   - **Lifestyle Risk (30%)**: Quantified risk score ($0 - 100$) derived from the NLTK rule-based lifestyle analyzer.

2. **Operational Decision Thresholds**:
   - **Critical Risk ($> 85\%$)**: `CRITICAL` alert level $\rightarrow$ *"Immediate medical consultation recommended."*
   - **Elevated Risk ($60\% - 85\%$)**: `APPOINTMENT_RECOMMENDED` alert level $\rightarrow$ *"Medical appointment recommendation."*
   - **Lower / Baseline Risk ($< 60\%$)**: `MONITORING` alert level $\rightarrow$ *"Regular monitoring recommended."*
   - *Note: This phase calculates the alert state but does not send notifications.*

3. **Unified Multimodal Streamlit Interface**:
   - Live on `pages/risk_assessment.py`.
   - Organised forms for demographics, physiological measurements, and diagnostic test results.
   - Text area for self-reported lifestyle narrative.
   - Dynamic overall risk score gauge, category banners, contribution breakdown tables, and component comparison charts.
   - Embedded SHAP waterfall plots and lifestyle evidence summaries.

4. **Status Dashboard Integration**:
   - Updated `pages/dashboard.py` showing live operational status for the Multimodal Engine, Clinical ML Model, SHAP Explainability, and Lifestyle NLP Analyzer.

### Running Tests

```bash
# Full test suite (244 passing)
pytest -q

# Phase 7 Multimodal Risk Engine tests only (22 passing)
pytest tests/test_multimodal_risk.py -v
```

---

## Phase 8: Emergency Alert & Notification System (DONE)

HeartGuard provides an automated emergency notification module to dispatch urgent alerts when a multimodal risk evaluation indicates critical cardiovascular risk.

### Key Capabilities

1. **Threshold-Based Emergency Triage**:
   - Strictly triggered when multimodal risk $> 85.0\%$ (`CRITICAL`).
   - Non-critical scores ($\le 85.0\%$) are logged with `NOT_TRIGGERED` without contacting external dispatchers.

2. **Twilio SMS Dispatch**:
   - Formatted SMS notifications sent to registered clinician and emergency contact numbers.
   - Idempotent alert dispatch prevents duplicate SMS transmissions for the same assessment ID.

3. **Privacy & Demo Mode**:
   - Phone numbers are masked (`+1*****4567`) in all user interfaces and audit logs.
   - Configurable `ALERTS_ENABLED` flag runs in Demo Mode by default to prevent unintended dispatches during development/testing.

---

## Phase 9: Security, Authentication & Production Hardening (DONE)

HeartGuard implements an end-to-end security architecture tailored for academic and clinical demo deployment.

### Key Capabilities

1. **Authentication & Password Security**:
   - Secure credential storage using **bcrypt** with a work factor of **12 rounds**.
   - Timing-attack resistant verification with generic error responses to prevent user enumeration.
   - Safe model serialization (`to_safe_dict()`) ensuring password hashes are never exposed.

2. **Role-Based Access Control (RBAC)**:
   - Two distinct roles: `PATIENT` and `ADMIN`.
   - Patients can access personal risk calculations and lifestyle assessments.
   - Administrators manage system configuration, audit logs, user accounts, and deep model explainability diagnostics.
   - Admin account provisioning is strictly restricted to an out-of-band CLI tool (`scripts/create_admin.py`).

3. **Input Validation & Sanitization**:
   - Comprehensive sanitization against Cross-Site Scripting (XSS) and SMS header injection.
   - Strict length bounds on email (255 chars), name (100 chars), password (min 8 chars), and lifestyle narratives (5,000 chars).

4. **Security Audit Logging & Rate Limiting**:
   - Structured security events recorded in an isolated SQLite database (`data/security/audit.db`).
   - Session-state rate limiting on login attempts (5 attempts, 60s lockout) to thwart brute-force attacks.

5. **Patient Privacy Protection**:
   - Clinician and emergency phone numbers are masked across all UI surfaces and database records.
   - Free-form lifestyle narratives and raw clinical vectors are excluded from application and audit logs.

### Running Security Tests

```bash
# Run full test suite
pytest -q

# Run Phase 9 security and authentication tests
pytest tests/test_auth.py tests/test_authorization.py tests/test_security.py tests/test_alert_security.py -v
```

---

## Phase 10: Patient History, Analytics, Trends & Report Generation (DONE)

HeartGuard provides an assessment history, longitudinal trend tracking, and PDF report generation system.

### Key Capabilities

1. **Assessment History & Privacy Isolation**:
   - Historical evaluations stored in SQLite (`data/assessments/assessments.db`).
   - Server-level patient data isolation: queries strictly filter by authenticated `user_id`.
   - Ownership verification prevents cross-account data exposure.

2. **Longitudinal Risk Trends & Comparative Analytics**:
   - Chronological risk trajectory charts (Overall, Clinical ML 70%, Lifestyle NLP 30%).
   - Pairwise assessment comparison with explicit percentage-point changes (e.g. `+8.0 percentage points`).
   - Prudent, non-diagnostic model trend descriptions.

3. **Professional PDF Report Generation**:
   - Multi-page academic/research prototype PDF generated via **ReportLab**.
   - Contains executive risk summary, weighted multimodal breakdown, SHAP explainability drivers, trend charts, alert audit details, and medical disclaimers.
   - Secure filename sanitization prevents path traversal.

4. **Formula-Safe CSV Data Export**:
   - Patients can download their assessment history as CSV.
   - Sanitization neutralizes spreadsheet formula injection (`=`, `+`, `-`, `@`).

5. **Admin Aggregated Analytics**:
   - System-wide assessment counts, risk category distributions, model version usage, and alert statistics without exposing patient PII.

### Running Phase 10 Tests

```bash
# Run full test suite (316 passing)
pytest -q

# Run Phase 10 tests
pytest tests/test_assessment_history.py tests/test_report_generator.py -v
```

---

## Phase 11 — Doctor Review Portal

Phase 11 introduces a secure **Doctor Review Portal** for authorized `REVIEWER`-role
professionals to inspect AI assessment results and record structured observations.

### Key Features

- **Role-gated access** — `REVIEWER` role enforced server-side via `require_reviewer()`
- **Read-only AI panel** — risk scores, SHAP factors, narrative summary (never editable)
- **Professional review form** — status, follow-up flag, urgency flag, free-text notes
- **Data isolation** — reviews stored in separate `reviews.db` (assessments never modified)
- **Idempotent creation** — only one review per assessment, prevents duplicate records
- **Ownership enforcement** — reviewers can only update their own review records

### Clinical Safety

> ⚠️ This portal is **NOT** a diagnostic system. Professional notes are observations
> only — not diagnoses, prescriptions, or treatment plans. AI-generated risk scores
> cannot be modified through any review action.

### Provisioning a Reviewer Account

```bash
export REVIEWER_EMAIL=reviewer@heartguard.local
export REVIEWER_PASSWORD=<strong-password>
export REVIEWER_NAME="Dr. Jane Smith"
python scripts/create_reviewer.py
unset REVIEWER_PASSWORD
```

### Testing Phase 11

```bash
# Run Phase 11 tests (43 tests)
pytest tests/test_review_service.py tests/test_review_authorization.py -v
```

---

## Phase 12 — Advanced Dashboard & Visualization

Phase 12 upgrades HeartGuard into a modern, responsive, accessible AI healthcare research platform with specialized dashboards and reusable UI components.

### Key Features

- **Patient Dashboard** (`pages/dashboard.py`):
  - Personalized greeting and academic prototype disclaimer banner.
  - 5 KPI metric cards: Model-Based Risk, Risk Category badge, Total Assessments, Review Status badge, and Alert Status badge.
  - Latest assessment summary panel with comparative delta analysis against prior evaluations.
  - Risk component decomposition cards and Altair comparative chart (70% Clinical ML + 30% Lifestyle NLP).
  - Chronological multimodal risk trajectory trend line with bounded 0–100% scale and tooltips.
  - Explainable AI (SHAP) feature contribution chart strictly using non-diagnostic language.
  - Structured lifestyle insights cards (sleep, stress, exercise, diet, smoking, etc.).
  - Recent assessments table (5 latest records) with direct links to full history.
  - Quick action buttons (role-aware).
- **Reviewer Portal Enhancements** (`pages/review.py`):
  - Queue summary KPI cards (Pending, In Review, Reviewed, Follow-Up Recommended, Total Assigned).
  - Review queue distribution chart.
  - Integrated SHAP and risk component charts for assessment inspection.
- **Admin Dashboard Enhancements** (`pages/admin.py`):
  - System-wide aggregated analytics (Total Assessments, Assessed Patients, System Mean Risk, Total Reviews, Pending Queue).
  - Visual distribution charts for Risk Categories, Review Statuses, Alert Outcomes, and Model Version Usage.
  - Strict privacy preservation (no raw patient medical narratives or PII).
- **Reusable UI Design System** (`src/ui/`):
  - Standardized badges (`src/ui/badges.py`) with text + iconography for colorblind accessibility.
  - Standardized metric and summary cards (`src/ui/cards.py`).
  - Altair visualization helpers (`src/ui/charts.py`).
  - Data table renderers (`src/ui/tables.py`).
  - High-level layout components and safe error boundaries (`src/ui/dashboard_components.py`).

### Testing Phase 12

```bash
# Run Phase 12 tests (23 tests)
pytest tests/test_dashboard_analytics.py tests/test_ui_components.py tests/test_dashboard_security.py -v

# Run full regression suite (333 passing)
pytest -q --ignore=tests/test_auth.py --ignore=tests/test_authorization.py --ignore=tests/test_security.py
```

---

## Medical Disclaimer

HeartGuard is an academic/research prototype and is not a medical diagnostic system.

## License

This project is for academic/research purposes only.
