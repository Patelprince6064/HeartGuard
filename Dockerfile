# HeartGuard — Production Dockerfile
# Multi-stage build for minimal production image
# Python 3.12 slim base (Debian bookworm)
# Application runs as non-root user

# --- Stage 1: Build dependencies ---
FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

# Install system dependencies required by numpy/scikit-learn/tensorflow
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libffi-dev \
        && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Stage 2: Production image ---
FROM python:3.12-slim-bookworm AS production

LABEL maintainer="HeartGuard Team"
LABEL description="HeartGuard - Early Heart Disease Risk Prediction with Explainable AI"
LABEL version="1.0.0"

# Security: do not run as root
RUN groupadd --gid 1000 heartguard && \
    useradd --uid 1000 --gid heartguard --create-home heartguard

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY config/ ./config/
COPY src/ ./src/
COPY pages/ ./pages/
COPY scripts/ ./scripts/
COPY app.py ./
COPY conftest.py ./
COPY pytest.ini ./

# Copy model artifacts
COPY models/ ./models/

# Copy data files needed at runtime
COPY data/raw/ ./data/raw/

# Create directories for runtime data and logs
RUN mkdir -p /app/data/auth \
    /app/data/security \
    /app/data/assessments \
    /app/data/alerts \
    /app/data/evaluations \
    /app/data/tmp \
    /app/reports/generated \
    /app/logs && \
    chown -R heartguard:heartguard /app

USER heartguard

# Environment defaults (overridable at runtime)
ENV ENVIRONMENT=production \
    DEBUG=false \
    LOG_TO_FILE=true \
    LOG_LEVEL=WARNING \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8501

# Health check using CLI script
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD ["python", "scripts/health_check.py", "--readiness"]

# Streamlit production startup
ENTRYPOINT ["streamlit", "run", "app.py", \
    "--server.port=8501", \
    "--server.address=0.0.0.0", \
    "--server.headless=true", \
    "--browser.gatherUsageStats=false", \
    "--server.enableXsrfProtection=true", \
    "--server.enableCORS=false"]
