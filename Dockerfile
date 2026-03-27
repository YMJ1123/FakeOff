# Flask API + ML classifier (no frontend — nginx handles that)
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY scam-pipeline/ scam-pipeline/
COPY classifier/ classifier/

WORKDIR /app/scam-pipeline

EXPOSE 5001

CMD ["gunicorn", \
     "--bind", "0.0.0.0:5001", \
     "--workers", "2", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "api_server:app"]
