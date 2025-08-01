#!/usr/bin/env python3
"""
Simple test Flask app for Vercel
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from Vercel! 🚀"

@app.route('/test')
def test():
    return "Test endpoint working! ✅"

if __name__ == '__main__':
    app.run(debug=True) 