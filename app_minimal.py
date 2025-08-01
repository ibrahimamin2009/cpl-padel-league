#!/usr/bin/env python3
"""
Minimal Flask app for Railway deployment testing
"""

from flask import Flask

# Create Flask app
app = Flask(__name__)

# Basic configuration
app.config['SECRET_KEY'] = 'test-secret-key-for-railway'

# Simple routes
@app.route('/')
def index():
    return "CPL Padel League - Railway Test"

@app.route('/test')
def test():
    return "✅ Railway deployment working!"

@app.route('/health')
def health():
    return "OK"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000) 