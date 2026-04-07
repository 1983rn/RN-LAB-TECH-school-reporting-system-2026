#!/usr/bin/env python3
"""
Malawi School Reporting System - Web Application
Flask-based web interface for school report generation

Created by: RN_LAB_TECH
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for, session, make_response
from typing import Dict, Any
import os
import sys
from datetime import datetime
import json
import hashlib
import zipfile
import io

# Add current directory to path 
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from termly_report_generator import TermlyReportGenerator
    from performance_analyzer import PerformanceAnalyzer
    from school_database import SchoolDatabase
except ImportError as e:
    print(f"Import error: {e}")
    print("Creating minimal versions...")

import logging

app = Flask(__name__)
# Support configuring SECRET_KEY from environment for production safety
app.secret_key = os.environ.get('SECRET_KEY', 'malawi_school_reporting_system_2025')
if app.secret_key == 'malawi_school_reporting_system_2025':
    logging.warning('Using default SECRET_KEY; set SECRET_KEY env var for production')

# Optionally configure SERVER_NAME to allow url_for outside requests
server_name = os.environ.get('SERVER_NAME')
if server_name:
    app.config['SERVER_NAME'] = server_name
    logging.info('Configured SERVER_NAME from environment: %s', server_name)

# Developer credentials
DEVELOPER_USERNAME = 'MAKONOKAya'
DEVELOPER_PASSWORD = 'NAMADEYIMKOLOWEKO1949'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_auth():
    return 'user_id' in session and 'user_type' in session

def check_developer_auth():
    return session.get('user_type') == 'developer'

def check_subscription_status():
    """Check if school subscription is valid"""
    if session.get('user_type') == 'school':
        days_remaining = session.get('days_remaining', 0)
        if days_remaining <= 0:
            return False
    return True

@app.before_request
def before_request():
    """Check subscription status before each request"""
    # Skip subscription check for login, logout, and developer routes
    exempt_routes = ['login', 'api_login', 'logout', 'developer_dashboard']
    exempt_prefixes = ['/api/developer/', '/static/']
    
    if request.endpoint in exempt_routes:
        return
    
    for prefix in exempt_prefixes:
        if request.path.startswith(prefix):
            return
    
    # Check if user is logged in
    if not check_auth():
        return redirect(url_for('login'))
    
    # Check subscription status for schools
    if session.get('user_type') == 'school' and not check_subscription_status():
        session.clear()
        flash('Your subscription has expired. Please contact the administrator to renew.', 'error')
        return redirect(url_for('login'))

# Initialize system components
try:
    db = SchoolDatabase()
    generator = TermlyReportGenerator(
        school_name="DEMO SECONDARY SCHOOL",
        school_address="P.O. Box 123, Lilongwe, Malawi",
        school_phone="+265 1 234 5678",
        school_email="demo@school.edu.mw"
    )
    analyzer = PerformanceAnalyzer("DEMO SECONDARY SCHOOL")
except Exception as e:
    print(f"Error initializing components: {e}")
    db = None
    generator = None
    analyzer = None

@app.route('/')
def index():
    """Main dashboard with form selection"""
    if not check_auth():
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login')
def login():
    """Login page"""
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    """Handle login authentication"""
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        user_type = data['user_type']
        
        if user_type == 'developer':
            if username == DEVELOPER_USERNAME and password == DEVELOPER_PASSWORD:
                session['user_id'] = 'developer'
                session['user_type'] = 'developer'
                session['username'] = username
                return jsonify({'success': True, 'redirect': '/developer-dashboard'})
        elif user_type == 'school':
            # Check school credentials
            if db:
                school = db.authenticate_school(username, password)
                if school:
                    session['user_id'] = school['school_id']
                    session['user_type'] = 'school'
                    session['username'] = username
                    session['school_name'] = school['school_name']
                    session['subscription_status'] = school['subscription_status']
                    session['days_remaining'] = school['days_remaining']
                    
                    # Check if subscription is expired
                    if school['days_remaining'] <= 0:
                        return jsonify({
                            'success': False, 
                            'message': 'Your subscription has expired. Please contact the administrator to renew your subscription.'
                        })
                    
                    return jsonify({'success': True, 'redirect': '/'})
        
        return jsonify({'success': False, 'message': 'Invalid credentials'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

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

@app.route('/form/<int:form_level>')
def form_data_entry(form_level):
    """Data entry page for specific form"""
    if form_level not in [1, 2, 3, 4]:
        return redirect(url_for('index'))
    
    subjects = ['Agriculture', 'Bible Knowledge', 'Biology', 'Chemistry', 
               'Chichewa', 'Computer Studies', 'English', 'Geography', 
               'History', 'Life Skills/SOS', 'Mathematics', 'Physics', 'Business Studies', 'Home Economics']
    
    # Get students for this form
    students = []
    if db:
        try:
            students = db.get_students_by_grade(form_level)
        except Exception as e:
            print(f"Error getting students: {e}")
    
    # Get terms and academic years from settings or define defaults
    settings = {}
    if db and hasattr(db, 'get_school_settings'):
        try:
            settings = db.get_school_settings()
        except:
            pass
    
    terms = settings.get('terms', ['Term 1', 'Term 2', 'Term 3'])
    academic_years = settings.get('academic_years', [f'{y}-{y+1}' for y in range(2020, 2031)])
    
    return render_template('form_data_entry.html', 
                         form_level=form_level, 
                         subjects=subjects, 
                         students=students,
                         terms=terms,
                         academic_years=academic_years)

@app.route('/report-generator')
def report_generator():
    """Report card generator page"""
    return render_template('report_generator.html')

@app.route('/ranking-analysis')
def ranking_analysis():
    """Ranking and analysis page"""
    return render_template('ranking_analysis.html')

@app.route('/settings')
def settings():
    """Settings page"""
    # Get current settings for terms and academic years
    settings_obj = {}
    if db and hasattr(db, 'get_school_settings'):
        try:
            settings_obj = db.get_school_settings()
        except:
            pass
    
    terms = settings_obj.get('terms', ['Term 1', 'Term 2', 'Term 3'])
    academic_years = settings_obj.get('academic_years', [f'{y}-{y+1}' for y in range(2020, 2031)])
    return render_template('settings.html', terms=terms, academic_years=academic_years, settings=settings_obj)

@app.route('/api/save-student-marks', methods=['POST'])
def api_save_student_marks():
    """Save student marks from data entry"""
    try:
        if not db:
            return jsonify({'success': False, 'message': 'Database not available'})
            
        data = request.get_json()
        student_id = data['student_id']
        form_level = data['form_level']
        term = data['term']
        academic_year = data['academic_year']
        marks = data['marks']  # Dictionary of subject: mark
        
        # Save marks to database
        for subject, mark in marks.items():
            # Normalize and validate mark safely: handle None and invalid values
            mark_str = '' if mark is None else str(mark).strip()
            if mark_str != '':
                try:
                    mark_value = int(mark_str)
                except (ValueError, TypeError):
                    # Skip invalid/non-integer marks
                    continue
                db.save_student_mark(student_id, subject, mark_value, term, academic_year, form_level)
        
        return jsonify({
            'success': True,
            'message': 'Marks saved successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error saving marks: {str(e)}'
        })

@app.route('/api/load-student-marks', methods=['GET'])
def api_load_student_marks():
    """Load existing marks for a student"""
    try:
        if not db:
            return jsonify({'success': False, 'message': 'Database not available'})
            
        student_id_str = request.args.get('student_id')
        if not student_id_str:
            return jsonify({'success': False, 'message': 'Missing student_id parameter'}), 400
        try:
            student_id = int(student_id_str)
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Invalid student_id parameter'}), 400
        # request.args.get may return None; supply sensible defaults to satisfy typing and DB API
        term = request.args.get('term') or 'Term 1'
        academic_year = request.args.get('academic_year') or '2024-2025'
        
        # Ensure we have a dict back from the DB call (avoid None)
        marks: Dict[str, Any] = db.get_student_marks(student_id, term, academic_year) or {}

        # Convert to format expected by frontend
        marks_data = {}
        for subject, data in marks.items():
            # data may be None or a dict; handle defensively
            if isinstance(data, dict):
                marks_data[subject] = data.get('mark')
            else:
                marks_data[subject] = None
        
        return jsonify({
            'success': True,
            'marks': marks_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error loading marks: {str(e)}'
        })

@app.route('/api/generate-report-card', methods=['POST'])
def api_generate_report_card():
    """Generate report card for a student"""
    try:
        if not generator:
            return jsonify({'success': False, 'message': 'Report generator not available'})
            
        data = request.get_json()
        student_id = int(data['student_id'])
        term = data['term']
        academic_year = data['academic_year']
        
        report = generator.generate_progress_report(student_id, term, academic_year)
        
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

@app.route('/api/export-report-card', methods=['POST'])
def api_export_report_card():
    """Export report card as PDF"""
    try:
        if not generator or not db:
            return jsonify({'success': False, 'message': 'Services not available'}), 500
            
        data = request.get_json()
        student_id = int(data['student_id'])
        term = data['term']
        academic_year = data['academic_year']
        
        pdf_bytes = generator.export_report_to_pdf_bytes(student_id, term, academic_year)
        
        if pdf_bytes:
            student = db.get_student_by_id(student_id)
            # Guard against missing student record to avoid subscript errors
            if student and isinstance(student, dict):
                first = student.get('first_name', 'Student')
                last = student.get('last_name', str(student_id))
                filename = f"{first}_{last}_Report_{term.replace(' ','_')}_{academic_year.replace('-','_')}.pdf"
            else:
                filename = f"Student_{student_id}_Report_{term.replace(' ','_')}_{academic_year.replace('-','_')}.pdf"
            
            response = make_response(pdf_bytes)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to generate PDF report'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error exporting report: {str(e)}'
        }), 500

@app.route('/api/print-all-reports')
def api_print_all_reports():
    """Generate and download all report cards for a form as ZIP"""
    try:
        if not generator or not db:
            return jsonify({'success': False, 'message': 'Services not available'}), 500
            
        form_level = int(request.args.get('form_level', 1))
        term = request.args.get('term', 'Term 1')
        academic_year = request.args.get('academic_year', '2024-2025')
        
        students = db.get_students_by_grade(form_level)
        if not students:
            return jsonify({
                'success': False,
                'message': f'No students found for Form {form_level}'
            }), 404
        
        mem_zip = io.BytesIO()
        with zipfile.ZipFile(mem_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            for student in students:
                try:
                    pdf_bytes = generator.export_report_to_pdf_bytes(student['student_id'], term, academic_year)
                    if pdf_bytes:
                        filename = f"{student['first_name']}_{student['last_name']}_Report_{term.replace(' ','_')}_{academic_year.replace('-','_')}.pdf"
                        zf.writestr(filename, pdf_bytes)
                except Exception as e:
                    print(f"Error generating PDF for {student['first_name']} {student['last_name']}: {e}")
                    continue
        
        mem_zip.seek(0)
        response = make_response(mem_zip.read())
        response.headers['Content-Type'] = 'application/zip'
        response.headers['Content-Disposition'] = f'attachment; filename="Form_{form_level}_Reports_{term.replace(" ","_")}_{academic_year.replace("-","_")}.zip"'
        return response
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error generating reports: {str(e)}'}), 500

if __name__ == '__main__':
    print("Starting Malawi School Reporting System...")
    print("Access the application at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)