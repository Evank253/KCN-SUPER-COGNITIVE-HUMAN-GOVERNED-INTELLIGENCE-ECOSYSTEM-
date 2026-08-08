#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"
python -m pip install -q -r requirements.txt
python -m pytest tests/ -q
