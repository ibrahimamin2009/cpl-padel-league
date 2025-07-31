#!/usr/bin/env python3
"""
WSGI entry point for production deployment
"""
import os
from app import app, init_db

# Initialize database on startup
with app.app_context():
    init_db()

if __name__ == "__main__":
    # For local development
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
else:
    # For production (Railway, etc.)
    application = app 