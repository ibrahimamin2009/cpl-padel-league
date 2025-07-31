#!/usr/bin/env python3
"""
WSGI entry point for production deployment
"""
from app import app

# For production (Railway, etc.)
application = app

if __name__ == "__main__":
    # For local development
    app.run(host='0.0.0.0', port=8000) 