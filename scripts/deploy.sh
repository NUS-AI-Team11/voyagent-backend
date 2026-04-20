#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/voyagent"
cd "$APP_DIR"

if [ ! -f .env ]; then
  echo "ERROR: /opt/voyagent/.env not found"
  exit 1
fi

docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
docker image prune -f

sleep 5
curl -f http://127.0.0.1:8000/api/v1/health
echo "Deploy success"
