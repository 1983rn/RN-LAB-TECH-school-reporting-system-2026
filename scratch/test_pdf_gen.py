
import os
import sys

# Add the project directory to sys.path
sys.path.append(os.getcwd())

from school_database import SchoolDatabase
from termly_report_generator import TermlyReportGenerator

def test_pdf_gen():
    db = SchoolDatabase()
    generator = TermlyReportGenerator(db)
    
    # Try to find a student with marks
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT student_id, term, academic_year, form_level, school_id FROM student_marks LIMIT 1")
        row = cursor.fetchone()
        
    if not row:
        print("No marks found in database to test with.")
        return
        
    s_id, term, year, form, school_id = row
    print(f"Testing with Student ID: {s_id}, Term: {term}, Year: {year}, School: {school_id}")
    
    pdf_bytes = generator.export_multiple_reports_to_pdf_bytes([s_id], term, year, school_id)
    
    if pdf_bytes:
        print(f"Success! Generated {len(pdf_bytes)} bytes.")
    else:
        print("Failed to generate PDF.")

if __name__ == "__main__":
    test_pdf_gen()
