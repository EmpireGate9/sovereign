#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   bash scripts/golden.sh "<PUBLIC_ZIP_URL>" "pai6-sovereign" "me-central2"
# Or run from inside the extracted folder with no args to deploy current source.

ZIP_URL="${1:-}"
APP_NAME="${2:-pai6-sovereign}"
REGION="${3:-me-central2}"
PORT="${PORT:-8080}"

log(){ printf "\n[Golden] %s\n" "$*"; }

log "Checking gcloud…"
gcloud --version >/dev/null

log "Enabling required APIs…"
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com

WORKDIR="$HOME/golden_build"
mkdir -p "$WORKDIR"
cd "$WORKDIR"

if [[ -n "$ZIP_URL" ]]; then
  log "Downloading ZIP from: $ZIP_URL"
  curl -L "$ZIP_URL" -o src.zip
  unzip -o src.zip -d src
  cd src
else
  log "No ZIP URL provided — expecting current directory has source."
fi

if [[ ! -f Dockerfile ]]; then
  log "Dockerfile missing; generating one (python:3.11-slim)…"
  cat > Dockerfile <<'EOF'
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8080
WORKDIR /app
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY backend/app /app/app
EXPOSE 8080
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8080"]
EOF
fi

IMAGE="gcr.io/$(gcloud config get-value project)/${APP_NAME}:v$(date +%s)"
log "Building image: $IMAGE"
gcloud builds submit --tag "$IMAGE" .

log "Deploying to Cloud Run…"
gcloud run deploy "$APP_NAME" --image "$IMAGE" --region "$REGION" --allow-unauthenticated --port "$PORT"

URL="$(gcloud run services describe "$APP_NAME" --region "$REGION" --format='value(status.url)')"
log "Deployed: $URL"
echo "$URL" > DEPLOYED_URL.txt
printf "\n[Golden] DONE. Open: %s\n" "$URL"
