# CLI-only image (no server). Run: docker run --rm IMAGE private-layer --help
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY src ./src
COPY config.example.yml .

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .

# Optional: install local_model extra and add detectors/models for -d --local-model
# RUN pip install --no-cache-dir ".[local_model]" && python -c "from pathlib import Path; (Path('src/private_layer/detectors/models')).mkdir(parents=True, exist_ok=True)"

ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["private-layer"]
