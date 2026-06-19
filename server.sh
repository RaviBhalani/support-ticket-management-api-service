#!/bin/bash

set -e

echo "ENVIRONMENT: $ENVIRONMENT"
echo "SERVER_HOST: $SERVER_HOST"
echo "SERVER_PORT: $SERVER_PORT"

if [ "$ENVIRONMENT" = "local" ]; then
    uvicorn src.main:app --host "$SERVER_HOST" --port "$SERVER_PORT" --reload --log-level info
else
    uvicorn src.main:app --host "$SERVER_HOST" --port "$SERVER_PORT" --log-level info
fi