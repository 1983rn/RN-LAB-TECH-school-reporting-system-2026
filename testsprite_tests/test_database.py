import pytest
from school_database import SchoolDatabase

def test_database_initialization(db: SchoolDatabase):
    """Test that the database initializes properly and is Postgres."""
    assert db.use_postgres is True
    assert 'school_reports_test' in db.db_path

def test_student_crud(db: SchoolDatabase):
    """Test Create, Read, Update for a student."""
    # Ensure clean state
    with db.get_connection() as conn:
        conn.cursor().execute("DELETE FROM students")
        conn.cursor().execute("DELETE FROM schools")
        conn.cursor().execute(
            "INSERT INTO schools (school_id, school_name, username, password_hash) VALUES (1, 'Test', 'test', 'hash') ON CONFLICT DO NOTHING"
        )
        conn.commit()

    student_data = {
        "first_name": "John",
        "last_name": "Doe",
        "grade_level": 1,
        "date_of_birth": "2010-01-01"
    }

    # Add student
    student_id = db.add_student(student_data, school_id=1)
    assert student_id is not None
    assert isinstance(student_id, int)

    # Read student
    fetched_student = db.get_student_by_id(student_id, school_id=1)
    assert fetched_student is not None
    assert fetched_student['first_name'] == "John"
    assert fetched_student['last_name'] == "Doe"

    # Update student
    update_data = {"first_name": "Johnny"}
    success = db.update_student(student_id, update_data, school_id=1)
    assert success is True

    # Verify update
    fetched_student = db.get_student_by_id(student_id, school_id=1)
    assert fetched_student['first_name'] == "Johnny"

def test_marks_insertion(db: SchoolDatabase):
    """Test adding marks for a student."""
    with db.get_connection() as conn:
        conn.cursor().execute("DELETE FROM student_marks")
        conn.cursor().execute("DELETE FROM students")
        conn.cursor().execute("DELETE FROM student_term_enrollment")
        conn.commit()

    student_data = {"first_name": "Jane", "last_name": "Smith", "grade_level": 2}
    student_id = db.add_student(student_data, school_id=1)

    db.enroll_student_in_term(student_id, "Term 1", "2025-2026", 2, school_id=1)

    marks_data = {
        "Math": 85,
        "English": 90
    }
    
    # We use bulk upload for adding marks
    rows_to_process = [{
        "first_name": "Jane",
        "last_name": "Smith",
        "is_duplicate": True,
        "existing_student_id": student_id,
        "marks": marks_data
    }]

    result = db.bulk_upload_students_data(
        rows_to_process, 
        term="Term 1", 
        academic_year="2025-2026", 
        form_level=2, 
        school_id=1, 
        duplicate_action="skip"
    )

    assert result['success'] is True
    assert result['mark_count'] == 2

    # Verify marks are saved
    marks_exist = db.check_marks_exist_for_period(2, "Term 1", "2025-2026", school_id=1)
    assert marks_exist is True
