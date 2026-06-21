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

echo "==> Seeding database..."
cd scripts
python seed.py
cd ..

echo "==> Sample users..."
cd scripts
python sample_users.py
cd ..
