web: gunicorn config.wsgi --log-file -
worker: celery worker -A config --loglevel=debug --concurrency=4