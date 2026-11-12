"""
Gunicorn configuration for the Agent CICO Receiving Service.

Runs the FastAPI app (asgi:application) with UvicornWorker so async handlers
in app/routes/cico.py can await IPS callbacks and agent-lookup HTTP calls.

Troubleshooting:
  - Port conflicts: change bind or stop the process holding 8013.
  - Worker count: workers = 2 * CPU + 1; reduce if memory is tight.
  - Logs: accesslog/errorlog "-" sends both streams to container stdout/stderr.
"""

import multiprocessing
import os
wsgi_app="asgi:app"

# Server socket
bind = os.environ.get("GUNICORN_BIND", "0.0.0.0:8014")

# Worker processes (Rule of thumb: 2-4 workers per core)
# workers = multiprocessing.cpu_count() * 2 + 1
workers=4
worker_class = "uvicorn.workers.UvicornWorker"
timeout =120
proc_name = "cico-receiver-service"

# Logging
loglevel = "info"
accesslog = "-"  # Log to stdout
errorlog = "-"  # Log to stderr