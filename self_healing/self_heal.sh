#!/usr/bin/env bash
# Simple self-healing: probe service URL; if unhealthy, trigger a quick roll.
set -euo pipefail

APP_NAME="${1:-pai6-sovereign}"
REGION="${2:-me-central2}"
URL="$(gcloud run services describe "$APP_NAME" --region "$REGION" --format='value(status.url)')"

probe(){
  curl -sS "$URL/api/system/healthz" | grep -q '"ok": true'
}

if probe; then
  echo "[Heal] Service healthy: $URL"
  exit 0
else
  echo "[Heal] Unhealthy — rolling revision…"
  REV_IMAGE="$(gcloud run services describe "$APP_NAME" --region "$REGION" --format='value(status.latestReadyRevisionName)')"
  IMAGE="$(gcloud run services describe "$APP_NAME" --region "$REGION" --format='value(status.traffic[0].latestRevision)' | sed 's/True/false/')"
  # Fast trick: re-deploy same image to force restart
  IMG="$(gcloud run services describe "$APP_NAME" --region "$REGION" --format='value(spec.template.spec.containers[0].image)')"
  gcloud run deploy "$APP_NAME" --image "$IMG" --region "$REGION" --allow-unauthenticated --port 8080
  echo "[Heal] Redeployed same image. Recheck manually."
fi
