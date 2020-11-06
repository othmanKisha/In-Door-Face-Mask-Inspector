#!/bin/bash
mkdir /app/logs/

touch /app/logs/server.log \
      /app/logs/access.log

chmod -R +rw /app/logs/

exec gunicorn app:app \
      --bind 0.0.0.0:5000 \
      --workers 3 \
      --threads 3 \
      --worker-class gthread \
      --access-logfile /app/logs/access.log \
      --log-file /app/logs/server.log \
      --timeout 120
