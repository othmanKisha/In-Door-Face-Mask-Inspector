#!/bin/bash
mkdir /app/logs/

touch /app/logs/logs.log \
      /app/logs/access.log \
      /app/logs/error.log

chmod -R +rw /app/logs/

exec gunicorn app:app \
      --bind 0.0.0.0:5000 \
      --workers 2 \
      --threads 2 \
      --worker-class gthread \
      --access-logfile /app/logs/access.log \
      --error-logfile /app/logs/error.log \
      --log-file /app/logs/logs.log \
      --timeout 120
