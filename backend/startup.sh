#!/usr/bin/env bash

# Production startup script for the backend
set -e

echo "Starting production backend..."

# Run database migrations if needed
# alembic upgrade head

# Start the application with uvicorn
exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-7860} --workers 2