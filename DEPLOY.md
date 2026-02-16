# Optional: run CLI in Docker / Cloud Run

The project is **SDK + CLI only** (no HTTP server). Use this if you want to run the CLI inside a container or on Cloud Run as a job.

## Local Docker

```bash
docker build -t ai-private-layer .
docker run --rm ai-private-layer private-layer --help
docker run --rm ai-private-layer private-layer detect "Email me at john@example.com" --format text
```

With local model: mount the model dir and set env (or bake into image):

```bash
docker run --rm -v $(pwd)/src/private_layer/detectors/models:/app/models ai-private-layer \
  private-layer detect "John in Berlin" -d --local-model private-layer-v1
```

(Adjust path if your image layout differs.)

## Google Cloud Run (job or custom service)

If you wrap the CLI in your own script or use Cloud Run Jobs:

1. Build and push image (see `deploy.sh` or `cloudbuild.yaml`).
2. Set env: `TOKEN_KEY_HEX` if using encryption.
3. No API key or tenant config; the CLI reads config from file or defaults.

For Cloud Build and deploy script, see `cloudbuild.yaml` and `deploy.sh` (they reference a service name; adapt to your job or remove if you only run locally).
