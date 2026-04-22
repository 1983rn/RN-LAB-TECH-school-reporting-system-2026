import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from school_database import SchoolDatabase

db = SchoolDatabase()
school_id = 1 # Assuming school_id 1
# Get a student
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT student_id, school_id FROM students LIMIT 1")
    res = cursor.fetchone()
    if res:
        student_id, school_id = res
        print(f"Testing with student_id={student_id}, school_id={school_id}")
        
        # Get existing marks
        marks_before = db.get_student_marks(student_id, 'Term 1', '2024-2025', school_id)
        print("Marks before:", marks_before)
        
        # Update mark
        db.save_student_mark(student_id, 'Mathematics', 99, 'Term 1', '2024-2025', 1, school_id)
        
        # Get marks after
        marks_after = db.get_student_marks(student_id, 'Term 1', '2024-2025', school_id)
        print("Marks after:", marks_after)
        
        # Verify directly from DB
        cursor.execute("SELECT subject, mark, term, academic_year, school_id FROM student_marks WHERE student_id=?", (student_id,))
        print("Direct DB query after:", cursor.fetchall())
    else:
        print("No students found.")
