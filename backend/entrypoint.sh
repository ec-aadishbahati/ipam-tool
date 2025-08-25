#!/usr/bin/env sh
set -e
python -m app.migrate
python -m app.seed_admin || true
export FORWARDED_ALLOW_IPS="*"
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers
