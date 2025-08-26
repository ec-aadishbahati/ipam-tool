#!/usr/bin/env sh
set -e

echo "Starting IPAM tool deployment..."

echo "Running database migration with retry logic..."
for i in $(seq 1 10); do
  echo "Migration attempt $i/10..."
  if python -m app.migrate; then
    echo "✅ Migration succeeded on attempt $i"
    break
  else
    echo "❌ Migration failed on attempt $i"
    if [ $i -eq 10 ]; then
      echo "⚠️ Migration failed after 10 attempts, continuing with app startup..."
      echo "⚠️ Database may not be ready - check Fly.io PostgreSQL status"
    else
      echo "⏳ Retrying in 5 seconds..."
      sleep 5
    fi
  fi
done

echo "Running admin user seeding with retry logic..."
for i in $(seq 1 5); do
  echo "Admin seeding attempt $i/5..."
  if python -m app.seed_admin; then
    echo "✅ Admin seeding succeeded on attempt $i"
    break
  else
    echo "❌ Admin seeding failed on attempt $i"
    if [ $i -eq 5 ]; then
      echo "⚠️ Admin seeding failed after 5 attempts, continuing with app startup..."
      echo "⚠️ Admin user may need to be created manually"
    else
      echo "⏳ Retrying in 3 seconds..."
      sleep 3
    fi
  fi
done

export FORWARDED_ALLOW_IPS="*"

echo "🚀 Starting uvicorn server on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers
