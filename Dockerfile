FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY src ./src
COPY config.example.yml .

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

ENV PORT=8080 HOST=0.0.0.0
CMD ["sh", "-c", "exec python -m uvicorn private_layer.api.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
