#!/bin/sh
set -e

# Run database initialization
python -c "from app.main import init_db; init_db()"

# Start Gunicorn
exec gunicorn -w 2 -b 0.0.0.0:5000 app.main:app