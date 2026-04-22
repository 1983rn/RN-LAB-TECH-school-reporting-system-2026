#!/usr/bin/env python3
"""
Test the delete student functionality
"""

from school_database import SchoolDatabase


def test_delete_function():
    db = SchoolDatabase()
    school_id = None

    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO schools (school_name, username, password_hash) VALUES (%s, %s, %s) RETURNING school_id",
                ("Delete Test School", "delete_test_school", "hash"),
            )
            school_id = cursor.fetchone()[0]
            conn.commit()

        student_id = db.add_student(
            {
                "first_name": "Delete",
                "last_name": "Tester",
                "grade_level": 1,
                "date_of_birth": "2010-01-01",
            },
            school_id,
        )
        db.save_student_mark(student_id, "Mathematics", 80, "Term 1", "2025-2026", 1, school_id)

        assert db.delete_student(student_id, school_id) is True
        students = db.get_students_by_grade(1, school_id)
        assert all(s["student_id"] != student_id for s in students)
        marks = db.get_student_marks(student_id, "Term 1", "2025-2026", school_id)
        assert marks == {}
    finally:
        if school_id:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM student_marks WHERE school_id = %s", (school_id,))
                cursor.execute("DELETE FROM students WHERE school_id = %s", (school_id,))
                cursor.execute("DELETE FROM school_settings WHERE school_id = %s", (school_id,))
                cursor.execute("DELETE FROM schools WHERE school_id = %s", (school_id,))
                conn.commit()