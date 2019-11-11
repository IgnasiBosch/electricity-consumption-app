#!/usr/bin/env bash

set -o nounset -o errexit

cd /app

echo "======================================"
echo "Starting service..."
echo "======================================"
exec s6-setuidgid app_user python3 -m app -c /app/config.json