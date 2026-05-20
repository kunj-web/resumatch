#!/bin/sh
set -e
cd /app
printf 'Waiting for database to become available...\n'
python - <<'PY'
import asyncio
import os
import time
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
async def wait_for_db(url):
    engine = create_async_engine(url, future=True)
    for _ in range(30):
        try:
            async with engine.connect() as conn:
                await conn.execute(text('SELECT 1'))
            await engine.dispose()
            return
        except Exception:
            time.sleep(1)
    raise SystemExit('Database did not become available in time')
asyncio.run(wait_for_db(os.environ['DATABASE_URL']))
PY
printf 'Running database migrations...\n'
alembic upgrade head
printf 'Starting Uvicorn...\n'
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"