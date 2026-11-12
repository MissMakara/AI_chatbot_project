"""
ASGI entry point for production deployment.

Gunicorn (see gunicorn.conf.py) loads this module and serves `application`,
which is the FastAPI app defined in app/run.py. UvicornWorker handles the
async route handlers used by the CICO receiver.

Troubleshooting:
  - Import errors here usually mean app/run.py or a dependency failed at import
    (often missing configs_local.ini or a bad config section).
  - To test locally without gunicorn: uvicorn asgi:application --host 0.0.0.0 --port 8013
"""

from app.run import app

# Standard ASGI callable name expected by gunicorn / uvicorn.
application=app