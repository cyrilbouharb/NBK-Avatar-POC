# MOBILE BACKEND MODE: Backend-only Docker image without frontend
# Python runtime stage (using Debian Bullseye to avoid OpenSSL 3 issues with speechsdk)
FROM python:3.11-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=src/app.py \
    FLASK_ENV=production \
    PIP_TRUSTED_HOST="pypi.org files.pythonhosted.org pypi.python.org" \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    ca-certificates \
    libasound2 \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash app

WORKDIR /app

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY --chown=app:app backend/src/ ./src/
COPY --chown=app:app data/scenarios/ ./data/scenarios/
COPY --chown=app:app data/graph-api-canned.json ./data/

USER app
EXPOSE 8000

# Health check endpoint updated for mobile backend mode
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["python", "src/app.py"]