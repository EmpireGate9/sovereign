#!/usr/bin/env bash
set -euo pipefail
APP_NAME="${1:-pai6-sovereign}"
REGION="${2:-me-central2}"
IMAGE="gcr.io/$(gcloud config get-value project)/${APP_NAME}:v$(date +%s)"

gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
gcloud builds submit --tag "$IMAGE" .
gcloud run deploy "$APP_NAME" --image "$IMAGE" --region "$REGION" --allow-unauthenticated --port 8080
gcloud run services describe "$APP_NAME" --region "$REGION" --format='value(status.url)'
