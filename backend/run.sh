#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"
python -m pip install -q -r requirements.txt
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
