#!/usr/bin/env sh
set -e

echo "Starting IPAM tool deployment with async migration strategy..."

export FORWARDED_ALLOW_IPS="*"

echo "🚀 Starting uvicorn server on port ${PORT:-8000}..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers &
UVICORN_PID=$!

echo "⏳ Waiting for uvicorn to initialize..."
sleep 5

echo "🔄 Starting async database migration with retry logic..."
(
  for i in $(seq 1 10); do
    echo "Migration attempt $i/10..."
    if python -m app.migrate; then
      echo "✅ Migration succeeded on attempt $i"
      break
    else
      echo "❌ Migration failed on attempt $i"
      if [ $i -eq 10 ]; then
        echo "⚠️ Migration failed after 10 attempts"
        echo "⚠️ Database may not be ready - check Fly.io PostgreSQL status"
        echo "⚠️ Application will continue running without migrations"
      else
        echo "⏳ Retrying migration in 3 seconds..."
        sleep 3
      fi
    fi
  done
) &

echo "👤 Starting async admin user seeding with retry logic..."
(
  sleep 10
  
  for i in $(seq 1 5); do
    echo "Admin seeding attempt $i/5..."
    if python -m app.seed_admin; then
      echo "✅ Admin seeding succeeded on attempt $i"
      break
    else
      echo "❌ Admin seeding failed on attempt $i"
      if [ $i -eq 5 ]; then
        echo "⚠️ Admin seeding failed after 5 attempts"
        echo "⚠️ Admin user may need to be created manually"
      else
        echo "⏳ Retrying admin seeding in 3 seconds..."
        sleep 3
      fi
    fi
  done
) &

echo "✅ Uvicorn server started (PID: $UVICORN_PID)"
echo "✅ Migration and admin seeding running asynchronously in background"
echo "✅ Application should be responsive immediately for health checks"

wait $UVICORN_PID
