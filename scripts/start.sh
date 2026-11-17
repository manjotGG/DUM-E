#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -x .venv/bin/python ] || [ ! -f frontend/dist/index.html ]; then
  printf 'Run bash scripts/setup.sh first.\n' >&2
  exit 1
fi
if [ ! -f ml/models/engines/model.joblib ]; then
  printf 'Train the model first: .venv/bin/python -m ml.engines.train\n' >&2
  exit 1
fi
printf 'DUM-E dashboard: http://127.0.0.1:8000\nAPI documentation: http://127.0.0.1:8000/docs\n'
exec .venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
