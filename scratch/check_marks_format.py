from school_database import SchoolDatabase
import json

db = SchoolDatabase()
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT student_id, term, academic_year, form_level, subject, mark FROM student_marks LIMIT 20")
    rows = cursor.fetchall()
    print("Sample student_marks:")
    for row in rows:
        print(row)
