#!/usr/bin/env python3
"""
Simple test to check if Flask can start
"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Flask is working!"

if __name__ == '__main__':
    print("Starting Flask test app...")
    app.run(debug=True, host='0.0.0.0', port=5000)