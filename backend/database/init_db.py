import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.db import init_db

if __name__ == '__main__':
    init_db()
    print("Database tables created successfully")
