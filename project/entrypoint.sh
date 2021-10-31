#!/bin/sh
redis-server ./redis/redis.conf
celery --app=app.worker worker --detach
alembic upgrade head
# uvicorn app.main:app --reload --workers 1 --host 0.0.0.0 --port 8000
gunicorn --workers 2 --worker-class=uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app.main:app