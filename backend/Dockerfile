
# Dockerfile (for FastAPI + Uvicorn)
FROM python:3.11-slim

# set workdir
WORKDIR /app

# copy dependency files
COPY ./requirements.txt /app/requirements.txt

# install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy source
COPY . /app

# use non-root user for security (optional)
RUN useradd -m appuser || true
USER appuser

# expose port (Vercel ignores EXPOSE but good to have)
EXPOSE 8000

# start uvicorn
# adjust module path if your FastAPI instance is in backend/main.py as app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
