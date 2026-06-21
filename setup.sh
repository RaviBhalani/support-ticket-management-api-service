#!/usr/bin/env bash
set -e

echo "==> Tearing down containers and wiping volumes..."
docker compose -f docker-compose.local.yaml --env-file .envs/local.env down --volumes

echo "==> Building and starting containers..."
docker compose -f docker-compose.local.yaml --env-file .envs/local.env up -d --build

echo "==> Waiting for postgres to be ready. Sleeping for 30 seconds."
sleep 30

echo "==> Running migrations..."
docker compose -f docker-compose.local.yaml --env-file .envs/local.env exec server alembic upgrade head

echo "==> Creating virtual environment..."
python -m venv .venv

echo "==> Installing dependencies..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
  .venv/Scripts/pip install -r requirements/local.txt
else
  .venv/bin/pip install -r requirements/local.txt
fi

echo "==> Seeding database..."
cd scripts
python seed.py
cd ..

echo "==> Sample users..."
cd scripts
python sample_users.py
cd ..
