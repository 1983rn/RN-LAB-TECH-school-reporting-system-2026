import pytest
import os
from termly_report_generator import TermlyReportGenerator
from school_database import SchoolDatabase

def test_pdf_report_generation(db: SchoolDatabase, tmp_path):
    """Test generating a simple PDF report."""
    # Ensure clean state
    with db.get_connection() as conn:
        conn.cursor().execute("DELETE FROM students")
        conn.cursor().execute("DELETE FROM student_marks")
        conn.cursor().execute("DELETE FROM student_term_enrollment")
        conn.commit()

    student_data = {"first_name": "Alice", "last_name": "PDF", "grade_level": 3}
    student_id = db.add_student(student_data, school_id=1)

    db.enroll_student_in_term(student_id, "Term 1", "2025-2026", 3, school_id=1)

    marks_data = {"Math": 85, "Science": 75}
    rows = [{
        "first_name": "Alice",
        "last_name": "PDF",
        "is_duplicate": True,
        "existing_student_id": student_id,
        "marks": marks_data
    }]
    
    db.bulk_upload_students_data(rows, "Term 1", "2025-2026", 3, school_id=1, duplicate_action="skip")

    # Use the generator
    generator = TermlyReportGenerator(school_name="Test School")
    # This relies on the database singleton/environment being patched, which conftest handles
    # but generator initializes its own db. Since we patched os.environ['DATABASE_URL'] in conftest, 
    # it should use the test database!
    
    pdf_bytes = generator.export_report_to_pdf_bytes(
        student_id=student_id,
        term="Term 1",
        academic_year="2025-2026",
        school_id=1
    )
    
    output_path = tmp_path / "test_report.pdf"
    
    # Save bytes to temp file to verify
    if pdf_bytes:
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
            
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0
