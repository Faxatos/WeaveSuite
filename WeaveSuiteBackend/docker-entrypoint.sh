#!/bin/sh

# Wait for PostgreSQL to be ready
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 0.1
done

# Initialize DB
python src/scripts/init_db.py

# Start FastAPI
uvicorn src.main:app --host 0.0.0.0 --port 8000