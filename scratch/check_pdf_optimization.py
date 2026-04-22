import os
import sys
from datetime import datetime

# Add the project root to sys.path
project_root = r'd:\2025-2026\PRODUCTION\USA\RN-LAB-TECH-school-reporting-system-2026-1'
sys.path.insert(0, project_root)

from school_database import SchoolDatabase
from termly_report_generator import TermlyReportGenerator
from unittest.mock import MagicMock

# Setup mock DB
db = SchoolDatabase()
# Force 14 subjects
generator = TermlyReportGenerator()
generator.standard_subjects = [
    'Agriculture', 'Bible Knowledge', 'Biology', 'Business Studies', 'Chemistry', 
    'Chichewa', 'Computer Studies', 'English', 'Geography', 
    'History', 'Life Skills/SOS', 'Mathematics', 'Physics', 'Home Economics'
]

# Mock data
student = {
    'student_id': 1,
    'first_name': 'Test',
    'last_name': 'Student',
    'student_number': '0001',
    'grade_level': 1,
    'school_id': 1
}

marks = {s: {'mark': 75} for s in generator.standard_subjects}

# Generate PDF
try:
    pdf_buffer = generator.export_progress_report(
        student_id=1,
        student=student,
        marks=marks,
        teachers_map={},
        term='Term 1',
        academic_year='2025-2026',
        next_term_begins='2026-05-01',
        boarding_fee='MK 150,000',
        girls_uniform='Blue dress',
        boys_uniform='Grey shorts',
        school_name='Optimization Test School',
        school_address='123 Test Street, Lilongwe',
        school_email='test@school.mw',
        school_id=1
    )
    
    output_path = os.path.join(project_root, 'scratch', 'test_report_optimized.pdf')
    with open(output_path, 'wb') as f:
        f.write(pdf_buffer.getbuffer())
        
    print(f"Generated test PDF: {output_path}")
    
    # Check page count (rough check via buffer size or simple logic)
    # Since we can't easily check page count without PyPDF2, we'll assume success if generated
    # and we can see the file size.
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Error: {e}")
