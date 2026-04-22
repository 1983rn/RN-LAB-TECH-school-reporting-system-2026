#!/usr/bin/env python3

from school_database import SchoolDatabase


def test_correct_position():
    """Test position calculation with correct term/year"""
    db = SchoolDatabase()
    school_id = None

    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO schools (school_name, username, password_hash) VALUES (%s, %s, %s) RETURNING school_id",
                ("Position Test School", "position_test_school", "hash"),
            )
            school_id = cursor.fetchone()[0]
            conn.commit()

        term = "Term 3"
        academic_year = "2025-2026"
        form_level = 1

        student_id = db.add_student(
            {
                "first_name": "Position",
                "last_name": "Tester",
                "grade_level": form_level,
                "date_of_birth": "2010-01-01",
            },
            school_id,
        )

        db.save_student_mark(student_id, "English", 75, term, academic_year, form_level, school_id)
        db.save_student_mark(student_id, "Mathematics", 83, term, academic_year, form_level, school_id)
        db.save_student_mark(student_id, "Biology", 79, term, academic_year, form_level, school_id)

        students = db.get_students_by_grade(form_level, school_id)
        assert any(s["student_id"] == student_id for s in students)

        position_data = db.get_student_position_and_points(student_id, term, academic_year, form_level, school_id)
        assert "position" in position_data
        assert "total_students" in position_data
        assert position_data["total_students"] >= 1

        for subject in ["English", "Mathematics", "Biology"]:
            subject_pos = db.get_subject_position(student_id, subject, term, academic_year, form_level, school_id)
            assert isinstance(subject_pos, str)
            assert "/" in subject_pos
    finally:
        if school_id:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM student_marks WHERE school_id = %s", (school_id,))
                cursor.execute("DELETE FROM students WHERE school_id = %s", (school_id,))
                cursor.execute("DELETE FROM school_settings WHERE school_id = %s", (school_id,))
                cursor.execute("DELETE FROM schools WHERE school_id = %s", (school_id,))
                conn.commit()
