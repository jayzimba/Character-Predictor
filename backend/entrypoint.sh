#!/bin/sh
set -e
python -c "from app.database.session import ensure_database_exists; ensure_database_exists()"
alembic upgrade head
python -m app.database.seed
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
