# Production WSGI Configuration for JobGlove
# This file is used when running with Gunicorn or other WSGI servers

import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from app import app
from database.db import init_db
from utils.logger import app_logger

# Initialize database on startup
app_logger.info("Initializing database for production...")
init_db()
app_logger.info("Database initialized")

# This is the WSGI callable
application = app

if __name__ == "__main__":
    # This block is only for direct execution
    # In production, use: gunicorn -w 4 -b 0.0.0.0:5000 wsgi:application
    app.run(host='0.0.0.0', port=5000)
