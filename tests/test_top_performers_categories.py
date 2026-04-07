from app import app as flask_app
from school_database import SchoolDatabase


def test_sciences_top_performer_by_total_marks():
    db = SchoolDatabase()
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT school_id FROM schools LIMIT 1")
        row = cursor.fetchone()
    assert row is not None
    school_id = row[0]

    # Create two students in Form 1 and insert marks such that student A has higher total in sciences
    with db.get_connection() as conn:
        cursor = conn.cursor()
        # Create students
        cursor.execute("INSERT INTO students (first_name, last_name, grade_level, school_id) VALUES (?, ?, ?, ?)", ('Alpha', 'One', 1, school_id))
        alpha_id = cursor.lastrowid
        cursor.execute("INSERT INTO students (first_name, last_name, grade_level, school_id) VALUES (?, ?, ?, ?)", ('Beta', 'Two', 1, school_id))
        beta_id = cursor.lastrowid

        # Term and year
        term = 'Term 1'
        year = '2025-2026'

        # Alpha: strong in sciences
        science_marks_alpha = {
            'Agriculture': 85,
            'Biology': 88,
            'Chemistry': 90,
            'Physics': 92,
            'Mathematics': 80
        }

        # Beta: weaker in sciences
        science_marks_beta = {
            'Agriculture': 70,
            'Biology': 72,
            'Chemistry': 68,
            'Physics': 75,
            'Mathematics': 78
        }

        for subject, mark in science_marks_alpha.items():
            cursor.execute("INSERT INTO student_marks (student_id, subject, mark, term, academic_year, school_id) VALUES (?, ?, ?, ?, ?, ?)", (alpha_id, subject, mark, term, year, school_id))
        for subject, mark in science_marks_beta.items():
            cursor.execute("INSERT INTO student_marks (student_id, subject, mark, term, academic_year, school_id) VALUES (?, ?, ?, ?, ?, ?)", (beta_id, subject, mark, term, year, school_id))

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
    assert len(performers) >= 1
    # Top performer should be Alpha One because total science marks are higher
    assert performers[0]['name'].startswith('Alpha'), f"Expected Alpha to top sciences, got {performers[0]['name']}"