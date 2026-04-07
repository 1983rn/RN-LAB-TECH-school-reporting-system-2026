#!/usr/bin/env python3
"""
Minimal Flask App for Render Deployment
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash  # type: ignore[import-not-found]
import os
import sqlite3
import hashlib
import logging

# Basic logging configuration to ensure exceptions are output to the platform logs
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
# Use environment secret key in production; fallback is a development-only value
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-please-change')
if app.secret_key == 'dev-secret-please-change':
    logging.warning('Using default SECRET_KEY; set SECRET_KEY env var for production')

# Allow optionally configuring SERVER_NAME in production so url_for can work
# even outside an active request (useful for template checks and background tasks)
server_name = os.environ.get('SERVER_NAME')
if server_name:
    app.config['SERVER_NAME'] = server_name
    logging.info('Configured SERVER_NAME from environment: %s', server_name)


# Developer credentials should be provided via environment variables in production
DEVELOPER_USERNAME = os.environ.get('DEVELOPER_USERNAME', 'MAKONOKAya')
DEVELOPER_PASSWORD = os.environ.get('DEVELOPER_PASSWORD', 'NAMADEYIMKOLOWEKO1949')

# Health check for deployment platforms
@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'Malawi School Reporting System'})
def init_minimal_db():
    """Initialize minimal database"""
    try:
        conn = sqlite3.connect('school_reports.db')
        cursor = conn.cursor()
        
        # Create minimal students table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_number TEXT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                grade_level INTEGER NOT NULL,
                status TEXT DEFAULT 'Active'
            )
        """)
        
        # Create minimal marks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_marks (
                mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                mark INTEGER NOT NULL,
                grade TEXT NOT NULL,
                term TEXT NOT NULL,
                academic_year TEXT NOT NULL,
                form_level INTEGER NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Database init error: {e}")
        return False

@app.route('/')
def index():
    """Main dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login')
def login():
    """Login page"""
    try:
        return render_template('login.html')
    except Exception as e:
        # Log full exception so deployment logs (e.g., Render) show the traceback
        logging.exception("Error rendering login template")
        # Also print the full traceback to stdout to increase the chance it appears in PaaS logs
        import traceback
        print(traceback.format_exc())
        # Return a minimal response so the error is visible in logs and the platform doesn't fail silently
        return "Internal Server Error", 500


# Debug endpoint to verify template rendering in the deployed environment.
# This is disabled by default; enable by setting the env var ENABLE_TEMPLATE_DEBUG=1
@app.route('/_debug/template-check')
def template_check():
    if os.environ.get('ENABLE_TEMPLATE_DEBUG') != '1':
        return "Not enabled", 404
    try:
        # Render inside a test request context so helpers like url_for work even when
        # there isn't an active external request (this avoids failures seen in PaaS envs)
        with app.test_request_context('/'):
            tpl = app.jinja_env.get_template('login.html')
            _ = tpl.render()
        return "Template OK", 200
    except Exception as e:
        logging.exception("Template check failed")
        import traceback
        tb = traceback.format_exc()
        # Return the short message but log the full traceback; do not expose full traces in production
        return f"Template error: {str(e)}\n\n{tb}", 500

@app.route('/api/login', methods=['POST'])
def api_login():
    """Handle login"""
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        user_type = data['user_type']
        
        if user_type == 'developer':
            if username == DEVELOPER_USERNAME and password == DEVELOPER_PASSWORD:
                session['user_id'] = 'developer'
                session['user_type'] = 'developer'
                return jsonify({'success': True, 'redirect': '/'})
        
        return jsonify({'success': False, 'message': 'Invalid credentials'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('login'))

# Log available template files at import time to help diagnose missing-template issues in deployment
try:
    template_files = []
    if app.template_folder and os.path.isdir(app.template_folder):
        template_files = os.listdir(app.template_folder)
    logging.info("Available templates: %s", template_files)
except Exception:
    logging.exception("Could not list templates folder")

if __name__ == '__main__':
    init_minimal_db()
    app.run(debug=False)