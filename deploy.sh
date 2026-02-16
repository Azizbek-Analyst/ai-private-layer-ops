#!/bin/bash

# Deploy to Google Cloud Run
# Usage: ./deploy.sh [PROJECT_ID] [REGION]

set -e

PROJECT_ID=${1:-${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project 2>/dev/null)}}
REGION=${2:-us-central1}
SERVICE_NAME="ai-private-layer-api"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

if [ -z "$PROJECT_ID" ]; then
    echo "Error: PROJECT_ID not set. Pass it as an argument or set GOOGLE_CLOUD_PROJECT"
    exit 1
fi

echo "Deploying to Google Cloud Run"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo ""

# Check auth
echo "Checking auth..."
gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n 1 || {
    echo "Error: Not authenticated. Run: gcloud auth login"
    exit 1
}

# Set project
echo "Setting project: $PROJECT_ID"
gcloud config set project "$PROJECT_ID"

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com --quiet

# Build Docker image
echo "Building Docker image..."
gcloud builds submit --tag "$IMAGE_NAME"

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
  --image "$IMAGE_NAME" \
  --platform managed \
  --region "$REGION" \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0 \
  --execution-environment gen2

# Get service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format="value(status.url)")

echo ""
echo "Deploy finished."
echo "Service URL: $SERVICE_URL"
echo ""
echo "Check health endpoint:"
echo "curl $SERVICE_URL/v1/health"
echo ""
echo "Remember to set env vars and secrets:"
echo "gcloud run services update $SERVICE_NAME --region $REGION \\"
echo "  --update-env-vars 'TENANT=qic,ai_private_demo,GLINER_MODEL=urchade/gliner_multi-v2.1' \\"
echo "  --update-secrets 'API_KEY=api-key-secret:latest,TOKEN_KEY_HEX=token-key-secret:latest'"

