
# Simple production image
FROM python:3.11-slim

WORKDIR /app

# Install runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default to web server; override in worker to run scheduler.py
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:${PORT:-5000}", "--workers", "2", "--timeout", "120"]
