import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from termly_report_generator import TermlyReportGenerator
    from school_database import SchoolDatabase
    
    db = SchoolDatabase()
    generator = TermlyReportGenerator(db)
    
    # Try to generate a report for student ID 20 (Agnes Zimba, School 2)
    # This will fail at the Table creation if hAlign is the issue
    student_id = 20
    term = "Term 1"
    academic_year = "2025/2026"
    school_id = 2  # Nanjati
    
    print(f"Attempting to generate report for student {student_id}...")
    pdf_bytes = generator.export_progress_report(student_id, term, academic_year, school_id)
    
    if pdf_bytes:
        print(f"Success! Generated {len(pdf_bytes)} bytes.")
    else:
        print("Failed: generator returned None.")
        
except Exception as e:
    import traceback
    print(f"Caught Exception: {str(e)}")
    traceback.print_exc()
