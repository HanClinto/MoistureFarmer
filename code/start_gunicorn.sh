#!/usr/bin/env bash
set -euo pipefail
# Start FastAPI via Gunicorn with Uvicorn workers and aggressive timeouts
# Recommended for development: pass --reload to auto-reload
exec python3 -m gunicorn webgui.server:app -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 --workers 1 --timeout 10 --graceful-timeout 5 "$@"
