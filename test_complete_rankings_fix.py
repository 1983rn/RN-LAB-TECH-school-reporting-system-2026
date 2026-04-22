#!/usr/bin/env python3
"""Focused ranking regression test with isolated data."""

from school_database import SchoolDatabase


def test_complete_rankings_fix():
    db = SchoolDatabase()
    school_id = None

    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO schools (school_name, username, password_hash) VALUES (%s, %s, %s) RETURNING school_id",
                ("Rankings Test School", "rankings_test_school", "hash"),
            )
            school_id = cursor.fetchone()[0]
            conn.commit()

        student_id = db.add_student(
            {
                "first_name": "Rank",
                "last_name": "Tester",
                "grade_level": 1,
                "date_of_birth": "2010-01-01",
            },
            school_id,
        )

        db.save_student_mark(student_id, "Mathematics", 84, "Term 1", "2025-2026", 1, school_id)
        db.save_student_mark(student_id, "English", 77, "Term 1", "2025-2026", 1, school_id)

        result_term1 = db.get_student_rankings(1, "Term 1", "2025-2026", school_id)
        result_term2 = db.get_student_rankings(1, "Term 2", "2025-2026", school_id)

        assert isinstance(result_term1.get("rankings"), list)
        assert isinstance(result_term1.get("total_students"), int)
        assert isinstance(result_term1.get("students_with_marks"), int)
        assert result_term1.get("total_students", 0) >= 1
        assert result_term1.get("students_with_marks", 0) >= 1
        assert len(result_term1.get("rankings", [])) >= 1
        assert len(result_term2.get("rankings", [])) == 0
    finally:
        if school_id:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM student_marks WHERE school_id = %s", (school_id,))
                cursor.execute("DELETE FROM students WHERE school_id = %s", (school_id,))
                cursor.execute("DELETE FROM school_settings WHERE school_id = %s", (school_id,))
                cursor.execute("DELETE FROM schools WHERE school_id = %s", (school_id,))
                conn.commit()
