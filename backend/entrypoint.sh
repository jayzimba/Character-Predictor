#!/bin/sh
set -e
python - <<'PY'
import time
from sqlalchemy.exc import OperationalError
from app.database.session import ensure_database_exists

for attempt in range(1, 31):
    try:
        ensure_database_exists()
        break
    except OperationalError as exc:
        message = str(exc).lower()
        waiting = "2003" in message or "connection refused" in message or "timed out" in message
        if not waiting or attempt == 30:
            raise
        print(f"waiting for database ({attempt}/30): {exc}")
        time.sleep(2)
PY
alembic upgrade head
python -m app.database.seed
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

