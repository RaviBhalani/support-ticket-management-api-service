#!/bin/bash

ENV=${1}

if [ -z "$ENV" ]; then
  echo "Usage: ./run_server.sh <environment>"
  echo "Environments: local, dev, test, prod"
  exit 1
fi

docker compose -f docker-compose.${ENV}.yaml --env-file .envs/${ENV}/api.env down
docker compose -f docker-compose.${ENV}.yaml --env-file .envs/${ENV}/api.env up -d --build
