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

## Future Phases (Pending)

- Phase 4: ML Model Training
- Phase 5: Model Evaluation
- Phase 6: Prediction Engine
- Phase 7: Explainable AI (SHAP)
- Phase 8: Lifestyle NLP
- Phase 9: Multimodal Risk Engine
- Phase 10: Emergency Alerts (Twilio)

## Medical Disclaimer

HeartGuard is an academic/research prototype and is not a medical diagnostic system.

## License

This project is for academic/research purposes only.
