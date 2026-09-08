# HeartGuard Viva Questions — Preparation Document

Comprehensive Q&A covering all major technical aspects of the HeartGuard project.

---

## Table of Contents

1. [Python & Software Engineering](#1-python--software-engineering)
2. [Machine Learning](#2-machine-learning)
3. [Explainability (SHAP)](#3-explainability-shap)
4. [NLP & Lifestyle Analysis](#4-nlp--lifestyle-analysis)
5. [Security](#5-security)
6. [Deployment](#6-deployment)
7. [Monitoring](#7-monitoring)

---

## 1. Python & Software Engineering

### Q: Why was Python chosen for this project?

**A:** Python was selected for three primary reasons:
1. **Readability** — Python's clean syntax aligns with the project's emphasis on transparency and explainability. The codebase follows PEP 8 conventions consistently.
2. **ML ecosystem** — scikit-learn, XGBoost, TensorFlow, SHAP, and NLTK all have mature, well-documented Python APIs. No other language offers this breadth of ML library support.
3. **Streamlit** — The frontend framework is Python-native, allowing a single language across the entire stack. This eliminated the need for a separate JavaScript/TypeScript frontend.

**Key reference:** `requirements.txt` lists all dependencies; `config/settings.py` centralizes all configuration.

---

### Q: Describe the project structure and design patterns used.

**A:** The project follows a modular, layered architecture:

```
HeartGuard/
├── app.py                    # Entry point (Streamlit app)
├── pages/                    # Streamlit pages (UI layer)
├── src/                      # Business logic (service layer)
│   ├── auth/                 # Authentication & RBAC
│   ├── data/                 # Data loading, preprocessing, pipeline
│   ├── ml/                   # Model training, evaluation, prediction
│   ├── explainability/       # SHAP integration
│   ├── nlp/                  # Lifestyle text analysis
│   ├── risk_engine/          # Multimodal risk calculation
│   ├── security/             # Input validation, audit logging, rate limiting
│   ├── alerts/               # Emergency SMS notifications
│   ├── analytics/            # Monitoring, drift detection, data quality
│   ├── recommendations/      # Clinical recommendation engine
│   ├── reports/              # PDF report generation
│   ├── review/               # Doctor review portal
│   ├── ui/                   # Reusable UI components
│   └── utils/                # Shared utilities, logging, exceptions
├── config/                   # Centralized configuration
│   ├── settings.py           # Environment, paths, weights
│   ├── security.py           # Security policies, rate limits
│   └── monitoring.py         # Monitoring thresholds
├── models/                   # Trained model artifacts (.pkl)
├── data/                     # SQLite databases, raw/processed data
├── reports/                  # Generated reports, evaluation metrics
├── tests/                    # 562 pytest tests
└── scripts/                  # CLI tools (create_admin, health_check)
```

**Design patterns used:**
- **Service layer pattern** — Business logic in `src/` is decoupled from UI in `pages/`
- **Repository pattern** — `src/auth/user_repository.py` abstracts database access
- **Strategy pattern** — SHAP explainer selection (`create_shap_explainer()`) dynamically picks the right explainer for each model type
- **Lazy loading** — `MultimodalRiskEngine._ensure_loaded()` defers model loading until first use
- **Configuration as code** — `config/settings.py` loads from environment variables with `.env` fallback

---

### Q: Why was SQLite chosen as the database?

**A:** SQLite was chosen because:
1. **Lightweight** — No separate database server process needed; the database is a single file
2. **Serverless** — Ideal for an academic prototype; no PostgreSQL/MySQL setup required
3. **Sufficient for prototype scale** — The Cleveland dataset has 303 instances; production-scale data (millions of records) would warrant PostgreSQL
4. **ACID compliant** — Ensures data integrity for audit logs and assessment records
5. **Python native** — `sqlite3` is in the standard library; no additional drivers needed
6. **Portable** — The entire database can be copied, backed up, or moved as a single file

**Databases used:**
| Database | Purpose | Location |
|----------|---------|----------|
| `auth.db` | User accounts | `data/auth/` |
| `assessments.db` | Assessment history | `data/assessments/` |
| `reviews.db` | Doctor reviews | `data/reviews/` |
| `audit.db` | Security audit log | `data/security/` |
| `monitoring.db` | Monitoring events | `data/monitoring/` |
| `evaluation.db` | Model evaluation runs | `data/evaluation/` |

**Key reference:** `config/settings.py:64-76` defines all database paths.

---

### Q: Describe the testing approach.

**A:** The project uses **pytest** as the test framework with **562 tests** across all modules.

**Test categories:**
- Unit tests (`test_pipeline.py`, `test_preprocessing.py`, `test_prediction.py`)
- Security tests (`test_auth.py`, `test_authorization.py`, `test_security.py`, `test_alert_security.py`)
- SHAP tests (`test_shap.py`)
- Lifestyle NLP tests (`test_lifestyle_analyzer.py`, `test_lifestyle.py`)
- Multimodal risk tests (`test_multimodal_risk.py`)
- Assessment history tests (`test_assessment_history.py`)
- Dashboard tests (`test_dashboard_analytics.py`, `test_ui_components.py`, `test_dashboard_security.py`)
- Model monitoring tests (`test_model_monitoring.py`)
- Drift detection tests (`test_drift_detection.py`)
- Anomaly detection tests (`test_anomaly_detection.py`)
- Data quality tests (`test_data_quality_monitoring.py`)
- Alert tests (`test_alerts.py`, `test_alert_analytics.py`)
- Recommendation tests (`test_recommendation_engine.py`, `test_recommendation_rules.py`, `test_recommendation_security.py`)
- Report generation tests (`test_report_generator.py`)
- Review service tests (`test_review_service.py`, `test_review_authorization.py`)

**Test command:** `pytest -q` (runs all 562 tests)

**Key reference:** `tests/` directory contains all test files; `conftest.py` provides shared fixtures.

---

## 2. Machine Learning

### Q: What models are used and why were they chosen?

**A:** Four classification models are implemented:

| Model | Class | Why Chosen |
|-------|-------|------------|
| **Logistic Regression** | `LogisticRegression` | Linear baseline; interpretable coefficients; fast training; compatible with `LinearExplainer` |
| **Random Forest** | `RandomForestClassifier` | Non-linear; handles feature interactions; robust to outliers; compatible with `TreeExplainer` |
| **XGBoost** | `XGBClassifier` | Gradient boosting; state-of-the-art for tabular data; regularization prevents overfitting; compatible with `TreeExplainer` |
| **Neural Network (MLP)** | `MLPClassifier` | Captures complex non-linear patterns; universal approximator; compatible with `KernelExplainer` |

**Model selection:** The best model is selected via 5-fold Stratified K-Fold cross-validation using ROC-AUC as the primary metric. The selection is stored in `reports/best_model.json`.

**Key reference:** `src/ml/models/logistic_regression_model.py`, `random_forest_model.py`, `xgboost_model.py`, `neural_network_model.py`.

---

### Q: What dataset is used?

**A:** The **Cleveland Heart Disease dataset** from the UCI Machine Learning Repository.

**Key characteristics:**
- 303 instances (patients)
- 13 clinical features (11 used as model inputs after preprocessing)
- Binary target: 0 (absence of heart disease) / 1 (presence)
- Original target values 0-4 are normalized: 0 → 0, 1+ → 1

**Clinical features (canonical schema):**

| Feature | Type | Description |
|---------|------|-------------|
| `age` | Numerical | Age in years |
| `sex` | Categorical | 0 = female, 1 = male |
| `chest_pain_type` | Categorical | 0-3 (typical angina, atypical angina, non-anginal, asymptomatic) |
| `resting_bp` | Numerical | Resting blood pressure (mm Hg) |
| `cholesterol` | Numerical | Serum cholesterol (mg/dl) |
| `fasting_blood_sugar` | Categorical | 0 = ≤120 mg/dl, 1 = >120 mg/dl |
| `resting_ecg` | Categorical | 0-2 (normal, ST-T abnormality, left ventricular hypertrophy) |
| `max_heart_rate` | Numerical | Maximum heart rate achieved |
| `exercise_angina` | Categorical | 0 = no, 1 = yes |
| `st_depression` | Numerical | ST depression induced by exercise |
| `num_major_vessels` | Numerical | Number of major vessels (0-4) colored by fluoroscopy |

**Key reference:** `src/data/features.py` defines the canonical schema, column mappings, and validation bounds.

---

### Q: How is the best model selected?

**A:** The best model is selected through **5-fold Stratified K-Fold cross-validation**:

1. The training data (80% of the full dataset) is split into 5 folds
2. Each fold is used as a validation set once, with the remaining 4 folds as training
3. **ROC-AUC** is computed for each fold
4. The model with the highest mean ROC-AUC across folds is selected as the best model
5. The result is saved to `reports/best_model.json`

**Secondary evaluation:** F1 score, precision, recall, accuracy, and confusion matrix are also computed for the final evaluation on the held-out test set (20%).

**Key reference:** `src/ml/cross_validation.py` implements `create_cv_strategy()` (StratifiedKFold, 5 folds); `src/ml/evaluate.py` handles evaluation.

---

### Q: What is the multimodal approach?

**A:** HeartGuard combines two independent risk assessment modalities into a single score:

**Formula:**
```
Overall Risk = (Clinical Risk × 0.70) + (Lifestyle Risk × 0.30)
```

- **Clinical ML Risk (70%):** The positive-class probability from the best trained clinical model, scaled to 0–100%. This captures objective, measurable physiological indicators.
- **Lifestyle Risk (30%):** A quantified risk score (0–100) derived from the NLTK rule-based lifestyle text analyzer. This captures subjective, behavioral risk factors reported by the patient.

**Why 70/30 weighting:**
- Clinical data is more objective and medically validated
- Lifestyle text is subjective and self-reported
- The weighting ensures clinical evidence dominates while lifestyle context provides meaningful adjustment

**Operational thresholds:**
| Overall Risk | Category | Recommended Action |
|-------------|----------|-------------------|
| > 85% | CRITICAL | Immediate medical consultation |
| 60%–85% | APPOINTMENT_RECOMMENDED | Medical appointment recommendation |
| < 60% | MONITORING | Regular monitoring recommended |

**Key reference:** `src/risk_engine/multimodal_risk.py:47-72` implements `calculate_multimodal_risk()`; `src/risk_engine/risk_categories.py` defines thresholds.

---

### Q: What preprocessing is used?

**A:** A scikit-learn `Pipeline` with two branches:

| Component | Strategy | Implementation |
|-----------|----------|----------------|
| **Numerical imputation** | Median | `SimpleImputer(strategy='median')` |
| **Numerical scaling** | MinMaxScaler | `MinMaxScaler()` |
| **Categorical imputation** | Most frequent | `SimpleImputer(strategy='most_frequent')` |
| **Categorical encoding** | One-hot | `OneHotEncoder(handle_unknown='ignore')` |

**Critical safeguards:**
- Preprocessor is fit **only on training data** after train/test split (no data leakage)
- `handle_unknown='ignore'` prevents errors from unseen categories at prediction time
- Feature ordering is deterministic (`HEARTGUARD_FEATURES` list in `src/data/features.py`)
- The fitted preprocessor is serialized to `models/preprocessor.pkl`

**Key reference:** `src/data/preprocessing.py` implements `create_preprocessor()`, `fit_preprocessor()`, `transform_data()`.

---

### Q: What are the 13 clinical features?

**A:** The 13 features from the Cleveland dataset are mapped to a canonical HeartGuard schema:

| # | Canonical Name | Source Name | Type | Range |
|---|---------------|-------------|------|-------|
| 1 | `age` | `age` | Numerical | 1–150 |
| 2 | `sex` | `sex` | Binary | 0/1 |
| 3 | `chest_pain_type` | `cp` | Categorical | 0–3 |
| 4 | `resting_bp` | `trestbps` | Numerical | 1–300 |
| 5 | `cholesterol` | `chol` | Numerical | 1–800 |
| 6 | `fasting_blood_sugar` | `fbs` | Binary | 0/1 |
| 7 | `resting_ecg` | `restecg` | Categorical | 0–2 |
| 8 | `max_heart_rate` | `thalach` | Numerical | 1–300 |
| 9 | `exercise_angina` | `exang` | Binary | 0/1 |
| 10 | `st_depression` | `oldpeak` | Numerical | 0–20 |
| 11 | `num_major_vessels` | `ca` | Numerical | 0–4 |

**Note:** The 13th feature `thal` is present in some versions of the Cleveland dataset but is used as an alternative target indicator, not as an input feature. The model uses 11 input features after preprocessing expands categoricals into one-hot columns.

**Key reference:** `src/data/features.py:35-47` defines `HEARTGUARD_FEATURES`; `src/data/features.py:141-148` defines `VALIDATION_BOUNDS`.

---

### Q: How is overfitting prevented?

**A:** Multiple strategies are employed:

1. **Train/test split** — 80/20 stratified split ensures the test set is representative
2. **Cross-validation** — 5-fold Stratified K-Fold provides robust performance estimates
3. **Regularization** — Logistic Regression uses L1/L2 penalty with tuned C parameter; XGBoost uses learning_rate and max_depth tuning; MLP uses alpha (L2 regularization)
4. **No data leakage** — Preprocessor is fit only on training data; test data is transformed using the fitted preprocessor
5. **Early stopping** — Neural Network can use early stopping to prevent over-training
6. **Feature selection** — Only 11 clinically relevant features are used (no unnecessary features)
7. **Model validation** — Final evaluation on held-out test set confirms generalization

**Key reference:** `src/ml/cross_validation.py` implements cross-validation; `src/ml/evaluate.py` computes generalization metrics.

---

## 3. Explainability (SHAP)

### Q: What is SHAP?

**A:** SHAP stands for **SHapley Additive exPlanations**. It is a game-theoretic approach to explaining the output of any machine learning model.

**Core concept:** SHAP assigns each feature an importance value (a "Shapley value") for a particular prediction. The Shapley value is the average marginal contribution of a feature value across all possible coalitions of features.

**Mathematical foundation:**
- Based on Shapley values from cooperative game theory (Lloyd Shapley, 1953)
- Each feature is a "player" in a game; the prediction is the "payout"
- SHAP fairly distributes the prediction among features

**Key properties:**
1. **Local accuracy** — The SHAP values sum to the difference between the model output and the average prediction
2. **Missingness** — Features not present have zero contribution
3. **Consistency** — If a feature's contribution increases, its SHAP value does not decrease

**Key reference:** `src/explainability/shap_explainer.py` implements the explainer creation logic.

---

### Q: Why SHAP over LIME?

**A:** SHAP was chosen over LIME for several reasons:

1. **Consistency** — SHAP guarantees that if a feature's effect increases, its importance value increases. LIME does not provide this guarantee.
2. **Game theory foundation** — SHAP values are derived from a rigorous mathematical framework (Shapley values), making them theoretically sound.
3. **Uniqueness** — SHAP values are the unique solution satisfying local accuracy, missingness, and consistency. LIME uses local linear approximation which is not unique.
4. **Model-specific optimizations** — `TreeExplainer` computes exact Shapley values in polynomial time for tree-based models. LIME requires perturbation-based sampling.
5. **Global explanations** — SHAP provides both local (per-prediction) and global (feature importance) explanations through a unified framework.

**When LIME might be preferred:**
- When the model is a true black box with no structure to exploit
- When computation speed is more critical than theoretical guarantees

For HeartGuard, SHAP's theoretical rigor and availability of efficient tree-based explainers made it the better choice.

---

### Q: What do SHAP values mean?

**A:** A SHAP value represents the contribution of a specific feature to a specific prediction, relative to the average prediction.

**Interpretation:**
- **Positive SHAP value** → The feature pushes the prediction **toward** heart disease presence (increases risk)
- **Negative SHAP value** → The feature pushes the prediction **away** from heart disease presence (decreases risk)
- **Zero SHAP value** → The feature has no effect on this particular prediction
- **Magnitude** → Larger absolute values indicate stronger influence

**Example:**
```
Feature: age = 65
SHAP value: +0.15
Meaning: Being 65 years old increases the risk prediction by 0.15
         (compared to the average patient)

Feature: max_heart_rate = 160
SHAP value: -0.08
Meaning: Having a max heart rate of 160 decreases the risk prediction
         by 0.08 (compared to the average patient)
```

**Visualization:** The SHAP waterfall plot shows these contributions visually, with the base value (average prediction) on the left and the final prediction on the right.

**Key reference:** `src/explainability/service.py` generates human-readable summaries from SHAP values.

---

### Q: How do you ensure explanations are not misleading?

**A:** Several safeguards are in place:

1. **Non-diagnostic language** — All explanations use phrases like "model-based contribution" and "statistical association" rather than causal language
2. **Disclaimers** — Every explanation includes: "This is a model-based risk estimate, not a clinical diagnosis. Consult a healthcare professional."
3. **Safety rules** — `src/nlp/explanation.py` defines `DISCLAIMER_TEXT` that is appended to all outputs
4. **No medical advice** — SHAP values are presented as feature contributions to a statistical model, not as medical risk factors
5. **Contextual framing** — Explanations are framed as "the model's reasoning" rather than "the patient's condition"
6. **Visual clarity** — Waterfall plots clearly show direction (risk increase/decrease) and magnitude

**Key reference:** `src/risk_engine/risk_explanation.py` implements `generate_overall_explanation()` with disclaimers.

---

## 4. NLP & Lifestyle Analysis

### Q: How does lifestyle analysis work?

**A:** HeartGuard uses a **lexicon-based, rule-driven NLP pipeline** to analyze free-text patient lifestyle descriptions:

**Pipeline steps:**
1. **Text preprocessing** (`src/nlp/text_preprocessor.py`):
   - Text normalization (lowercasing, whitespace standardization)
   - Punctuation preservation for decimals (e.g., "5.5 hours")
   - NLTK `punkt`/`punkt_tab` tokenization with offline regex fallback

2. **Risk lexicon matching** (`src/nlp/risk_lexicon.py`):
   - 6 risk categories with predefined keywords and weights
   - Multi-word phrase matching (prioritized over single words)
   - Negation detection ("do not smoke", "don't drink", "avoid junk food")
   - Alcohol disambiguation (prevents "drink coffee" from triggering alcohol risk)
   - Positive exercise recognition (counters false inactivity flags)

3. **Scoring** (`src/nlp/scoring.py`):
   - Sum detected risk points across all categories
   - Cap at 100 (mathematical maximum)
   - Categorize: LOW (0–29), MODERATE (30–59), HIGH (60–84), CRITICAL (85–100)

4. **Explanation generation** (`src/nlp/explanation.py`):
   - Clinical narratives for detected risk factors
   - Top 3 risk factors identified
   - Non-diagnostic language enforced

**Key reference:** `src/nlp/lifestyle_analyzer.py` orchestrates the pipeline; `src/nlp/risk_lexicon.py` defines the lexicon.

---

### Q: What lifestyle factors are analyzed?

**A:** Six cardiovascular lifestyle risk domains:

| Factor | Risk Points | Severity | Example Keywords |
|--------|-------------|----------|-----------------|
| **Smoking** | 25 | High | smoke, cigarettes, tobacco, nicotine, vape |
| **Family History** | 20 | High | family history, heart attack, cardiac |
| **Unhealthy Diet** | 18 | Moderate | junk food, fast food, fried, oily food |
| **Physical Inactivity** | 15 | High | no exercise, sedentary, desk job, inactive |
| **Poor Sleep** | 12 | Moderate | insomnia, poor sleep, sleep 5 hours |
| **Alcohol Use** | 10 | Low | drink, alcohol, beer, wine, liquor |

**Maximum possible score:** 100 (all factors detected)

**Risk categories:**
| Score Range | Category |
|-------------|----------|
| 0–29 | LOW |
| 30–59 | MODERATE |
| 60–84 | HIGH |
| 85–100 | CRITICAL |

**Key reference:** `src/nlp/risk_lexicon.py:28-182` defines `RISK_LEXICON`.

---

### Q: How is the lifestyle risk calculated?

**A:** The lifestyle risk score is calculated through weighted point accumulation:

1. For each detected risk category, add its predefined `risk_points` to the total
2. Apply negation detection: if a risk keyword is preceded by a negation cue (e.g., "no", "not", "never", "don't"), the risk is **not** counted
3. Apply disambiguation: "drink coffee" does not trigger alcohol risk; "drink alcohol" does
4. Apply positive indicators: "exercise regularly" counteracts physical inactivity
5. Sum all detected points
6. Cap the total at 100

**Example:**
```
Input: "I smoke cigarettes and eat fast food daily"
- Smoking detected: +25 points
- Unhealthy Diet detected: +18 points
- Total: 43 → MODERATE risk
```

**Weighted contribution to multimodal score:**
```
Lifestyle contribution = Lifestyle Risk × 0.30
```

**Key reference:** `src/nlp/scoring.py` implements the scoring logic; `src/nlp/lifestyle_analyzer.py:analyze()` orchestrates.

---

## 5. Security

### Q: How is authentication implemented?

**A:** Authentication uses **bcrypt** with a work factor of 12 rounds:

**Password hashing:**
- Passwords are hashed using `bcrypt.hashpw()` with `bcrypt.gensalt(rounds=12)`
- The hash is stored in `auth.db`; plaintext is never persisted
- `User.to_safe_dict()` ensures password hashes are never exposed in API responses

**Verification:**
- `bcrypt.checkpw()` performs constant-time comparison (timing-attack resistant)
- Generic error messages ("Invalid email or password") prevent user enumeration
- Failed login attempts are recorded in the audit log

**Session management:**
- Session tokens are generated using `secrets.token_urlsafe(32)`
- Session timeout: 30 minutes of inactivity
- Session invalidation on logout

**Key reference:** `src/auth/password_service.py` implements bcrypt operations; `src/auth/session_manager.py` handles sessions.

---

### Q: What is RBAC and how is it implemented?

**A:** Role-Based Access Control (RBAC) restricts system access based on user roles:

**Roles:**

| Role | Permissions |
|------|------------|
| **PATIENT** | Create/view own assessments, view own history, download own reports, view own dashboard |
| **REVIEWER** | Read AI predictions, submit professional reviews, view review queue |
| **ADMIN** | Full system access: user management, audit logs, model monitoring, analytics, security center |

**Implementation:**
- Role is stored in `users` table as `TEXT NOT NULL DEFAULT 'PATIENT'`
- Server-side enforcement via decorators: `require_reviewer()`, `require_admin()`
- Admin accounts are provisioned **only** via out-of-band CLI tool (`scripts/create_admin.py`)
- Role changes are logged in the audit trail

**Key reference:** `src/auth/authorization.py` implements role checking; `src/security/authorization_service.py` provides server-side enforcement.

---

### Q: How is patient data isolated?

**A:** Multiple layers of data isolation prevent cross-account access:

1. **User ID filtering** — Every database query includes `WHERE user_id = ?` with the authenticated user's ID
2. **IDOR prevention** — `validate_integer_id()` validates that IDs are positive integers; no raw user-supplied IDs are used directly
3. **Ownership verification** — Before accessing an assessment, the system verifies the requesting user owns it
4. **Session binding** — Each request is bound to the authenticated session; session tokens are validated on every request
5. **Separate databases** — Assessments, reviews, and audit logs are in separate SQLite databases

**Example flow:**
```
Patient requests assessment #42
  → Session validated (user_id = 5)
  → Query: SELECT * FROM assessments WHERE id = 42 AND user_id = 5
  → If no rows returned → access denied
```

**Key reference:** `src/auth/authorization.py` implements ownership checks; `src/security/input_validator.py:88-98` validates integer IDs.

---

### Q: How are audit logs implemented?

**A:** Audit logs are implemented as an **append-only, structured, indexed SQLite database**:

**Schema:**
```sql
CREATE TABLE audit_log (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp     TEXT NOT NULL,
    event_type    TEXT NOT NULL,
    user_id       INTEGER,
    role          TEXT,
    status        TEXT NOT NULL,
    detail        TEXT,
    resource_type TEXT,
    resource_id   TEXT,
    category      TEXT,
    severity      TEXT DEFAULT 'INFO',
    ip_hash       TEXT
);
```

**Event taxonomy (50+ event types):**
- AUTHENTICATION: login_success, login_failure, logout, registration, session_expired
- AUTHORIZATION: access_denied, idor_attempt, privilege_escalation_attempt
- DATA_ACCESS: assessment_created, assessment_viewed, data_exported
- ADMIN_ACTION: admin_access, role_changed, user_status_changed
- FILE_ACCESS: report_generated, report_downloaded, file_upload_rejected
- MODEL_OPERATION: model_evaluation, model_status_changed
- SYSTEM_SECURITY: rate_limit_exceeded, input_validation_failed

**Privacy protections:**
- IP addresses are SHA-256 hashed (salted)
- Passwords, tokens, API keys are redacted via regex patterns
- Raw clinical vectors and lifestyle narratives are never logged
- Detail text is truncated to 500 characters

**Indexes:** timestamp, user_id, event_type, category, severity

**Key reference:** `src/security/audit_logger.py` implements the complete audit logging system.

---

### Q: What security headers are used?

**A:** HeartGuard sets the following HTTP security headers (defined in `config/security.py`):

| Header | Value | Purpose |
|--------|-------|---------|
| `X-Content-Type-Options` | `nosniff` | Prevents MIME-type sniffing |
| `X-Frame-Options` | `DENY` | Prevents clickjacking (no iframe embedding) |
| `X-XSS-Protection` | `1; mode=block` | Enables browser XSS filter |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Limits referrer information leakage |
| `Content-Security-Policy` | `default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; ...` | Restricts resource loading to trusted sources |

**CSP details:**
- `default-src 'self'` — Only load resources from the same origin
- `script-src 'self' 'unsafe-inline' 'unsafe-eval'` — Required for Streamlit
- `style-src 'self' 'unsafe-inline' https://fonts.googleapis.com` — Allows Google Fonts
- `font-src 'self' https://fonts.gstatic.com` — Allows Google Fonts
- `img-src 'self' data:` — Allows inline images
- `connect-src 'self'` — Only allow same-origin connections

**Key reference:** `config/security.py:96-109` defines `SECURITY_HEADERS`.

---

### Q: How does rate limiting work?

**A:** Rate limiting is implemented at the session/application level:

**Policies:**

| Action | Limit | Window |
|--------|-------|--------|
| Login | 5 attempts | 60 seconds |
| Registration | 5 attempts | 60 seconds |
| Assessment creation | 10 | 60 seconds |
| Report generation | 10 | 60 seconds |
| Report download | 15 | 60 seconds |
| AI insights | 20 | 60 seconds |
| Model evaluation | 3 | 60 seconds |

**Implementation:**
- Session-state tracking via `streamlit.session_state`
- Rate limit exceeded events are logged to the audit trail
- Blocked requests return appropriate error messages

**Key reference:** `config/security.py:21-29` defines `RATE_LIMITS`; `src/security/rate_limiter.py` implements enforcement.

---

## 6. Deployment

### Q: How is the application deployed?

**A:** HeartGuard is deployed using **Streamlit** as the web framework, with **Docker** support for containerized deployment:

**Local deployment:**
```bash
pip install -r requirements.txt
streamlit run app.py
```

**Docker deployment:**
```dockerfile
FROM python:3.12-slim
# ... Dockerfile in project root
```

**Environment configuration:**
- `.env` file (development) or environment variables (production)
- `ENVIRONMENT` variable: `development`, `testing`, or `production`
- `APP_URL` for the application URL
- `ALERTS_ENABLED` for Twilio SMS toggle

**Health checks:**
- `scripts/health_check.py` verifies all components are operational
- `src/startup/startup_validator.py` runs pre-flight checks on application start

**Key reference:** `Dockerfile` at project root; `src/startup/startup_validator.py` validates startup conditions.

---

### Q: What are the health checks?

**A:** Two layers of health verification:

**1. Startup Validator** (`src/startup/startup_validator.py`):
- Verifies all required directories exist
- Checks model artifacts are present and loadable
- Validates database connectivity
- Confirms configuration is complete
- Runs before the application accepts requests

**2. Health Check Script** (`scripts/health_check.py`):
- CLI-based health verification
- Checks all databases are accessible
- Verifies model files are readable
- Validates environment variables
- Can be used as a Docker HEALTHCHECK

**Key reference:** `src/startup/startup_validator.py` runs on application startup; `scripts/health_check.py` is a standalone CLI tool.

---

### Q: How are secrets managed?

**A:** Secrets are managed through environment variables with development fallbacks:

**Approach:**
1. **Environment variables** (production) — Set via Docker, systemd, or shell
2. **`.env` file** (development) — Loaded by `python-dotenv`; never committed to git
3. **`.gitignore`** — `.env` is excluded from version control

**Sensitive values:**
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` — Twilio SMS credentials
- `REVIEWER_PASSWORD`, `ADMIN_PASSWORD` — Account provisioning passwords
- `SECRET_KEY` — Session signing key

**Security measures:**
- `config/settings.py` loads via `os.getenv()` with safe defaults
- Passwords are never hard-coded in source files
- `.env.example` provides a template without real values
- `startup_validator.py` checks that critical secrets are set in production

**Key reference:** `config/settings.py:19-20` loads `.env`; `.env.example` provides the template.

---

## 7. Monitoring

### Q: What monitoring exists?

**A:** HeartGuard implements a comprehensive monitoring stack:

**1. Drift Detection** (`src/analytics/drift_detection.py`):
- **Numerical features:** KS test, PSI (Population Stability Index)
- **Categorical features:** Chi-square test, PSI
- **Prediction distribution:** JS divergence
- **Confidence monitoring:** Low-confidence prediction tracking
- **Thresholds:** PSI warning 0.10 / critical 0.25; KS alpha 0.05; JS divergence warning 0.05 / critical 0.15

**2. Data Quality Monitoring** (`src/analytics/data_quality_monitoring.py`):
- Missing rate tracking (warning: 5%, critical: 20%)
- Duplicate rate tracking (warning: 2%, critical: 10%)
- Out-of-range value detection (warning: 3%)
- Schema change detection

**3. Anomaly Detection** (`src/analytics/anomaly_detection.py`):
- Z-score based anomaly detection (threshold: 3.0)
- Volume spike detection (2x normal)
- Error rate monitoring (warning: 5%, critical: 15%)

**4. Performance Monitoring** (`src/analytics/performance_monitoring.py`):
- Latency tracking (warning: 5s, critical: 10s)
- Cache TTL: 300 seconds

**5. Model Monitoring** (`src/analytics/model_monitoring.py`):
- Evaluation run history (accuracy, precision, recall, F1, ROC-AUC, PR-AUC)
- Model status tracking (PRODUCTION, VALIDATION, RETIRED)
- Metric trend analysis

**6. Monitoring Events** (`src/analytics/monitoring_events.py`):
- Centralized event logging for all monitoring systems
- Event lifecycle management with configurable retention (90 days)
- Severity-based alerting

**Key reference:** `config/monitoring.py` defines all thresholds; `src/analytics/` implements the monitoring services.

---

### Q: How is model performance tracked?

**A:** Model performance is tracked through evaluation runs stored in an SQLite database:

**Evaluation runs include:**
- Model name and version
- Evaluation date
- Metrics: accuracy, precision, recall, F1, ROC-AUC, PR-AUC
- Confusion matrix
- Training data metadata
- Status (COMPLETED, FAILED)

**Tracking workflow:**
1. `src/ml/evaluate.py` computes metrics on the test set
2. Results are stored in `evaluation.db` via `ModelMonitoringService`
3. `pages/model_monitoring.py` displays historical performance
4. Admin can compare metrics across evaluation runs
5. Performance degradation triggers monitoring events

**Key reference:** `src/analytics/model_monitoring.py` implements `ModelMonitoringService`; `src/ml/evaluate.py` generates metrics.

---

### Q: What is monitored for drift?

**A:** Three types of drift are monitored:

**1. Feature Drift:**
- **Numerical features** (age, resting_bp, cholesterol, max_heart_rate, st_depression):
  - KS test (Kolmogorov-Smirnov) — tests if two distributions differ significantly
  - PSI (Population Stability Index) — measures distribution shift magnitude
- **Categorical features** (sex, chest_pain_type, fasting_blood_sugar, resting_ecg, exercise_angina):
  - Chi-square test — tests if frequency distributions differ
  - PSI

**2. Prediction Drift:**
- JS divergence (Jensen-Shannon) — measures divergence between reference and current prediction distributions
- Threshold: warning at 0.05, critical at 0.15

**3. Confidence Drift:**
- Tracks proportion of low-confidence predictions (probability < 0.40)
- Warning when > 30% of predictions are low-confidence

**Reference window:** 90 days (configurable)
**Current window:** 30 days (configurable)
**Minimum sample size:** 30 assessments

**Key reference:** `src/analytics/drift_detection.py` implements all drift detection; `config/monitoring.py:22-34` defines thresholds.

---

## Additional Quick-Fire Questions

### Q: What is the dataset split?
**A:** 80/20 stratified split with `random_state=42` for reproducibility.

### Q: How many tests pass?
**A:** 562 tests across all modules.

### Q: What is the model artifact format?
**A:** Python pickle (`.pkl`) files with SHA-256 integrity checksums in `models/model_manifest.json`.

### Q: How are passwords stored?
**A:** bcrypt hashes with work factor 12, stored in `data/auth/auth.db`.

### Q: What is the session timeout?
**A:** 30 minutes of inactivity.

### Q: How many roles exist?
**A:** Three: PATIENT, REVIEWER, ADMIN.

### Q: What is the lifestyle score range?
**A:** 0–100, categorized as LOW (0–29), MODERATE (30–59), HIGH (60–84), CRITICAL (85–100).

### Q: What is the clinical weight in multimodal scoring?
**A:** 70% clinical ML, 30% lifestyle NLP.

### Q: What is the critical risk threshold?
**A:** Overall risk > 85%.

### Q: What Python version is required?
**A:** Python 3.12+.

---

**End of Viva Questions Document**
