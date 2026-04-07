from app import app as flask_app
from school_database import SchoolDatabase


def test_best_in_sciences_includes_business_and_home_economics():
    db = SchoolDatabase()
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT school_id FROM schools LIMIT 1")
        row = cursor.fetchone()
    assert row is not None
    school_id = row[0]

    # Create two students and marks where Business Studies and Home Economics tilt the result
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students (first_name, last_name, grade_level, school_id) VALUES (?, ?, ?, ?)", ('SciA', 'One', 1, school_id))
        a_id = cursor.lastrowid
        cursor.execute("INSERT INTO students (first_name, last_name, grade_level, school_id) VALUES (?, ?, ?, ?)", ('SciB', 'Two', 1, school_id))
        b_id = cursor.lastrowid

        term = 'Term 1'
        year = '2025-2026'

        # SciA has higher scores in Business Studies and Home Economics
        marks_a = {
            'Agriculture': 60,
            'Biology': 60,
            'Chemistry': 60,
            'Physics': 60,
            'Mathematics': 60,
            'Business Studies': 95,
            'Home Economics': 95
        }
        # SciB has good regular science scores but low in the two extras
        marks_b = {
            'Agriculture': 80,
            'Biology': 80,
            'Chemistry': 80,
            'Physics': 80,
            'Mathematics': 80,
            'Business Studies': 40,
            'Home Economics': 40
        }

        for subject, mark in marks_a.items():
            cursor.execute("INSERT INTO student_marks (student_id, subject, mark, term, academic_year, school_id) VALUES (?, ?, ?, ?, ?, ?)", (a_id, subject, mark, term, year, school_id))
        for subject, mark in marks_b.items():
            cursor.execute("INSERT INTO student_marks (student_id, subject, mark, term, academic_year, school_id) VALUES (?, ?, ?, ?, ?, ?)", (b_id, subject, mark, term, year, school_id))

    client = flask_app.test_client()
    with client.session_transaction() as sess:
        sess['user_id'] = school_id
        sess['user_type'] = 'school'
        sess['days_remaining'] = 365

    rv = client.get(f'/api/top-performers/1/sciences?term=Term+1&academic_year=2025-2026')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['success']
    performers = data['performers']
    assert performers[0]['name'].startswith('SciA'), f"Expected SciA to top sciences, got {performers[0]['name']}"