import tempfile, os
from school_database import SchoolDatabase

def main():
    """Manual smoke script for adding a student in PostgreSQL mode."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        path = f.name

    print('DB:', path)

    db = SchoolDatabase(path)
    student = {'first_name': 'Unit', 'last_name': 'Tester', 'grade_level': 1, 'date_of_birth': '2010-01-01'}
    student_id = db.add_student(student)
    print('Added student id', student_id)
    # save marks without school_id
    for sub, mark in {'Math': 85, 'English': 78}.items():
        db.save_student_mark(student_id, sub, mark, 'Term 1', '2024-2025', 1)
    marks = db.get_student_marks(student_id, 'Term 1', '2024-2025')
    print('Marks retrieved:', marks)
    # cleanup
    import time
    for _ in range(5):
        try:
            os.unlink(path)
            break
        except PermissionError:
            time.sleep(0.1)
    else:
        # If still cannot delete, ignore for CI environment
        pass


if __name__ == "__main__":
    main()
