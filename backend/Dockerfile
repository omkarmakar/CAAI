# backend/Dockerfile
FROM python:3.11-bullseye

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# copy requirements first (cache layer)
COPY backend/requirements.txt /app/requirements.txt

# Install system deps commonly needed by packages (adjust later if build errors)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl gcc libpq-dev libssl-dev libffi-dev \
    libjpeg-dev zlib1g-dev libxml2-dev libxslt1-dev poppler-utils \
    && pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && apt-get purge -y --auto-remove build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend source
COPY backend /app

# (optional) create non-root user for runtime
RUN useradd -m appuser || true
USER appuser

EXPOSE 8000

# Use Vercel PORT envvar (fallback to 8000 for local testing)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers"]
