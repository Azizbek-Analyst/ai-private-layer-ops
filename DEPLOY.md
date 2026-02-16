# Deploy to Google Cloud Run

## Prerequisites

- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- `gcloud auth login`
- `gcloud config set project YOUR_PROJECT_ID`

## 1. Secrets (Secret Manager)

```bash
echo -n "your-api-key" | gcloud secrets create api-key-secret --data-file=-
echo -n "YOUR_64_HEX_CHARS" | gcloud secrets create token-key-secret --data-file=-
# Generate key: openssl rand -hex 32
```

Grant Cloud Run access (replace `PROJECT_NUMBER`):

```bash
gcloud secrets add-iam-policy-binding api-key-secret \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
gcloud secrets add-iam-policy-binding token-key-secret \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## 2. Deploy

**Option A: Script**

```bash
./deploy.sh YOUR_PROJECT_ID us-central1
```

**Option B: Manual**

```bash
export PROJECT_ID=your-project-id
export REGION=us-central1

gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com --quiet
gcloud builds submit --tag gcr.io/$PROJECT_ID/ai-private-layer-api
gcloud run deploy ai-private-layer-api \
  --image gcr.io/$PROJECT_ID/ai-private-layer-api \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0 \
  --execution-environment gen2
```

## 3. Set env and secrets

```bash
gcloud run services update ai-private-layer-api --region $REGION \
  --update-env-vars "TENANT=default,demo,GLINER_MODEL=urchade/gliner_multi-v2.1" \
  --update-secrets "API_KEY=api-key-secret:latest,TOKEN_KEY_HEX=token-key-secret:latest"
```

## 4. Verify

```bash
SERVICE_URL=$(gcloud run services describe ai-private-layer-api --region $REGION --format="value(status.url)")
curl $SERVICE_URL/v1/health
```

## CI/CD (Cloud Build)

```bash
gcloud services enable cloudbuild.googleapis.com
# Grant Cloud Build permission to deploy to Cloud Run (see Cloud docs)
gcloud builds submit --config cloudbuild.yaml
```

Trigger on push: create a GitHub trigger pointing at `cloudbuild.yaml` and branch `main`.

## Troubleshooting

- **Container failed to start and listen on PORT**  
  The container reads `PORT` from the environment. Ensure the image was built from the current Dockerfile.

- **Slow first request (cold start)**  
  GLiNER loads on first use. Use `--min-instances 1` or a smaller model in config (e.g. `urchade/gliner_small-v2.1`).

- **Out of memory**  
  Increase memory: `gcloud run services update ai-private-layer-api --region $REGION --memory 8Gi`.

- **Request timeout**  
  Increase timeout: `--timeout 600` (max 3600 for Cloud Run).

- **Logs**  
  `gcloud logging read "resource.type=cloud_run_revision" --limit 50 --format json`

## Local Docker test

```bash
docker build -t ai-private-layer-api .
docker run -p 8080:8080 \
  -e API_KEY=test \
  -e TENANT=default \
  -e TOKEN_KEY_HEX=1111111111111111111111111111111111111111111111111111111111111111 \
  ai-private-layer-api
curl http://localhost:8080/v1/health
```
