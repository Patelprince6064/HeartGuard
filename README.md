# HeartGuard

## Early Heart Disease Risk Prediction with Explainable AI

> **Academic & Research Prototype** — HeartGuard is not a medical diagnostic system.
> Model predictions are experimental estimates and should not replace clinical evaluation.

---

## Problem Statement

Heart disease is the leading cause of death globally, responsible for approximately 17.9 million deaths annually (WHO). Early detection of cardiovascular risk can significantly improve patient outcomes through timely intervention. However, existing risk assessment tools often lack transparency, making it difficult for clinicians and patients to understand why a particular risk level was assigned.

## Solution

HeartGuard is a multimodal heart disease risk prediction platform that combines:

1. **Machine Learning** — Four clinical classifiers (Logistic Regression, Random Forest, XGBoost, Neural Network) trained on the Cleveland Heart Disease dataset
2. **Explainable AI (SHAP)** — Every prediction comes with a transparent, feature-by-feature explanation of model decisions
3. **NLP Lifestyle Analysis** — Free-text lifestyle descriptions are analyzed using a rule-based NLP engine to quantify lifestyle risk factors
4. **Multimodal Risk Fusion** — Clinical ML predictions (70%) and lifestyle risk (30%) are combined into a unified risk score
5. **Professional Review** — Authorized reviewers can inspect AI predictions and record clinical observations
6. **Emergency Alerts** — Critical risk cases trigger SMS notifications via Twilio
7. **Comprehensive Monitoring** — Data drift detection, model performance tracking, and data quality monitoring

---

## Features

| Feature | Description | Phase |
|---------|-------------|-------|
| Risk Assessment | Multimodal clinical + lifestyle risk prediction | 1-7 |
| Explainable AI | SHAP-based feature importance and patient-level explanations | 5 |
| Lifestyle NLP | Free-text lifestyle risk factor extraction and scoring | 6 |
| Emergency Alerts | Twilio SMS notifications for critical risk | 8 |
| Security & Auth | Bcrypt authentication, RBAC, rate limiting, audit logging | 9 |
| History & Reports | Assessment history, trend analysis, PDF report generation | 10 |
| Doctor Review | Professional review portal for clinical observation | 11 |
| Dashboard | Interactive dashboard with KPIs and charts | 12 |
| PDF Reports | Multi-page academic/research prototype PDF reports | 13 |
| Model Evaluation | Comprehensive ML model evaluation and comparison | 14 |
| Security Hardening | Enterprise-grade security architecture | 15 |
| Deployment | Docker, health checks, production configuration | 16 |
| Analytics & Monitoring | Drift detection, data quality, anomaly detection, performance monitoring | 17 |
| UI/UX Polish | Design system, responsive design, accessibility | 18 |
| Final QA | Complete testing, documentation, demo preparation | 19 |
| React Frontend | Modern React + Tailwind CSS UI with REST API | 21 |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   React Frontend (Vite)                     │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐  │
│  │Login │ │Dash  │ │Assess│ │Histry│ │Review│ │Admin │  │
│  └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘  │
├─────┼────────┼────────┼────────┼────────┼────────┼────────┤
│              REST API Layer (FastAPI)                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │  Auth    │ │Assessment│ │ Dashboard│ │  Reviews │    │
│  │  API     │ │   API    │ │   API    │ │   API    │    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │
├─────────────────────────────────────────────────────────────┤
│                    Python Backend Services                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │  Auth    │ │   ML     │ │  Risk    │ │ SHAP     │    │
│  │  Module  │ │ Pipeline │ │  Engine  │ │ Explainer│    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │  NLP     │ │  Alerts  │ │ Reports  │ │ Security │    │
│  │ Lifestyle│ │  Twilio  │ │ PDF Gen  │ │ Audit    │    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │
├─────────────────────────────────────────────────────────────┤
│                    SQLite Databases                         │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ │
│  │  Auth  │ │Audit   │ │Assess  │ │Alerts  │ │Reviews │ │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.12 |
| Frontend | React.js, Vite, Tailwind CSS, Recharts, Framer Motion |
| API Layer | FastAPI, uvicorn |
| ML Libraries | scikit-learn, XGBoost, TensorFlow |
| Explainability | SHAP |
| NLP | NLTK |
| Visualization | Recharts (frontend), Matplotlib (backend) |
| PDF Reports | ReportLab |
| Notifications | Twilio |
| Database | SQLite |
| Authentication | bcrypt, JWT (python-jose) |
| Testing | pytest |
| Deployment | Docker |

---

## ML Models

| Model | Type | CV ROC-AUC |
|-------|------|-----------|
| Logistic Regression | Linear | 0.4357 |
| Random Forest | Ensemble | 0.5381 |
| XGBoost | Gradient Boosting | 0.6078 |
| Neural Network | MLP | 0.4978 |

**Best Model**: XGBoost (selected by highest CV ROC-AUC)

**Multimodal Formula**: `Overall Risk = (Clinical ML Risk × 0.70) + (Lifestyle NLP Risk × 0.30)`

---

## Project Structure

```
HeartGuard/
├── app.py                      # Main Streamlit entry point (deprecated)
├── api/                        # FastAPI REST API layer
│   ├── main.py                 # FastAPI application
│   ├── auth.py                 # Authentication endpoints
│   ├── assessments.py          # Assessment CRUD endpoints
│   ├── dashboard.py            # Dashboard data endpoints
│   ├── reviews.py              # Review workflow endpoints
│   ├── admin.py                # Admin analytics/monitoring endpoints
│   ├── recommendations.py      # Recommendations endpoints
│   ├── reports.py              # Report generation endpoints
│   ├── security.py             # Security audit endpoints
│   ├── health.py               # Health check endpoints
│   ├── deps.py                 # Auth dependencies, rate limiting
│   └── requirements.txt        # API-specific dependencies
├── frontend/                   # React frontend application
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Page components (patient, reviewer, admin)
│   │   ├── context/            # React context (auth)
│   │   ├── services/           # API service layer
│   │   ├── components/layout/  # Layout components (sidebar, topbar)
│   │   └── components/routes/  # Route guards
│   ├── package.json
│   └── vite.config.js
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Multi-stage Docker build
├── .env.example                # Environment variable template
├── config/
│   ├── settings.py             # Centralized configuration
│   ├── security.py             # Security policies
│   └── monitoring.py           # Monitoring thresholds
├── src/
│   ├── auth/                   # Authentication & authorization
│   ├── ml/                     # ML training & prediction
│   ├── data/                   # Data loading & preprocessing
│   ├── explainability/         # SHAP implementation
│   ├── nlp/                    # Lifestyle NLP analysis
│   ├── risk_engine/            # Multimodal risk calculation
│   ├── alerts/                 # Emergency SMS alerts
│   ├── reports/                # PDF report generation
│   ├── review/                 # Doctor review workflow
│   ├── recommendations/        # Recommendation engine
│   ├── security/               # Security & audit logging
│   ├── analytics/              # Analytics & monitoring
│   ├── evaluation/             # Model evaluation
│   ├── health/                 # Health checks
│   └── utils/                  # Shared utilities
├── pages/                      # Streamlit pages (deprecated)
├── tests/                      # Automated tests
├── models/                     # Trained model artifacts
├── data/                       # Databases & datasets
├── reports/                    # Evaluation reports
├── docs/                       # Documentation
└── scripts/                    # Admin scripts
```

---

## Installation

### Prerequisites
- Python 3.12+
- Node.js 18+
- pip
- npm

### Backend Setup

```bash
# 1. Clone the repository
git clone https://github.com/heartguard/heartguard.git
cd heartguard

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment
cp .env.example .env
# Edit .env with your settings (at minimum, set SECRET_KEY)

# 6. Run the API server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
```

The frontend runs on http://localhost:5173 and proxies API requests to http://localhost:8000.

### Docker Deployment

```bash
# Build the image
docker build -t heartguard .

# Run the container
docker run -p 8000:8000 \
  -e SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))") \
  -e ADMIN_EMAIL=admin@heartguard.local \
  -e ADMIN_PASSWORD=YourSecurePassword \
  heartguard
```

---

## Configuration

Environment variables (see `.env.example`):

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Application secret key |
| `ADMIN_EMAIL` | Yes | Admin account email |
| `ADMIN_PASSWORD` | Yes | Admin account password |
| `REVIEWER_EMAIL` | No | Reviewer account email |
| `REVIEWER_PASSWORD` | No | Reviewer account password |
| `TWILIO_ACCOUNT_SID` | No | Twilio account SID |
| `TWILIO_AUTH_TOKEN` | No | Twilio auth token |
| `ALERTS_ENABLED` | No | Enable SMS alerts (default: false) |
| `DEBUG` | No | Debug mode (default: false) |
| `HEARTGUARD_CORS_ORIGINS` | No | Allowed CORS origins (default: http://localhost:5173) |

---

## API Documentation

The FastAPI backend provides auto-generated interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | /api/auth/register | Register patient account | No |
| POST | /api/auth/login | Login (returns JWT) | No |
| GET | /api/auth/me | Current user info | Yes |
| POST | /api/assessments | Create new assessment | Yes |
| GET | /api/assessments | List assessments | Yes |
| GET | /api/assessments/latest | Latest assessment | Yes |
| GET | /api/dashboard | Dashboard data | Yes |
| GET | /api/reviews/queue | Review queue | REVIEWER |
| POST | /api/reviews/{id} | Create review | REVIEWER |
| GET | /api/admin/analytics | System analytics | ADMIN |
| GET | /api/admin/health | System health | ADMIN |
| GET | /api/health | Public health check | No |

---

## Testing

```bash
# Run full test suite (562 tests)
pytest -q

# Run specific test categories
pytest tests/test_auth.py -v                    # Authentication
pytest tests/test_security_phase15.py -v        # Security
pytest tests/test_shap.py -v                    # SHAP Explainability
pytest tests/test_multimodal_risk.py -v         # Risk Engine
pytest tests/test_review_service.py -v          # Review Workflow
pytest tests/test_ui_components.py -v           # UI Components
pytest tests/test_deployment.py -v              # Deployment
pytest tests/test_drift_detection.py -v         # Drift Detection
```

---

## Usage

### Patient Workflow
1. Navigate to the landing page and click "Get Started"
2. Register an account or login
3. View your dashboard with risk summary and trends
4. Create a new risk assessment (enter clinical data + lifestyle description)
5. View your risk result with SHAP explanation
6. Review personalized recommendations
7. View assessment history and trends
8. Generate and download PDF reports

### Reviewer Workflow
1. Login with reviewer credentials
2. View the reviewer dashboard with queue statistics
3. Browse the review queue of pending assessments
4. Inspect AI predictions and explanations
5. Submit professional clinical observations

### Admin Workflow
1. Login with admin credentials
2. View the admin dashboard with system overview
3. Monitor analytics with interactive charts
4. Track model performance and data drift
5. Review data quality metrics
6. Check system health status
7. Review audit logs and security events
8. Manage user accounts

---

## Documentation

| Document | Description |
|----------|-------------|
| `docs/architecture.md` | System architecture |
| `docs/data_flow.md` | Data flow documentation |
| `docs/ml_pipeline.md` | ML pipeline documentation |
| `docs/model_card.md` | Model card |
| `docs/security.md` | Security documentation |
| `docs/privacy.md` | Privacy documentation |
| `docs/testing.md` | Testing documentation |
| `docs/user_guide.md` | Patient user guide |
| `docs/admin_guide.md` | Admin guide |
| `docs/reviewer_guide.md` | Reviewer guide |
| `docs/demo_script.md` | Demo presentation script |
| `docs/viva_questions.md` | Viva preparation Q&A |

---

## Known Limitations

1. **Dataset**: Limited to Cleveland Heart Disease dataset (303 samples). Not validated on diverse populations.
2. **Models**: ROC-AUC scores are modest (0.43-0.61). This is an academic/research prototype, not a clinical-grade system.
3. **Lifestyle NLP**: Rule-based approach with predefined lexicon. Not a production NLP system.
4. **Clinical Validation**: No clinical validation has been performed. Predictions are experimental estimates.
5. **Population Bias**: Training data may not represent all demographics equally.

---

## Clinical Disclaimer

HeartGuard is an academic/research prototype and is not a medical diagnostic system. Model predictions are experimental estimates based on the provided data and should not replace evaluation or advice from a qualified healthcare professional. If you or someone nearby is experiencing severe symptoms, seek immediate emergency medical attention.

---

## License

This project is for academic/research purposes only.
