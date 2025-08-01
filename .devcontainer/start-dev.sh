#!/bin/bash

echo "Starting FastAPI server and Celery worker..."

# Start FastAPI in background
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

# Start Celery worker
celery -A app.core.celery_app.celery worker --loglevel=info
