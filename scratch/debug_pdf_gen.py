
import sys
import os
import uuid
# Ensure we can import from parent dir if needed, though we are in project root
sys.path.append(os.getcwd())

from termly_report_generator import TermlyReportGenerator
from school_database import SchoolDatabase
import logging

# Setup logging to console
logging.basicConfig(level=logging.DEBUG)

def debug_pdf_generation(student_id, term='Term 1', academic_year='2025-2026', school_id=2):
    print(f"--- DEBUGGING PDF GENERATION FOR STUDENT {student_id} ---")
    db = SchoolDatabase()
    generator = TermlyReportGenerator(db)
    
    # 1. Check Student
    student = db.get_student_by_id(student_id, 1) # Assuming school_id 1 for debug
    if not student:
        print(f"ERROR: Student {student_id} not found in database.")
        return
        
    print(f"Found student: {student['first_name']} {student['last_name']} (Form {student['grade_level']})")
    print(f"School ID: {student.get('school_id')}")
    
    # 1b. Check School Settings explicitly
    settings = db.get_school_settings(school_id)
    print(f"DEBUG: Retrieved settings for school {school_id}:")
    print(f"  school_name: {repr(settings.get('school_name'))}")
    print(f"  school_address: {repr(settings.get('school_address'))}")
    
    # 2. Check Marks
    marks = db.get_student_marks(student_id, term, academic_year, school_id)
    print(f"Found {len(marks)} marks.")
    
    # 3. Attempt Generation with Verbose Error Catching
    try:
        print("Starting generator.export_report_to_pdf_bytes...")
        pdf_bytes = generator.export_report_to_pdf_bytes(student_id, term, academic_year, school_id)
        
        if not pdf_bytes:
            print("FAILED: generator.export_report_to_pdf_bytes returned b''")
        else:
            print(f"SUCCESS: Generated {len(pdf_bytes)} bytes")
                
    except Exception as e:
        print(f"CRITICAL: Uncaught exception in debug script: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # FATIMA ELIAS from our previous query
    target_id = 22 
    debug_pdf_generation(target_id, term='Term 1', academic_year='2025-2026', school_id=2)
