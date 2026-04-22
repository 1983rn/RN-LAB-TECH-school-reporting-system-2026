#!/usr/bin/env python3
"""
Malawi School Reporting System - Web Application
Flask-based web interface for school report generation

Created by: RN_LAB_TECH
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for, session, make_response
from werkzeug.utils import secure_filename
import os
import sys
import traceback
from datetime import datetime
import json
import hashlib
import zipfile
import io
import secrets
# import sqlite3 # No longer needed, using PostgreSQL via psycopg2
import pandas as pd

# Add current directory to path 
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from termly_report_generator import TermlyReportGenerator
from performance_analyzer import PerformanceAnalyzer
from school_database import SchoolDatabase
from multi_user_manager import SchoolUserManager

app = Flask(__name__, template_folder='templates', static_folder='static')

# Signature Upload Configuration
UPLOAD_FOLDER = os.path.join(current_dir, 'static', 'uploads', 'signatures')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Use environment-provided SECRET_KEY in production
app.secret_key = os.environ.get('SECRET_KEY')
if not app.secret_key:
    import secrets
    app.secret_key = secrets.token_hex(32)
    print('WARNING: Generated temporary SECRET_KEY; set SECRET_KEY env var for production')

# Configure Flask for production when deployed
if os.environ.get('FLASK_ENV') == 'production':
    app.config['ENV'] = 'production'
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
else:
    # Development mode - ensure debug is controlled by environment
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'

# Track initialization status
INIT_OK = True

# Track whether system components initialized successfully. If False, the
# module will not raise at import time so the CLI can show a user-friendly
# message and pause instead of the window closing immediately.
INIT_OK = True


def _show_windows_messagebox(title: str, message: str) -> None:
    """Show a simple Windows message box when no console is available."""
    try:
        import ctypes
        # MB_OK | MB_ICONERROR = 0x00000000 | 0x00000010
        ctypes.windll.user32.MessageBoxW(0, message, title, 0x00000010)
    except Exception as e:
        # Fall back to printing if MessageBox is not available
        print(f"MessageBox error: {e}")
        print(title)
        print(message)


def show_error_message(title: str, message: str) -> None:
    """Display an error message. Use Windows MessageBox when appropriate,
    otherwise print and pause interactively so the console doesn't close
    immediately when double-clicking the script."""
    is_console = False
    try:
        is_console = sys.stdin is not None and sys.stdin.isatty()
    except Exception:
        is_console = False

    if os.name == 'nt' and not is_console:
        _show_windows_messagebox(title, message)
    else:
        # Interactive console: print details and wait for a keystroke so users
        # running from a terminal or double-clicking the .bat can see the error.
        print('\n' + title)
        print(message)
        if is_console:
            try:
                input('Press Enter to exit...')
            except Exception as e:
                print(f"Error in input handling: {e}")


import bcrypt

# Developer credentials - use environment variables or secure defaults
# Note: In production, set DEVELOPER_USERNAME and DEVELOPER_PASSWORD_HASH env vars
DEVELOPER_USERNAME = os.environ.get('DEVELOPER_USERNAME', 'MAKONOKAya')
# Default hash for NAMADEYIMKOLOWEKO1949 (can be overridden via environment)
DEVELOPER_PASSWORD_HASH = os.environ.get('DEVELOPER_PASSWORD_HASH', 
    '$2b$12$/UCr8jdGrSXBlinn0nPuXuku5QkIfJ1YB78Z31NHxVYgWtxKhKZty')

def hash_password(password):
    # bcrypt is a binary extension; some linters/Pylance can't infer attributes.
    # Silence attribute-access diagnostics while keeping runtime behavior.
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')  # type: ignore[attr-defined]

def verify_password(password, hashed):
    # type: ignore[attr-defined]
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))  # type: ignore[attr-defined]

def check_auth():
    return 'user_id' in session and 'user_type' in session

def check_developer_auth():
    return session.get('user_type') == 'developer'

def get_current_school_id():
    """Get current school ID from session"""
    if session.get('user_type') == 'school':
        return session.get('user_id')
    elif session.get('user_type') == 'school_user':
        return session.get('school_id')
    return None

def require_school_auth():
    """Decorator to require school authentication"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            school_id = get_current_school_id()
            if not school_id:
                return jsonify({'success': False, 'message': 'School authentication required'}), 403
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

def check_subscription_status():
    """Check if school subscription is valid"""
    if session.get('user_type') == 'school':
        days_remaining = session.get('days_remaining', 0)
        if days_remaining <= 0:
            return False
    return True

@app.context_processor
def inject_school_settings():
    """Make school settings available to all templates"""
    school_settings = {}
    try:
        user_type = session.get('user_type')
        school_id = None
        
        if user_type == 'school':
            school_id = session.get('user_id')
        elif user_type == 'school_user':
            school_id = session.get('school_id')
            
        if school_id:
            school_name_from_session = session.get('school_name', '')
            # Try to get settings from database if db is available
            try:
                # Access db from global scope
                school_settings = db.get_school_settings(school_id)
                # Ensure school_name exists in settings
                if not school_settings.get('school_name') and school_name_from_session:
                    school_settings['school_name'] = school_name_from_session
            except (NameError, AttributeError, Exception) as e:
                # Fallback to session data
                school_settings = {'school_name': school_name_from_session}
        else:
            school_settings = {'school_name': session.get('school_name', '')}
    except Exception as e:
        # Always return a dict, even if there's an error
        school_settings = {'school_name': session.get('school_name', '')}
    
    # Always return school_settings, even if empty
    return dict(school_settings=school_settings)

@app.before_request
def before_request():
    """Check subscription status before each request"""
    # Skip subscription check for login, logout, and developer routes
    exempt_routes = ['login', 'api_login', 'logout', 'developer_dashboard', 'health']
    exempt_prefixes = ['/api/developer/', '/static/']
    
    if request.endpoint in exempt_routes:
        return
    
    for prefix in exempt_prefixes:
        if request.path.startswith(prefix):
            return
    
    # For API endpoints, return JSON error instead of redirect
    if request.path.startswith('/api/'):
        if not check_auth():
            return jsonify({
                'success': False,
                'message': 'Authentication required. Please login first.',
                'redirect': '/login'
            }), 403
        
        # Check subscription status for schools
        if session.get('user_type') == 'school' and not check_subscription_status():
            session.clear()
            return jsonify({
                'success': False,
                'message': 'Your subscription has expired. Please contact the administrator to renew.',
                'redirect': '/login'
            }), 403
    else:
        # For regular pages, use redirect
        if not check_auth():
            return redirect(url_for('login'))
        
        # Check subscription status for schools
        if session.get('user_type') == 'school' and not check_subscription_status():
            session.clear()
            flash('Your subscription has expired. Please contact the administrator to renew.', 'error')
            return redirect(url_for('login'))

# Initialize system components with error handling
db = None
user_manager = None
generator = None
analyzer = None

try:
    db = SchoolDatabase()
    user_manager = SchoolUserManager(db)
    user_manager.create_school_users_table()  # Verifies tables exist in Postgres
    generator = TermlyReportGenerator(
        school_name="[ENTER SCHOOL NAME]",
        school_address="[ENTER ADDRESS]",
        school_phone="[ENTER PHONE]",
        school_email="[ENTER EMAIL]"
    )
    analyzer = PerformanceAnalyzer("[ENTER SCHOOL NAME]")
    print("SUCCESS: System components initialized successfully")
except Exception as e:
    # Record the initialization failure so the CLI can report it cleanly
    print(f"ERROR: Error initializing system components: {e}")
    import traceback
    traceback.print_exc()
    INIT_OK = False
    
    # If we are in production, re-raise the exception to prevent the app from starting in a broken state
    if os.environ.get('RENDER') or os.environ.get('FLASK_ENV') == 'production':
        raise
        
    # Use the user-friendly display routine when appropriate so double-clicking
    # the script on Windows doesn't flash and close without giving feedback.
    try:
        show_error_message('Initialization Error', f"Error initializing system components: {e}\nSee the console/log for the full traceback.")
    except Exception as e:
        # If the helper fails, fall back to the printed traceback above
        print(f"Error showing message: {e}")
    # Do not re-raise here so the __main__ block can display a friendly
    # message (useful when users double-click the script on Windows).
    # The server will not start if INIT_OK is False.


@app.route('/')
def index():
    """Main dashboard with form selection"""
    if not check_auth():
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/multi-user-dashboard')
def multi_user_dashboard():
    """Multi-user dashboard for school users"""
    if 'user_type' not in session or session.get('user_type') != 'school_user':
        return redirect(url_for('login'))
    
    try:
        school_id = session.get('school_id')
        assigned_forms = session.get('assigned_forms', [])
        full_name = session.get('full_name')
        role = session.get('role')
        
        # Get school settings (shared across all users)
        school_settings = db.get_school_settings(school_id)
        
        return render_template('multi_user_dashboard.html', 
                         school_settings=school_settings,
                         assigned_forms=assigned_forms,
                         full_name=full_name,
                         role=role,
                         school_name=session.get('school_name'))
    except Exception as e:
        print(f"Error in multi-user dashboard: {e}")
        return render_template('error.html', error="Dashboard loading failed")

@app.route('/form/<int:form_level>/multi-user')
def form_data_entry_multi_user(form_level):
    """Multi-user data entry page with conflict prevention"""
    if 'user_type' not in session or session.get('user_type') != 'school_user':
        return redirect(url_for('login'))
    
    try:
        school_id = session.get('school_id')
        user_id = session.get('school_user_id')
        assigned_forms = session.get('assigned_forms', [])
        
        # Check if user is assigned to this form
        if form_level not in assigned_forms:
            return render_template('error.html', 
                             error=f"You are not assigned to Form {form_level}. "
                                   f"Your assigned forms: {assigned_forms}")
        
        # Check for access conflicts
        access_check = user_manager.check_form_access_conflict(user_id, form_level)
        
        if not access_check['can_access']:
            return render_template('error.html', 
                             error=access_check['reason'],
                             details=access_check.get('active_users', []))
        
        # Log form access
        user_manager.log_user_activity(
            user_id, 'form_access', form_level,
            details=f"User accessed Form {form_level} data entry"
        )
        
        # Get terms and academic years from school settings
        settings = db.get_school_settings(school_id) if hasattr(db, 'get_school_settings') else {}
        terms = settings.get('terms') or ['Term 1', 'Term 2', 'Term 3']
        academic_years = settings.get('academic_years') or [f'{y}-{y+1}' for y in range(2025, 2036)]
        
        # Get selected term and academic year from settings
        selected_term = settings.get('selected_term', '')
        selected_academic_year = settings.get('selected_academic_year', '')
        
        # If no selected values, use defaults
        if not selected_term and terms:
            selected_term = terms[0]
        if not selected_academic_year and academic_years:
            selected_academic_year = academic_years[0]
        
        # Get students enrolled in this form, term, and school - STRICT TERM ISOLATION
        try:
            students = db.get_students_enrolled_in_term(form_level, selected_term, selected_academic_year, school_id)
            
            # ENFORCE: Always show empty list for new terms/academic years
            # No fallback to showing all students - term-specific enrollment required
            if not students:
                print(f"NEW TERM/YEAR: No students enrolled in Form {form_level} for {selected_term} {selected_academic_year}")
                print("Students must be manually enrolled or uploaded for this term/academic year")
            
            # Check if this is a new academic year/term by looking for existing marks
            if selected_term and selected_academic_year:
                has_marks = db.check_marks_exist_for_period(
                    form_level, selected_term, selected_academic_year, school_id
                )
                if not has_marks and not students:
                    print(f"New academic year/term confirmed: {selected_academic_year} {selected_term} - no students enrolled yet")
            
        except Exception as e:
            print(f"Error getting students: {e}")
            students = []
        
        # Get subjects for this form level
        subjects = db.get_subjects_by_form(form_level, school_id)
        
        return render_template('form_data_entry_multi_user.html', 
                         form_level=form_level, 
                         students=students,
                         subjects=subjects,
                         terms=terms,
                         academic_years=academic_years,
                         selected_term=selected_term,
                         selected_academic_year=selected_academic_year,
                         full_name=session.get('full_name'),
                         role=session.get('role'),
                         assigned_forms=assigned_forms)
        
    except Exception as e:
        print(f"Error in multi-user form data entry: {e}")
        return render_template('error.html', error="Failed to load form data entry page")

@app.route('/login')
def login():
    """Login page"""
    return render_template('login.html')

@app.route('/health')
def health():
    """Health check endpoint for deployment platforms"""
    return jsonify({'status': 'ok', 'service': 'Malawi School Reporting System'})

@app.route('/api/login', methods=['POST'])
def api_login():
    """Handle login authentication"""
    try:
        # Validate request content type
        if not request.is_json:
            return jsonify({
                'success': False, 
                'message': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        user_type = data.get('user_type', '').strip()
        
        if not username or not password or not user_type:
            return jsonify({
                'success': False,
                'message': 'Username, password, and user_type are required'
            }), 400
        
        if user_type == 'developer':
            # Developer uses bcrypt hashing
            if username == DEVELOPER_USERNAME and verify_password(password, DEVELOPER_PASSWORD_HASH):
                session['user_id'] = 'developer'
                session['user_type'] = 'developer'
                session['username'] = username
                return jsonify({'success': True, 'redirect': '/developer-dashboard'})
        elif user_type == 'school':
            # Check school credentials first
            school = db.authenticate_school(username, password)
            if school:
                # Now check if this is a multi-user login
                if '@' in username or '_' in username:  # Likely a user account
                    # Try to authenticate as school user
                    user = user_manager.authenticate_school_user(username, password, school['school_id'])
                    if user:
                        session['user_id'] = user['user_id']
                        session['school_user_id'] = user['user_id']
                        session['user_type'] = 'school_user'
                        session['username'] = user['username']
                        session['full_name'] = user['full_name']
                        session['school_id'] = school['school_id']
                        session['school_name'] = school['school_name']
                        session['assigned_forms'] = user['assigned_forms']
                        session['role'] = user['role']
                        session['subscription_status'] = school['subscription_status']
                        session['days_remaining'] = school['days_remaining']
                        
                        # Log user activity
                        user_manager.log_user_activity(
                            user['user_id'], 'login', 
                            details=f"User {user['username']} logged in"
                        )
                        
                        return jsonify({
                            'success': True, 
                            'redirect': '/multi-user-dashboard',
                            'user_info': {
                                'full_name': user['full_name'],
                                'assigned_forms': user['assigned_forms'],
                                'role': user['role']
                            }
                        })
                
                # Fallback to school admin login
                session['user_id'] = school['school_id']
                session['user_type'] = 'school'
                session['username'] = username
                session['school_name'] = school['school_name']
                session['subscription_status'] = school['subscription_status']
                session['days_remaining'] = school['days_remaining']

                # If developer provided an OTP temporary password, force change on first login
                if school.get('must_change_password'):
                    session['must_change_password'] = True
                    return jsonify({'success': True, 'redirect': '/change-password', 'must_change_password': True})

                # Check if subscription is expired
                if school['days_remaining'] <= 0:
                    return jsonify({
                        'success': False, 
                        'message': 'Your subscription has expired. Please contact the administrator to renew your subscription.'
                    })

                return jsonify({'success': True, 'redirect': '/'})
        
        return jsonify({'success': False, 'message': 'Invalid credentials'})
        
    except Exception as e:
        import traceback
        print(f"Login error: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': f'Login error: {str(e)}'}), 500

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/developer-dashboard')
def developer_dashboard():
    """Developer dashboard"""
    if not check_developer_auth():
        return redirect(url_for('login'))
    return render_template('developer_dashboard.html')


@app.route('/change-password')
def change_password_page():
    """Page where schools change their temporary OTP password on first login"""
    if session.get('user_type') != 'school':
        return redirect(url_for('login'))
    # If the session does not indicate a forced change, allow access but still render
    return render_template('change_password.html')


@app.route('/api/change-password', methods=['POST'])
def api_change_password():
    """API endpoint for schools to change their password"""
    try:
        if session.get('user_type') != 'school':
            return jsonify({'success': False, 'message': 'School authentication required'}), 403

        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type must be application/json'}), 400

        data = request.get_json()
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')

        if not new_password or not confirm_password or new_password != confirm_password:
            return jsonify({'success': False, 'message': 'Passwords do not match or are empty'}), 400

        school_id = get_current_school_id()
        if not school_id:
            return jsonify({'success': False, 'message': 'School authentication required'}), 403

        db.update_school_password(school_id, new_password)
        # Clear the session flag
        session.pop('must_change_password', None)

        return jsonify({'success': True, 'message': 'Password changed successfully', 'redirect': '/'})

    except Exception as e:
        import traceback
        print(f"Error changing password: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': f'Error changing password: {str(e)}'}), 500

@app.route('/api/user-heartbeat', methods=['POST'])
def api_user_heartbeat():
    """Update user activity heartbeat"""
    try:
        if not check_auth():
            return jsonify({'success': False, 'message': 'Authentication required'}), 403
        
        data = request.get_json()
        user_id = data.get('user_id')
        form_level = data.get('form_level')
        activity = data.get('activity', 'active')
        
        if user_id and form_level:
            user_manager.log_user_activity(
                user_id, activity, form_level,
                details=f"User heartbeat: {activity}"
            )
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error updating heartbeat: {str(e)}'})

@app.route('/api/check-form-conflicts', methods=['POST'])
def api_check_form_conflicts():
    """Check for form access conflicts"""
    try:
        if not check_auth():
            return jsonify({'success': False, 'message': 'Authentication required'}), 403
        
        data = request.get_json()
        user_id = data.get('user_id')
        form_level = data.get('form_level')
        
        if user_id and form_level:
            access_check = user_manager.check_form_access_conflict(user_id, form_level)
            return jsonify({
                'success': True,
                'conflict': not access_check['can_access'],
                'conflict_info': access_check
            })
        
        return jsonify({'success': False, 'message': 'Invalid parameters'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error checking conflicts: {str(e)}'})

@app.route('/api/user-activity/<int:user_id>')
def api_user_activity(user_id):
    """Get user activity log"""
    try:
        if not check_auth():
            return jsonify({'success': False, 'message': 'Authentication required'}), 403
        
        # Get recent activities for the user
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT activity_type, form_level, details, timestamp
                FROM user_activity_log
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT 10
            """, (user_id,))
            
            activities = []
            for row in cursor.fetchall():
                activities.append({
                    'activity_type': row[0],
                    'form_level': row[1],
                    'details': row[2],
                    'timestamp': row[3]
                })
        
        return jsonify({
            'success': True,
            'activities': activities
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error getting activity: {str(e)}'})

@app.route('/api/check-form-status')
def api_check_form_status():
    """Check status of all forms for conflicts"""
    try:
        if not check_auth():
            return jsonify({'success': False, 'message': 'Authentication required'}), 403
        
        # Get active conflicts for all forms
        conflicts = []
        for form_level in [1, 2, 3, 4]:
            active_users = user_manager.get_active_users_on_form(form_level, minutes=2)
            if active_users:
                conflicts.append({
                    'form_level': form_level,
                    'users': active_users
                })
        
        return jsonify({
            'success': True,
            'conflicts': conflicts
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error checking form status: {str(e)}'}), 500

@app.route('/api/delete-student', methods=['POST'])
def api_delete_student():
    """Delete a student and all their marks"""
    try:
        if not check_auth():
            return jsonify({'success': False, 'message': 'Authentication required'}), 403
        
        data = request.get_json()
        student_id = data.get('student_id')
        form_level = data.get('form_level')
        
        if not student_id:
            return jsonify({'success': False, 'message': 'Student ID is required'}), 400
        
        # Get school ID from session
        school_id = get_current_school_id()
        if not school_id:
            return jsonify({'success': False, 'message': 'School not found'}), 400
        
        # Verify student belongs to this school and form
        student = db.get_student_by_id(student_id, school_id)
        if not student or student.get('school_id') != school_id:
            return jsonify({'success': False, 'message': 'Student not found'}), 404
        
        # Delete student and all their marks
        success = db.delete_student(student_id, school_id)
        
        if success:
            # Log the activity if multi-user
            if session.get('user_type') == 'school_user':
                user_id = session.get('school_user_id')
                if user_id:
                    user_manager.log_user_activity(
                        user_id, 'delete_student', form_level,
                        details=f"Deleted student {student['first_name']} {student['last_name']} (ID: {student_id})"
                    )
            
            return jsonify({
                'success': True, 
                'message': f'Student {student["first_name"]} {student["last_name"]} deleted successfully'
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to delete student'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error deleting student: {str(e)}'}), 500

@app.route('/api/update-student-name', methods=['POST'])
def api_update_student_name():
    """Update a student's name"""
    try:
        if not check_auth():
            return jsonify({'success': False, 'message': 'Authentication required'}), 403
        
        data = request.get_json()
        student_id = data.get('student_id')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        form_level = data.get('form_level')
        
        if not student_id or not first_name or not last_name:
            return jsonify({'success': False, 'message': 'Student ID, first name, and last name are required'}), 400
        
        # Get school ID from session
        school_id = get_current_school_id()
        if not school_id:
            return jsonify({'success': False, 'message': 'School not found'}), 400
        
        # Verify student belongs to this school and form
        student = db.get_student_by_id(student_id, school_id)
        if not student or student.get('school_id') != school_id:
            return jsonify({'success': False, 'message': 'Student not found'}), 404
        
        # Update student name
        success = db.update_student_name(student_id, first_name, last_name, school_id)
        
        if success:
            # Log the activity if multi-user
            if session.get('user_type') == 'school_user':
                user_id = session.get('school_user_id')
                if user_id:
                    user_manager.log_user_activity(
                        user_id, 'edit_student', form_level,
                        details=f"Updated student name from {student['first_name']} {student['last_name']} to {first_name} {last_name} (ID: {student_id})"
                    )
            
            return jsonify({
                'success': True, 
                'message': f'Student name updated to {first_name} {last_name}'
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to update student name'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error updating student name: {str(e)}'}), 500

@app.route('/form/<int:form_level>')
def form_data_entry(form_level):
    """Data entry page for specific form"""
    if form_level not in [1, 2, 3, 4]:
        return redirect(url_for('index'))
    
    school_id = get_current_school_id()
    if not school_id:
        return redirect(url_for('login'))
    
    # Default subject list for all forms (1-4)
    default_subjects = ['Agriculture', 'Bible Knowledge', 'Biology', 'Business Studies', 'Chemistry', 
               'Chichewa', 'Clothing & Textiles', 'Computer Studies', 'English', 'Geography', 
               'History', 'Life Skills/SOS', 'Mathematics', 'Physics', 'Technical Drawing', 'Home Economics']

    # Merge with any per-school subject entries from subject_teachers to ensure subjects are not accidentally omitted
    try:
        teachers_map = db.get_subject_teachers(form_level=form_level, school_id=school_id)
        merged_subjects = sorted(set(default_subjects) | set(teachers_map.keys()))
    except Exception:
        merged_subjects = sorted(default_subjects)

    # Remove Accounting from Form 1 subjects
    if form_level == 1:
        subjects = [s for s in merged_subjects if s != 'Accounting']
    else:
        subjects = merged_subjects
    
    # Get terms and academic years
    settings = db.get_school_settings(school_id) if hasattr(db, 'get_school_settings') else {}
    terms = ['Term 1', 'Term 2', 'Term 3']
    academic_years = [f'{y}-{y+1}' for y in range(2025, 2036)]
    
    # Get selected term and academic year from settings (these are set in the settings page)
    selected_term = settings.get('selected_term', '')
    selected_academic_year = settings.get('selected_academic_year', '')

    # If no selected values, use defaults
    if not selected_term and terms:
        selected_term = terms[0]
    if not selected_academic_year and academic_years:
        selected_academic_year = academic_years[0]

    # Get students enrolled in this form, term, and school - STRICT TERM ISOLATION
    try:
        students = db.get_students_enrolled_in_term(form_level, selected_term, selected_academic_year, school_id)
        
        # ENFORCE: Always show empty list for new terms/academic years
        # No fallback to showing all students - term-specific enrollment required
        if not students:
            print(f"NEW TERM/YEAR: No students enrolled in Form {form_level} for {selected_term} {selected_academic_year}")
            print("Students must be manually enrolled or uploaded for this term/academic year")
        
        # Check if this is a new academic year/term by looking for existing marks
        if selected_term and selected_academic_year:
            has_marks = db.check_marks_exist_for_period(
                form_level, selected_term, selected_academic_year, school_id
            )
            if not has_marks and not students:
                print(f"New academic year/term confirmed: {selected_academic_year} {selected_term} - no students enrolled yet")
        
    except Exception as e:
        print(f"Error getting students: {e}")
        students = []
    
    # If no selected values, use defaults
    if not selected_term and terms:
        selected_term = terms[0]
    if not selected_academic_year and academic_years:
        selected_academic_year = academic_years[0]
    
    return render_template('form_data_entry.html', 
                         form_level=form_level, 
                         subjects=subjects, 
                         students=students,
                         terms=terms,
                         academic_years=academic_years,
                         selected_term=selected_term,
                         selected_academic_year=selected_academic_year)



@app.route('/ranking-analysis')
def ranking_analysis():
    """Ranking and analysis page"""
    school_id = get_current_school_id()
    if not school_id:
        return redirect(url_for('login'))

    # Provide available academic years and current selection so the page can render selects
    settings = db.get_school_settings(school_id)

    # Available lists
    available_years = [f'{y}-{y+1}' for y in range(2025, 2036)]
    available_terms = ['Term 1', 'Term 2', 'Term 3']

    # Use selected values from settings (set in settings page), fallback to first available if not set
    selected_academic_year = settings.get('selected_academic_year', '')
    if not selected_academic_year and available_years:
        selected_academic_year = available_years[0]
    elif not selected_academic_year:
        selected_academic_year = f'{2025}-{2026}'
    
    selected_term = settings.get('selected_term', '')
    if not selected_term and available_terms:
        selected_term = available_terms[0]
    elif not selected_term:
        selected_term = 'Term 1'

    return render_template('ranking_analysis.html', available_years=available_years, selected_academic_year=selected_academic_year, available_terms=available_terms, selected_term=selected_term)

@app.route('/settings')
def settings():
    """Settings page"""
    school_id = get_current_school_id()
    if not school_id:
        return redirect(url_for('login'))
    
    # Get current settings for this school
    settings_obj = db.get_school_settings(school_id)
    terms = ['Term 1', 'Term 2', 'Term 3']
    academic_years = [f'{y}-{y+1}' for y in range(2025, 2036)]

    # Provide selectable ranges for the UI
    available_years = [f'{y}-{y+1}' for y in range(2025, 2036)]
    available_terms = ['Term 1', 'Term 2', 'Term 3']

    # Fetch current subject teachers for Forms 1-4 so the settings page can render them server-side
    subject_teachers_by_form = {}
    if school_id:
        for form_level in [1, 2, 3, 4]:
            subject_teachers_by_form[form_level] = db.get_subject_teachers(form_level=form_level, school_id=school_id)

    import json as json_mod
    junior_grading_json = json_mod.dumps(settings_obj.get('junior_grading_rules', []))
    senior_grading_json = json_mod.dumps(settings_obj.get('senior_grading_rules', []))

    return render_template('settings.html', terms=terms, academic_years=academic_years, settings=settings_obj, available_years=available_years, available_terms=available_terms, subject_teachers=subject_teachers_by_form, junior_grading_json=junior_grading_json, senior_grading_json=senior_grading_json)

@app.route('/grading-config')
def grading_config():
    """Grading system configuration page"""
    school_id = get_current_school_id()
    if not school_id:
        return redirect(url_for('login'))
    
    settings_obj = db.get_school_settings(school_id)
    
    import json as json_mod
    junior_grading_json = json_mod.dumps(settings_obj.get('junior_grading_rules', []))
    senior_grading_json = json_mod.dumps(settings_obj.get('senior_grading_rules', []))
    
    return render_template('grading_config.html', settings=settings_obj, junior_grading_json=junior_grading_json, senior_grading_json=senior_grading_json)

@app.route('/api/save-student-marks', methods=['POST'])
def api_save_student_marks():
    """Save student marks from data entry"""
    try:
        school_id = get_current_school_id()
        if not school_id:
            return jsonify({'success': False, 'message': 'School authentication required'}), 403
        
        data = request.get_json()
        student_id = data['student_id']
        form_level = data['form_level']
        term = data['term']
        academic_year = data['academic_year']
        marks = data['marks']  # Dictionary of subject: mark
        
        app.logger.info(f"DEBUG: Saving marks for student {student_id} (School: {school_id})")
        app.logger.info(f"DEBUG: Marks data to save: {marks}")
        
        # Save marks to database with school_id
        for subject, mark in marks.items():
            if mark is not None and str(mark).strip():
                mark_value = int(str(mark).strip())
                
                # Fetch old mark for logging
                old_marks = db.get_student_marks(student_id, term, academic_year, school_id)
                old_mark = old_marks.get(subject, {}).get('mark', 'None')
                app.logger.info(f"DEBUG: Before Update: old_mark for {subject} = {old_mark}")
                
                db.save_student_mark(student_id, subject, mark_value, term, academic_year, form_level, school_id)
                app.logger.info(f"DEBUG: After Update: new_mark for {subject} = {mark_value}")
        
        app.logger.info(f"Marks updated successfully for student: {student_id}")
        return jsonify({
            'success': True,
            'message': 'Marks saved successfully'
        })
        
    except Exception as e:
        app.logger.error(f"Error saving marks: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error saving marks: {str(e)}'
        })

@app.route('/api/load-student-marks', methods=['GET'])
def api_load_student_marks():
    """Load existing marks for a student"""
    try:
        school_id = get_current_school_id()
        if not school_id:
            return jsonify({'success': False, 'message': 'School authentication required'}), 403
        
        student_id = int(request.args.get('student_id'))
        term = request.args.get('term')
        academic_year = request.args.get('academic_year')
        
        app.logger.info(f"DEBUG: Loading marks for student {student_id} (School: {school_id}, Term: {term}, Year: {academic_year})")
        
        marks = db.get_student_marks(student_id, term, academic_year, school_id)
        
        # Convert to format expected by frontend
        marks_data = {}
        for subject, data in marks.items():
            marks_data[subject] = data['mark']
            
        app.logger.info(f"DEBUG: Retrieved marks from database: {marks_data} for student {student_id}")
        
        response = make_response(jsonify({
            'success': True,
            'marks': marks_data,
            'debug_info': {
                'student_id': student_id,
                'school_id': school_id,
                'term': term,
                'academic_year': academic_year,
                'total_marks': len(marks_data)
            }
        }))
        # Strong cache control to prevent browser caching
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0, private'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        response.headers['Vary'] = 'Cookie, Authorization'
        return response
        
    except Exception as e:
        app.logger.error(f"Error loading marks: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error loading marks: {str(e)}'
        })

@app.route('/api/get-subject-teachers', methods=['GET'])
def api_get_subject_teachers():
    """Return subject teacher mapping for a form level for the current school"""
    try:
        school_id = get_current_school_id()
        if not school_id:
            return jsonify({'success': False, 'message': 'School authentication required'}), 403

        form_level = int(request.args.get('form_level', 1))
        teachers = db.get_subject_teachers(form_level=form_level, school_id=school_id)
        return jsonify({'success': True, 'teachers': teachers})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/clear-form-data', methods=['POST'])
def api_clear_form_data():
    """Clear all student names and marks for a specific form, term, and academic year"""
    try:
        school_id = get_current_school_id()
        if not school_id:
            return jsonify({'success': False, 'message': 'School authentication required'}), 403

        data = request.get_json()
        form_level = int(data.get('form_level'))
        term = (data.get('term') or '').strip()
        academic_year = (data.get('academic_year') or '').strip()
        
        if not all([form_level, term, academic_year]):
            return jsonify({'success': False, 'message': 'Missing required parameters'}), 400

        app.logger.info(f"Clearing data request: Form {form_level}, {term} {academic_year}, School {school_id}")
        
        # Get counts before clearing for confirmation
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Count students enrolled in this form/term/year
            cursor.execute("""
                SELECT COUNT(*) FROM student_term_enrollment 
                WHERE form_level = ? AND term = ? AND academic_year = ? AND school_id = ?
            """, (form_level, term, academic_year, school_id))
            student_count = cursor.fetchone()[0]
            
            # Count marks directly by the same dimensions used during upload/save.
            cursor.execute("""
                SELECT COUNT(*) FROM student_marks
                WHERE form_level = ? AND term = ? AND academic_year = ? AND school_id = ?
            """, (form_level, term, academic_year, school_id))
            marks_count = cursor.fetchone()[0]
        
        if student_count == 0 and marks_count == 0:
            return jsonify({
                'success': False, 
                'message': 'No data found to clear for this form and term',
                'student_count': 0,
                'marks_count': 0
            })
        
        # Clear the data
        cleared_students = 0
        cleared_marks = 0
        
        try:
            # First, clear all marks for students in this form/term/year
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Delete marks directly by form/term/year/school.
                # This clears orphaned marks even when enrollment rows are missing.
                cursor.execute("""
                    DELETE FROM student_marks 
                    WHERE form_level = ? AND term = ? AND academic_year = ? AND school_id = ?
                """, (form_level, term, academic_year, school_id))
                cleared_marks = cursor.rowcount
                
                # Delete student enrollments for this form/term/year
                cursor.execute("""
                    DELETE FROM student_term_enrollment 
                    WHERE form_level = ? AND term = ? AND academic_year = ? AND school_id = ?
                """, (form_level, term, academic_year, school_id))
                cleared_students = cursor.rowcount
                
                conn.commit()
                
            app.logger.info(f"Cleared data: {cleared_students} students, {cleared_marks} marks")
            
            return jsonify({
                'success': True,
                'message': f'Successfully cleared data for Form {form_level}, {term} {academic_year}',
                'cleared_students': cleared_students,
                'cleared_marks': cleared_marks,
                'form_level': form_level,
                'term': term,
                'academic_year': academic_year
            })
            
        except Exception as e:
            app.logger.error(f"Error clearing data: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error clearing data: {str(e)}'
            }), 500

    except Exception as e:
        app.logger.error(f"Error in clear form data API: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error processing request: {str(e)}'
        }), 500

@app.route('/api/update-subject-teacher', methods=['POST'])
def api_update_subject_teacher():
    """Update or insert a subject-teacher assignment for the current school"""
    try:
        school_id = get_current_school_id()
        if not school_id:
            return jsonify({'success': False, 'message': 'School authentication required'}), 403

        data = request.get_json()
        subject = data.get('subject')
        form_level = int(data.get('form_level'))
        teacher_name = data.get('teacher_name', '').strip()

        db.update_subject_teacher(subject, form_level, teacher_name, school_id)
        return jsonify({'success': True, 'message': 'Teacher updated'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/delete-subject-teacher', methods=['POST'])
def api_delete_subject_teacher():
    """Delete a subject-teacher assignment for the current school"""
    try:
        school_id = get_current_school_id()
        if not school_id:
            return jsonify({'success': False, 'message': 'School authentication required'}), 403

        data = request.get_json()
        subject = data.get('subject')
        form_level = int(data.get('form_level'))

        success = db.delete_subject_teacher(subject, form_level, school_id)
        if success:
            return jsonify({'success': True, 'message': 'Teacher assignment deleted'})
        else:
            return jsonify({'success': False, 'message': 'No matching assignment found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/generate-report-card', methods=['POST'])
def api_generate_report_card():
    """Generate report card for a student"""
    try:
        school_id = get_current_school_id()
        if not school_id:
            return jsonify({'success': False, 'message': 'School authentication required'}), 403
        
        data = request.get_json()
        student_id = int(data['student_id'])
        term = data['term']
        academic_year = data['academic_year']
        
        report = generator.generate_progress_report(student_id, term, academic_year, school_id)
        
        if report:
            return jsonify({
                'success': True,
                'report': report
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No report data available for this student'
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating report: {str(e)}'
        })

@app.route('/api/export-report-card', methods=['GET', 'POST'], strict_slashes=False)
def api_export_report_card():
    """Export report card as PDF"""
    try:
        school_id = get_current_school_id()
        if not school_id:
            return jsonify({'success': False, 'message': 'School authentication required'}), 403
        
        # Support both JSON POST and GET/Form parameters
        if request.method == 'POST' and request.is_json:
            data = request.get_json()
            student_id_raw = data.get('student_id')
            term = data.get('term')
            academic_year = data.get('academic_year')
        else:
            # Fallback to args (GET) or form (POST)
            student_id_raw = request.args.get('student_id') or request.form.get('student_id')
            term = request.args.get('term') or request.form.get('term')
            academic_year = request.args.get('academic_year') or request.form.get('academic_year')
            
        if not student_id_raw or not term or not academic_year:
            return jsonify({'success': False, 'message': 'Missing required parameters: student_id, term, and academic_year are required'}), 400
            
        student_id = int(student_id_raw)
        
        print(f"DEBUG [PDF Export]: Request for student_id={student_id}, term='{term}', year='{academic_year}', school_id={school_id}")

        student = db.get_student_by_id(student_id, school_id)
        if not student:
            print(f"DEBUG [PDF Export]: Student ID {student_id} not found in database")
            return jsonify({'success': False, 'message': f'Student with ID {student_id} not found'}), 404
        
        # Verify school ID
        if student.get('school_id') and student['school_id'] != school_id:
             print(f"DEBUG [PDF Export]: Unauthorized - Student {student_id} belongs to school {student['school_id']}, not {school_id}")
             return jsonify({'success': False, 'message': 'Unauthorized access to student record'}), 403

        print(f"DEBUG [PDF Export]: Generating report for learner: {student['first_name']} {student['last_name']} (ID: {student_id})")
        
        # Use a lightweight existence check to avoid loading full marks twice.
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 1 FROM student_marks
                WHERE student_id = ? AND term = ? AND academic_year = ? AND school_id = ?
                LIMIT 1
            """, (student_id, term, academic_year, school_id))
            has_marks = cursor.fetchone() is not None

        if not has_marks:
            print(f"DEBUG [PDF Export]: No marks found for student {student_id} in {term} {academic_year}")
            return jsonify({'success': False, 'message': 'No marks found for this student'}), 404
        
        pdf_bytes = generator.export_report_to_pdf_bytes(student_id, term, academic_year, school_id)
        
        if pdf_bytes and len(pdf_bytes) > 100:  # Valid PDFs are usually > 100 bytes
            # Verify PDF signature (%PDF-)
            if not pdf_bytes.startswith(b'%PDF-'):
                 print(f"DEBUG [PDF Export]: Warning! Generated bytes for {student_id} do not start with %PDF- signature.")
                 # Fallback to check if it's text
                 if b'================' in pdf_bytes or b'Student Name:' in pdf_bytes:
                     return jsonify({'success': False, 'message': 'Internal error: PDF generator returned text instead of PDF binary. Verify library installation.'}), 500

            safe_name = f"{student['first_name']}_{student['last_name']}".replace(' ', '_')
            filename = f"{safe_name}_Report_{term.replace(' ','_')}_{academic_year.replace('-','_')}.pdf"
            
            print(f"DEBUG [PDF Export]: Successfully generated {len(pdf_bytes)} bytes for {filename}")
            
            response = make_response(pdf_bytes)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'inline; filename="{filename}"'
            return response
        else:
            print(f"DEBUG [PDF Export]: PDF generation returned invalid or empty content for student {student_id}")
            return jsonify({
                'success': False,
                'message': 'Failed to generate PDF report - empty or invalid content. Please check server logs.'
            }), 500
        
    except Exception as e:
        import traceback
        print(f"CRITICAL [PDF Export Error]: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': f'Internal error during PDF export: {str(e)}'
        }), 500

@app.route('/api/print-all-reports')
def api_print_all_reports():
    """Generate and download all report cards for a form as a single combined PDF"""
    try:
        school_id = get_current_school_id()
        if not school_id:
            return jsonify({'success': False, 'message': 'School authentication required'}), 403
        
        form_level = int(request.args.get('form_level', 1))
        term = request.args.get('term', 'Term 1')
        academic_year = request.args.get('academic_year', '2024-2025')
        
        # Get students enrolled in this term/year (not all students by grade)
        students = db.get_students_enrolled_in_term(form_level, term, academic_year, school_id)
        if not students:
            return jsonify({
                'success': False,
                'message': f'No students found for Form {form_level}, {term} {academic_year}'
            }), 404
        
        # Import PyPDF2 for PDF concatenation
        try:
            from PyPDF2 import PdfReader, PdfWriter
        except ImportError:
            # Fallback to pypdf if PyPDF2 is not available
            try:
                from pypdf import PdfReader, PdfWriter
            except ImportError:
                return jsonify({
                    'success': False,
                    'message': 'PDF library not available. Please install PyPDF2 or pypdf.'
                }), 500
        
        # Build a set of students that actually have marks for this period.
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT student_id
                FROM student_marks
                WHERE form_level = ? AND term = ? AND academic_year = ? AND school_id = ?
            """, (form_level, term, academic_year, school_id))
            students_with_marks = {row[0] for row in cursor.fetchall()}

        if not students_with_marks:
            return jsonify({
                'success': False,
                'message': f'No marks found for Form {form_level}, {term} {academic_year}'
            }), 404

        # Keep existing student ordering but only generate reports for students with marks.
        students = [s for s in students if s.get('student_id') in students_with_marks]
        if not students:
            return jsonify({
                'success': False,
                'message': f'No students with marks found for Form {form_level}, {term} {academic_year}'
            }), 404

        successful_reports = 0

        # Create the combined PDF directly in memory (avoid temp file I/O).
        writer = PdfWriter()

        # Generate and append each student's PDF.
        for student in students:
            try:
                pdf_bytes = generator.export_report_to_pdf_bytes(student['student_id'], term, academic_year, school_id)

                if pdf_bytes and pdf_bytes.startswith(b'%PDF-'):
                    reader = PdfReader(io.BytesIO(pdf_bytes))
                    for page in reader.pages:
                        writer.add_page(page)
                    successful_reports += 1
                else:
                    app.logger.warning(f"No PDF generated for student {student['first_name']} {student['last_name']}")
            except Exception as e:
                app.logger.error(f"Error generating report for {student['first_name']} {student['last_name']}: {e}")
                continue

        if successful_reports == 0:
            return jsonify({
                'success': False,
                'message': 'No report cards could be generated for any students'
            }), 500

        output_buffer = io.BytesIO()
        writer.write(output_buffer)
        output_buffer.seek(0)
        combined_pdf_bytes = output_buffer.read()
        
        # Create response
        response = make_response(combined_pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename="Form_{form_level}_Report_Cards_{term.replace(" ","_")}_{academic_year.replace("-","_")}.pdf"'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        app.logger.info(f"Generated combined PDF for Form {form_level}, {term} {academic_year}: {successful_reports}/{len(students)} reports")
        
        return response
        
    except Exception as e:
        app.logger.error(f"Error generating combined PDF reports: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error generating reports: {str(e)}'
        }), 500

@app.route('/api/get-rankings', methods=['GET'])
def api_get_rankings():
    """Get student rankings for analysis"""
    try:
        school_id = get_current_school_id()
        if not school_id:
            return jsonify({'success': False, 'message': 'School authentication required'}), 403
        
        form_level = int(request.args.get('form_level', 1))
        term = request.args.get('term', 'Term 1')
        academic_year = request.args.get('academic_year', '2024-2025')
        
        # Get the rankings data which includes rankings array and counts
        rankings_data = db.get_student_rankings(form_level, term, academic_year, school_id)
        
        # Make sure we have valid rankings data
        if not rankings_data or 'rankings' not in rankings_data:
            return jsonify({
                'success': False,
                'message': 'No ranking data available',
                'rankings': [],
                'total_students': 0,
                'students_with_marks': 0
            })
        
        # Return the rankings array and additional data
        return jsonify({
            'success': True,
            'rankings': rankings_data.get('rankings', []),
            'total_students': rankings_data.get('total_students', 0),
            'students_with_marks': rankings_data.get('students_with_marks', 0)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error loading rankings: {str(e)}'
        })

@app.route('/api/get-top-performers', methods=['GET','POST'])
def api_get_top_performers():
    """Get top performing students"""
    try:
        school_id = get_current_school_id()
        # Allow developer access (developer may inspect data across schools) - only require auth for 'school' users
        if session.get('user_type') == 'school' and not school_id:
            return jsonify({'success': False, 'message': 'School authentication required'}), 403
        
        # Support both GET query params and POST JSON body for tests and API clients
        if request.method == 'POST':
            data = request.get_json() or {}
            form_level = int(data.get('form_level', 1))
            term = data.get('term', 'Term 1')
            academic_year = data.get('academic_year', '2024-2025')
            limit = int(data.get('limit', 10))
        else:
            form_level = int(request.args.get('form_level', 1))
            term = request.args.get('term', 'Term 1')
            academic_year = request.args.get('academic_year', '2024-2025')
            limit = int(request.args.get('limit', 10))
        
        top_performers = db.get_top_performers(form_level, term, academic_year, limit, school_id)
        
        return jsonify({
            'success': True,
            'top_performers': top_performers
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error loading top performers: {str(e)}'
        })

@app.route('/api/get-subject-analysis', methods=['GET'])
def api_get_subject_analysis():
    """Get subject performance analysis"""
    try:
        school_id = get_current_school_id()
        if not school_id:
            return jsonify({'success': False, 'message': 'School authentication required'}), 403
        
        form_level = int(request.args.get('form_level', 1))
        term = request.args.get('term', 'Term 1')
        academic_year = request.args.get('academic_year', '2024-2025')
        
        analysis = db.get_subject_analysis(form_level, term, academic_year, school_id)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error loading subject analysis: {str(e)}'
        })

@app.route('/api/rankings/<int:form_level>', methods=['GET'])
def api_get_rankings_by_form(form_level):
    """Get student rankings for specific form level"""
    try:
        school_id = get_current_school_id()
        if not school_id:
            return jsonify({'success': False, 'message': 'School authentication required'}), 403
        
        term = request.args.get('term', 'Term 1')
        academic_year = request.args.get('academic_year', '2025-2026')
        
        result = db.get_student_rankings(form_level, term, academic_year, school_id)
        
        # Extract rankings array from result dict
        rankings_array = result.get('rankings', []) if isinstance(result, dict) else result
        
        # If no rankings found for current school, provide helpful message
        if not rankings_array:
            return jsonify({
                'success': True,
                'rankings': [],
                'message': f'No ranking data found for Form {form_level}, {term}, {academic_year}. Please ensure marks have been entered for this period.',
                'total_students': result.get('total_students', 0) if isinstance(result, dict) else 0,
                'students_with_marks': result.get('students_with_marks', 0) if isinstance(result, dict) else 0
            })
        
        return jsonify({
            'success': True,
            'rankings': rankings_array,
            'total_students': result.get('total_students', 0) if isinstance(result, dict) else len(rankings_array),
            'students_with_marks': result.get('students_with_marks', 0) if isinstance(result, dict) else len(rankings_array)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error loading rankings: {str(e)}'
        })

@app.route('/api/top-performers/<int:form_level>/<category>', methods=['GET'])
def api_get_top_performers_by_category(form_level, category):
    """Get top performers by category"""
    try:
        school_id = get_current_school_id()
        if not school_id:
            return jsonify({'success': False, 'message': 'School authentication required'}), 403
        
        term = request.args.get('term', 'Term 1')
        academic_year = request.args.get('academic_year', '2025-2026')
        
        performers = db.get_top_performers_by_category(category, form_level, term, academic_year, school_id)
        
        return jsonify({
            'success': True,
            'performers': performers
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error loading top performers: {str(e)}'
        })

@app.route('/api/update-student', methods=['POST'])
def api_update_student():
    """Update student information"""
    try:
        data = request.get_json()
        student_id = int(data['student_id'])
        
        update_data = {
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name')
        }
        
        school_id = get_current_school_id()
        success = db.update_student(student_id, update_data, school_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Student updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Student not found or no changes made'
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating student: {str(e)}'
        })

@app.route('/api/add-student', methods=['POST'])
def api_add_student():
    """Add new student"""
    try:
        school_id = get_current_school_id()
        if not school_id:
            return jsonify({'success': False, 'message': 'School authentication required'}), 403
        
        data = request.get_json()
        
        student_data = {
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'grade_level': data['form_level']
        }
        
        student_id = db.add_student(student_data, school_id)
        
        # Also enroll the student in the current term/year
        term = data.get('term')
        academic_year = data.get('academic_year')
        if term and academic_year:
            db.enroll_student_in_term(student_id, term, academic_year, data['form_level'], school_id)
        
        return jsonify({
            'success': True,
            'message': 'Student added successfully',
            'student_id': student_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error adding student: {str(e)}'
        })


@app.route('/api/upload-students-excel', methods=['POST'])
def api_upload_students_excel():
    """Upload students via Excel file"""
    try:
        school_id = get_current_school_id()
        if not school_id:
            return jsonify({'success': False, 'message': 'School authentication required'}), 403
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file part'}), 400
        
        file = request.files['file']
        form_level = request.form.get('form_level')
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No selected file'}), 400
        
        if not form_level:
            return jsonify({'success': False, 'message': 'Form level is required'}), 400
        
        form_level = int(form_level)

        # Resolve upload period early so duplicates/use cases are scoped consistently.
        term = (request.form.get('term') or '').strip()
        academic_year = (request.form.get('academic_year') or '').strip()

        if not term or not academic_year:
            settings = db.get_school_settings(school_id)
            term = (term or settings.get('selected_term') or '').strip()
            academic_year = (academic_year or settings.get('selected_academic_year') or '').strip()

        if not term or not academic_year:
            return jsonify({
                'success': False,
                'message': 'Term and academic year are required for Excel upload.'
            }), 400
        
        if file and (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
            # Read Excel file
            df = pd.read_excel(file)
            
            # Normalize column names (strip whitespace and handle case)
            df.columns = [str(col).strip() for col in df.columns]
            
            # Required columns
            required_columns = ['First Name', 'Last Name']
            
            # Check if required columns exist (flexible matching)
            found_columns = {}
            for req in required_columns:
                # Try exact, case-insensitive, no-space, underscore
                req_normalized = req.lower().replace(' ', '')
                for col in df.columns:
                    col_normalized = str(col).lower().replace(' ', '').replace('_', '')
                    if col_normalized == req_normalized:
                        found_columns[req] = col
                        break
            
            if len(found_columns) < len(required_columns):
                missing = [req for req in required_columns if req not in found_columns]
                return jsonify({
                    'success': False, 
                    'message': f'Required columns not found: {", ".join(missing)}. Please ensure your Excel file has "First Name" and "Last Name" columns.'
                }), 400
            
            # Find subject columns
            subject_columns = {}
            default_subjects = ['Agriculture', 'Bible Knowledge', 'Biology', 'Business Studies', 'Chemistry', 'Chichewa', 'Clothing & Textiles', 'Computer Studies', 'English', 'Geography', 'History', 'Home Economics', 'Life Skills/SOS', 'Mathematics', 'Physics', 'Technical Drawing']
            
            for subject in default_subjects:
                subj_normalized = subject.lower().replace(' ', '').replace('/', '').replace('&', '')
                for col in df.columns:
                    col_normalized = str(col).lower().replace(' ', '').replace('/', '').replace('&', '').replace('_', '')
                    if col_normalized == subj_normalized:
                        subject_columns[subject] = col
                        break
            
            # Check duplicates only within the selected period and form.
            # Data Entry is term-scoped, so duplicate checks must be too.
            existing_students = db.get_students_enrolled_in_term(form_level, term, academic_year, school_id)
            def normalize_name(name):
                import re
                if not name or str(name).lower() == 'nan':
                    return ""
                return re.sub(r'\s+', ' ', str(name)).strip().lower()

            # Map existing students for quick lookup
            existing_student_map = {f"{normalize_name(s['first_name'])} {normalize_name(s['last_name'])}": s['student_id'] for s in existing_students}
            
            duplicate_action = request.form.get('duplicate_action') # 'skip' or 'maintain' or None
            
            duplicates_found = []
            rows_to_process = []
            
            for index, row in df.iterrows():
                first_name_raw = str(row[found_columns['First Name']]).strip()
                last_name_raw = str(row[found_columns['Last Name']]).strip()
                
                first_name_norm = normalize_name(first_name_raw)
                last_name_norm = normalize_name(last_name_raw)
                
                if not first_name_norm or not last_name_norm:
                    continue
                
                full_name_norm = f"{first_name_norm} {last_name_norm}"
                existing_student_id = existing_student_map.get(full_name_norm)
                is_duplicate = existing_student_id is not None
                
                if is_duplicate:
                    duplicates_found.append(f"{first_name_raw} {last_name_raw}")
                
                # Capture marks for this row
                row_marks = {}
                for subject, col_name in subject_columns.items():
                    mark = row[col_name]
                    if pd.notnull(mark):
                        try:
                            mark_val = int(float(mark))
                            if 0 <= mark_val <= 100:
                                row_marks[subject] = mark_val
                        except (ValueError, TypeError):
                            pass

                rows_to_process.append({
                    'first_name': first_name_raw,
                    'last_name': last_name_raw,
                    'is_duplicate': is_duplicate,
                    'existing_student_id': existing_student_id,
                    'marks': row_marks
                })

            # If duplicates found and no action specified, ask user
            if duplicates_found and not duplicate_action:
                return jsonify({
                    'success': True,
                    'has_duplicates': True,
                    'duplicates': list(set(duplicates_found))[:20], # Show unique names, limit 20
                    'total_duplicates': len(set(duplicates_found)),
                    'message': f'Found {len(set(duplicates_found))} students who may already be enrolled.'
                })

            # Process rows using bulk method
            result = db.bulk_upload_students_data(
                rows_to_process=rows_to_process,
                term=term,
                academic_year=academic_year,
                form_level=form_level,
                school_id=school_id,
                duplicate_action=duplicate_action
            )
            
            if not result.get('success'):
                return jsonify({'success': False, 'message': result.get('message', 'Bulk upload failed')}), 500
            
            success_count = result.get('success_count', 0)
            mark_count = result.get('mark_count', 0)
            fail_count = result.get('fail_count', 0)
            errors = result.get('errors', [])
            
            message = f'Successfully processed students.'
            if success_count > 0:
                message = f'Added {success_count} new students. '
            if mark_count > 0:
                message += f'Saved {mark_count} subject marks. '
            if fail_count > 0:
                message += f'Failed to process {fail_count} records.'
            
            return jsonify({
                'success': True, 
                'message': message,
                'marks_saved': mark_count,
                'failed': fail_count,
                'errors': errors[:10],
                'term': term,
                'academic_year': academic_year
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid file format. Please upload an Excel file (.xlsx or .xls)'}), 400
            
    except Exception as e:
        import traceback
        print(f"Excel upload error: {e}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': f'Error processing Excel file: {str(e)}'
        })


@app.route('/api/get-all-students', methods=['GET'])
def api_get_all_students():
    """Get all students for the current school"""
    try:
        school_id = get_current_school_id()
        if not school_id:
            return jsonify({'success': False, 'message': 'School authentication required'}), 403
        
        # Get students from all forms for this school
        all_students = []
        for form_level in [1, 2, 3, 4]:
            students = db.get_students_by_grade(form_level, school_id)
            all_students.extend(students)
        
        return jsonify({
            'success': True,
            'students': all_students
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving students: {str(e)}'
        })

@app.route('/api/upload-signature', methods=['POST'])
def api_upload_signature():
    """Handle signature image uploads"""
    try:
        school_id = get_current_school_id()
        if not school_id:
            return jsonify({'success': False, 'message': 'School authentication required'}), 403
        
        if 'signature' not in request.files:
            return jsonify({'success': False, 'message': 'No file part'}), 400
        
        file = request.files['signature']
        sig_type = request.form.get('type')  # head_teacher, form_1, form_2, etc.
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No selected file'}), 400
        
        valid_types = ['head_teacher', 'form_1', 'form_2', 'form_3', 'form_4']
        if not sig_type or sig_type not in valid_types:
            return jsonify({'success': False, 'message': 'Invalid signature type'}), 400

        if file and allowed_file(file.filename):
            # Extract extension
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = secure_filename(f"{sig_type}_{school_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}")
            
            # Ensure folder for this school exists
            school_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(school_id))
            os.makedirs(school_folder, exist_ok=True)
            
            file_path = os.path.join(school_folder, filename)
            file.save(file_path)
            
            # Relative path for web access and DB storage
            relative_path = f"static/uploads/signatures/{school_id}/{filename}"
            
            # Update database
            db_field = f"{sig_type}_signature" if sig_type == 'head_teacher' else f"{sig_type}_teacher_signature"
            db.update_school_settings({db_field: relative_path}, school_id)
            
            return jsonify({
                'success': True, 
                'message': 'Signature uploaded successfully',
                'path': relative_path
            })
        else:
            return jsonify({'success': False, 'message': 'Allowed file types: png, jpg, jpeg'}), 400
            
    except Exception as e:
        print(f"Error in signature upload: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Upload failed: {str(e)}'}), 500

@app.route('/api/delete-signature', methods=['POST'])
def api_delete_signature():
    """Handle signature deletion"""
    try:
        school_id = get_current_school_id()
        if not school_id:
            return jsonify({'success': False, 'message': 'School authentication required'}), 403
        
        data = request.get_json()
        sig_type = data.get('type')  # head_teacher, form_1, form_2, etc.
        
        valid_types = ['head_teacher', 'form_1', 'form_2', 'form_3', 'form_4']
        if not sig_type or sig_type not in valid_types:
            return jsonify({'success': False, 'message': 'Invalid signature type'}), 400

        # Update database with empty string
        db_field = f"{sig_type}_signature" if sig_type == 'head_teacher' else f"{sig_type}_teacher_signature"
        db.update_school_settings({db_field: ""}, school_id)
        
        return jsonify({
            'success': True, 
            'message': 'Signature removed successfully'
        })
            
    except Exception as e:
        print(f"Error in signature deletion: {e}")
        return jsonify({'success': False, 'message': f'Deletion failed: {str(e)}'}), 500

@app.route('/api/update-settings', methods=['POST'])
@app.route('/api/update-school-settings', methods=['POST'])
def api_update_school_settings():
    """Update school settings"""
    try:
        school_id = get_current_school_id()
        if not school_id:
            return jsonify({'success': False, 'message': 'School authentication required'}), 403
        
        data = request.get_json()
        
        # Remove PTA and SDF fields (no longer applicable) - store empty values to be safe
        data['pta_fund'] = ''
        data['sdf_fund'] = ''
        
        # Update school settings
        db.update_school_settings(data, school_id)
        
        return jsonify({
            'success': True,
            'message': 'School settings updated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating settings: {str(e)}'
        })

@app.route('/api/export-rankings-pdf', methods=['POST'])
def api_export_rankings_pdf():
    """Export rankings as PDF"""
    try:
        school_id = get_current_school_id()
        if not school_id:
            return jsonify({'success': False, 'message': 'School authentication required'}), 403
        
        from reportlab.lib.pagesizes import letter, A4  # type: ignore[import-not-found]
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer  # type: ignore[import-not-found]
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # type: ignore[import-not-found]
        from reportlab.lib import colors  # type: ignore[import-not-found]
        from reportlab.lib.units import inch  # type: ignore[import-not-found]
        import io
        
        data = request.get_json()
        form_level = int(data['form_level'])
        term = data['term']
        academic_year = data['academic_year']
        
        # Get the rankings data which includes the rankings list and counts
        rankings_data = db.get_student_rankings(form_level, term, academic_year, school_id)
        
        if not rankings_data or 'rankings' not in rankings_data or not rankings_data['rankings']:
            return jsonify({'success': False, 'message': 'No rankings data found'}), 404
            
        rankings = rankings_data['rankings']
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Header
        settings = db.get_school_settings(school_id)
        school_name = settings.get('school_name') or 'SECONDARY SCHOOL'
        
        header_style = ParagraphStyle('Header', parent=styles['Normal'], alignment=1, fontSize=14, spaceAfter=10)
        story.append(Paragraph(f"<b>{school_name.upper()}</b>", header_style))
        
        # Title
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], alignment=1, spaceAfter=30)
        story.append(Paragraph(f"Form {form_level} Student Rankings - {term} {academic_year}", title_style))
        story.append(Spacer(1, 12))
        
        # Table data
        if form_level >= 3:
            table_data = [['Position', 'Student Name', 'Aggregate Points', 'Subjects Passed', 'Status']]
            for i, student in enumerate(rankings):
                table_data.append([
                    str(i + 1),
                    student['name'],
                    str(student.get('aggregate_points', 'N/A')),
                    f"{student['subjects_passed']}/{student.get('total_subjects', 12)}",
                    student['status']
                ])
        else:
            table_data = [['Position', 'Student Name', 'Grade', 'Subjects Passed', 'Status']]
            for i, student in enumerate(rankings):
                table_data.append([
                    str(i + 1),
                    student['name'],
                    student.get('grade', 'N/A'),
                    f"{student['subjects_passed']}/{student.get('total_subjects', 12)}",
                    student['status']
                ])
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        doc.build(story)
        
        buffer.seek(0)
        response = make_response(buffer.read())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename="Form_{form_level}_Rankings_{term}_{academic_year}.pdf"'
        return response
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error generating PDF: {str(e)}'}), 500

@app.route('/api/export-top-performers-pdf', methods=['POST'])
def api_export_top_performers_pdf():
    """Export top performers as PDF"""
    try:
        school_id = get_current_school_id()
        if not school_id:
            return jsonify({'success': False, 'message': 'School authentication required'}), 403
        
        from reportlab.lib.pagesizes import letter, A4  # type: ignore[import-not-found]
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer  # type: ignore[import-not-found]
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # type: ignore[import-not-found]
        from reportlab.lib import colors  # type: ignore[import-not-found]
        from reportlab.lib.units import inch  # type: ignore[import-not-found]
        import io
        
        data = request.get_json()
        form_level = int(data['form_level'])
        term = data['term']
        academic_year = data['academic_year']
        category = data['category']
        
        performers = db.get_top_performers_by_category(category, form_level, term, academic_year, school_id)
        
        if not performers:
            return jsonify({'success': False, 'message': 'No top performers data found'}), 404
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Header
        settings = db.get_school_settings(school_id)
        school_name = settings.get('school_name') or 'SECONDARY SCHOOL'
        
        header_style = ParagraphStyle('Header', parent=styles['Normal'], alignment=1, fontSize=14, spaceAfter=10)
        story.append(Paragraph(f"<b>{school_name.upper()}</b>", header_style))
        
        # Title
        category_titles = {
            'overall': 'Best Overall Students',
            'sciences': 'Best in Sciences Department',
            'humanities': 'Best in Humanities Department',
            'languages': 'Best in Languages Department'
        }
        
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], alignment=1, spaceAfter=30)
        story.append(Paragraph(f"{category_titles.get(category, category.title())} - Form {form_level}", title_style))
        story.append(Paragraph(f"{term} {academic_year}", ParagraphStyle('SubTitle', parent=styles['Normal'], alignment=1)))
        story.append(Spacer(1, 12))
        
        # Table data
        table_data = [['Rank', 'Student Name', 'Overall Average', 'Excellence Area']]
        for i, student in enumerate(performers[:10]):
            table_data.append([
                str(i + 1),
                student['name'],
                f"{student['average']}%",
                student.get('excellence_area', category.title())
            ])
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        doc.build(story)
        
        buffer.seek(0)
        response = make_response(buffer.read())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename="Top_Performers_{category}_Form_{form_level}_{term}_{academic_year}.pdf"'
        return response
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error generating PDF: {str(e)}'}), 500

@app.route('/api/get-available-periods', methods=['GET'])
def api_get_available_periods():
    """Get available academic periods with grade data"""
    try:
        school_id = get_current_school_id()
        if not school_id:
            return jsonify({'success': False, 'message': 'School authentication required'}), 403
        
        periods_data = db.get_available_terms_and_years(school_id)
        
        return jsonify({
            'success': True,
            'data': periods_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving periods: {str(e)}'
        }), 500

@app.route('/api/update-selected-period', methods=['POST'])
def api_update_selected_period():
    """Update selected term and academic year in settings when changed in data entry"""
    try:
        school_id = get_current_school_id()
        if not school_id:
            return jsonify({'success': False, 'message': 'School authentication required'}), 403
        
        data = request.get_json()
        term = data.get('term', '')
        academic_year = data.get('academic_year', '')
        
        if not term or not academic_year:
            return jsonify({'success': False, 'message': 'Term and academic year are required'}), 400
        
        # Get current settings
        current_settings = db.get_school_settings(school_id)
        
        # Update only the selected term and academic year
        updated_settings = {
            'school_name': current_settings.get('school_name', ''),
            'school_address': current_settings.get('school_address', ''),
            'school_phone': current_settings.get('school_phone', ''),
            'school_email': current_settings.get('school_email', ''),
            'pta_fund': current_settings.get('pta_fund', ''),
            'sdf_fund': current_settings.get('sdf_fund', ''),
            'boarding_fee': current_settings.get('boarding_fee', ''),
            'next_term_begins': current_settings.get('next_term_begins', ''),
            'boys_uniform': current_settings.get('boys_uniform', ''),
            'girls_uniform': current_settings.get('girls_uniform', ''),
            'selected_term': term,
            'selected_academic_year': academic_year
        }
        
        # Update settings
        db.update_school_settings(updated_settings, school_id)
        
        # Also ensure the academic period exists
        db.update_academic_periods([academic_year], [term], school_id)
        
        return jsonify({
            'success': True,
            'message': f'Updated selected period to {term} {academic_year}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating selected period: {str(e)}'
        }), 500

# DEVELOPER SCHOOL MANAGEMENT ENDPOINTS
@app.route('/api/developer/add-school', methods=['POST'])
def api_developer_add_school():
    """Add new school (Developer only)"""
    # Check authentication first
    if not check_developer_auth():
        return jsonify({'success': False, 'message': 'Unauthorized access. Please login as developer first.'}), 403
    
    try:
        # Validate request content type
        if not request.is_json:
            return jsonify({
                'success': False, 
                'message': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        required_fields = ['school_name', 'username', 'password']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
            
        global db
        if db is None:
            try:
                db = SchoolDatabase()
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'Database initialization failed: {str(e)}'
                }), 500
        
        # Check if username already exists
        existing_schools = db.get_all_schools()
        if any(school['username'] == data['username'] for school in existing_schools):
            return jsonify({
                'success': False,
                'message': 'Username already exists. Please choose a different username.'
            }), 400
        
        school_data = {
            'school_name': data['school_name'].strip(),
            'username': data['username'].strip(),
            'password': data['password']
        }
        
        school_id = db.add_school(school_data)
        
        # Create blank settings for the new school - waiting for admin to edit
        blank_settings = {
            'school_name': '',  # Blank - admin will fill in
            'school_address': '',
            'school_phone': '',
            'school_email': '',
            'pta_fund': '',
            'sdf_fund': '',
            'boarding_fee': '',
            'next_term_begins': '',
            'boys_uniform': '',
            'girls_uniform': ''
        }
        
        db.update_school_settings(blank_settings, school_id)
        
        return jsonify({
            'success': True,
            'message': 'School added successfully with blank settings ready for configuration',
            'school_id': school_id
        })
        
    except Exception as e:
        # Log the full error for debugging
        import traceback
        print(f"Error in add_school endpoint: {e}")
        print(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'message': f'Error adding school: {str(e)}'
        }), 500

@app.route('/api/developer/schools', methods=['GET'])
def api_developer_get_schools():
    """Get all schools (Developer only)"""
    if not check_developer_auth():
        return jsonify({
            'success': False, 
            'message': 'Unauthorized access. Please login as developer first.',
            'redirect': '/login'
        }), 403
    
    try:
        schools = db.get_all_schools()
        return jsonify({
            'success': True,
            'schools': schools
        })
        
    except Exception as e:
        import traceback
        print(f"Error in get_schools endpoint: {e}")
        print(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'message': f'Error retrieving schools: {str(e)}'
        }), 500

@app.route('/api/developer/update-school-status', methods=['POST'])
def api_developer_update_school_status():
    """Update school status (Developer only)"""
    if not check_developer_auth():
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403
    
    try:
        data = request.get_json()
        school_id = int(data['school_id'])
        status = data['status']
        
        db.update_school_status(school_id, status)
        
        return jsonify({
            'success': True,
            'message': f'School status updated to {status}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating school status: {str(e)}'
        })

@app.route('/api/developer/grant-subscription', methods=['POST'])
def api_developer_grant_subscription():
    """Grant subscription to school (Developer only)"""
    if not check_developer_auth():
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403
    
    try:
        data = request.get_json()
        school_id = int(data['school_id'])
        months = int(data.get('months', 12))
        
        db.grant_subscription(school_id, months)
        
        return jsonify({
            'success': True,
            'message': f'Granted {months} months subscription'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error granting subscription: {str(e)}'
        })

@app.route('/api/developer/delete-school', methods=['POST'])
def api_developer_delete_school():
    """Delete school (Developer only)"""
    if not check_developer_auth():
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403
    
    try:
        data = request.get_json()
        school_id = int(data['school_id'])
        
        # Delete school from database
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM schools WHERE school_id = ?", (school_id,))
            
            if cursor.rowcount > 0:
                return jsonify({
                    'success': True,
                    'message': 'School deleted successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'School not found'
                })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error deleting school: {str(e)}'
        })

@app.route('/api/developer/send-reminders', methods=['POST'])
def api_developer_send_reminders():
    """Send subscription reminders (Developer only)"""
    if not check_developer_auth():
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403
    
    try:
        count = db.send_subscription_reminder()
        
        return jsonify({
            'success': True,
            'message': f'Sent reminders to {count} schools'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error sending reminders: {str(e)}'
        })

@app.route('/api/developer/schools-to-lock', methods=['GET'])
def api_developer_schools_to_lock():
    """Get schools that should be locked (Developer only)"""
    if not check_developer_auth():
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403
    
    try:
        schools = db.get_schools_to_lock()
        
        return jsonify({
            'success': True,
            'schools': schools
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving schools to lock: {str(e)}'
        })

@app.route('/api/developer/reset-school-credentials', methods=['POST'])
def api_developer_reset_school_credentials():
    """Reset a school's credentials (Developer only)"""
    if not check_developer_auth():
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403
    try:
        data = request.get_json()
        school_id = int(data.get('school_id'))
        # Generate a secure temporary password
        temp_password = secrets.token_urlsafe(9)[:12]
        db.reset_school_credentials(school_id, temp_password)
        return jsonify({
            'success': True,
            'message': 'School credentials have been reset. The school will be required to change this password on first login.',
            'temporary_password': temp_password
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error resetting credentials: {str(e)}'})

# Add error handler for 404 errors
@app.errorhandler(404)
def not_found_error(error):
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'message': f'API endpoint not found: {request.path}'
        }), 404
    return render_template('404.html'), 404

# Add error handler for 500 errors
@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Server Error: {str(error)}")
    app.logger.error(traceback.format_exc())
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'message': 'Internal server error occurred'
        }), 500
    return render_template('500.html'), 500

if __name__ == "__main__":
    try:
        print("STARTING: School Reporting System...")
        print("=" * 50)
        
        # If the app failed initialization during import, report and pause
        if not getattr(app, 'INIT_OK', True):
            msg = 'Application failed to initialize during import. The server will not start. See the earlier traceback for details.'
            print('\nERROR: ' + msg)
            input('Press Enter to exit...')
            sys.exit(1)

        print("SUCCESS: Flask application loaded successfully!")
        print("INFO: Starting web server...")
        print("INFO: Open your browser and go to: http://localhost:5000")
        print("INFO: Login credentials:")
        print("   Developer: {user} / (hidden - do not expose plaintext)".format(user=DEVELOPER_USERNAME))
        print("=" * 50)
        print("Press Ctrl+C to stop the server\n")
        
        # Start the Flask development server with the same settings as start_app.py
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=False  # Disable reloader to avoid double startup
        )
        
    except ImportError as e:
        print(f"ERROR: Import Error: {e}")
        print("INFO: Make sure all required packages are installed:")
        print("   pip install -r requirements.txt")
        input("Press Enter to exit...")
        sys.exit(1)
        
    except Exception as e:
        print(f"ERROR: Error starting application: {e}")
        print("\nDEBUG: Full error details:")
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)
        
    # If there are command line arguments, use the original argument parser
    # This maintains backward compatibility with any existing scripts
    import argparse
    import subprocess

    parser = argparse.ArgumentParser(description='Run the School Reporting System app (development helper)')
    parser.add_argument('--setup', action='store_true', help='Create .venv and install requirements into it before starting')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind the server to')
    parser.add_argument('--port', default=5000, type=int, help='Port to run the server on')
    parser.add_argument('--debug', action='store_true', help='Run Flask in debug mode')
    args = parser.parse_args()

    def create_virtualenv_and_install():
        venv_dir = os.path.join(os.getcwd(), '.venv')
        pip_path = None
        try:
            if not os.path.isdir(venv_dir):
                print('Creating virtual environment at .venv...')
                subprocess.check_call([sys.executable, '-m', 'venv', venv_dir])
            # Determine pip inside venv
            pip_exe = os.path.join(venv_dir, 'Scripts' if os.name == 'nt' else 'bin', 'pip' + ('.exe' if os.name == 'nt' else ''))
            if os.path.isfile(pip_exe):
                pip_path = pip_exe
                print('Upgrading pip inside the venv...')
                subprocess.check_call([pip_path, 'install', '--upgrade', 'pip'])
                print('Installing requirements into the venv...')
                subprocess.check_call([pip_path, 'install', '-r', 'requirements.txt'])
                print('Requirements installed successfully into .venv')
            else:
                print('Could not find pip in the virtual environment. Activate the venv and run `pip install -r requirements.txt` manually.')
        except subprocess.CalledProcessError as e:
            print(f'Error while creating venv or installing packages: {e}')
            print('You may need to run the setup steps manually. See README or run the original run_web_app.bat on Windows.')

    # Only run setup if explicitly requested. This avoids doing installs in production environments.
    if args.setup:
        create_virtualenv_and_install()
        # After setup we'll instruct the user to activate the venv and re-run without --setup
        print('\nSetup complete. Recommended: activate the virtual environment and run the app again without --setup:')
        if os.name == 'nt':
            # Escape backslashes to avoid invalid escape sequence warnings
            print('  .venv\\Scripts\\activate.bat')
        else:
            print('  source .venv/bin/activate')
        print('Then: python app.py --host {host} --port {port} --debug (as needed)'.format(host=args.host, port=args.port))
        sys.exit(0)

    # Print helpful runtime info, similar to run_web_app.bat/start_app.py
    print('===============================================')
    print(' RN_LAB_TECH Progress Reporting System - Web Version')
    print(' Starting application...')
    print('===============================================')
    print('\nOpen your browser and go to: http://{host}:{port}'.format(host=args.host, port=args.port))
    print('Press Ctrl+C to stop the server')
    print('\nDeveloper credentials:')
    print('   Developer: {user} / (hidden - set DEVELOPER_PASSWORD environment variable)'.format(user=DEVELOPER_USERNAME))

    # Prevent starting the server when initialization failed earlier
    if not INIT_OK:
        # Prefer a message box on Windows when no console is present; otherwise print and pause.
        try:
            show_error_message('Startup Aborted', 'System initialization failed during import. See the log/console for details.')
        except Exception:
            print('\nERROR: System initialization failed. The server will not start.')
            print('See the earlier traceback for details.')
            try:
                input('Press Enter to exit...')
            except Exception:
                pass
        sys.exit(1)

    # Start the Flask development server (safe for local use)
    try:
        app.run(debug=args.debug, host=args.host, port=args.port, use_reloader=False)
    except Exception as e:
        import traceback
        traceback.print_exc()
        try:
            show_error_message('Application Start Failed', f"{str(e)}\nSee the traceback in the console for more details.")
        except Exception:
            print('ERROR: Application failed to start. Check the error messages above.')
            try:
                input('Press Enter to exit...')
            except Exception:
                pass
        sys.exit(1)
