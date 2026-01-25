# Mem-Proxy Dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install dependencies first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py ./

# Create memory dir
RUN mkdir -p /app/memory && useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8010

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8010/health').getcode()==200 else 1)"

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8010"]
