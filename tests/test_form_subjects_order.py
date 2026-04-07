import re
from app import app as flask_app
from school_database import SchoolDatabase


def test_form_subjects_includes_new_subjects_and_sorted():
    db = SchoolDatabase()
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT school_id FROM schools LIMIT 1")
        row = cursor.fetchone()
    assert row is not None, "No school exists for testing"
    school_id = row[0]

    client = flask_app.test_client()
    with client.session_transaction() as sess:
        sess['user_id'] = school_id
        sess['user_type'] = 'school'
        sess['days_remaining'] = 365

    rv = client.get('/form/1')
    assert rv.status_code == 200
    body = rv.get_data(as_text=True)

    # Ensure new subjects present
    assert 'Business Studies' in body, 'Business Studies should appear in Data Entry subjects'
    assert 'Home Economics' in body, 'Home Economics should appear in Data Entry subjects'

    # Extract subject headers in order
    headers = re.findall(r'<th[^>]*class="subject-column"[^>]*>\s*([^<]+?)\s*</th>', body)
    assert headers, 'No subject headers found in the Data Entry page'

    # Verify headers are alphabetically sorted (case-insensitive)
    headers_normalized = [h.strip() for h in headers]
    assert headers_normalized == sorted(headers_normalized, key=lambda s: s.lower()), f"Subjects are not sorted alphabetically: {headers_normalized}"


def test_db_backed_subjects_are_included():
    db = SchoolDatabase()
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT school_id FROM schools LIMIT 1")
        row = cursor.fetchone()
    assert row is not None
    school_id = row[0]

    # Insert a school-specific subject that is NOT in defaults
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO subject_teachers (subject, form_level, teacher_name, updated_date, school_id) VALUES (?, ?, ?, datetime('now'), ?)", ('Accounting', 1, 'Acct Teacher', school_id))

    client = flask_app.test_client()
    with client.session_transaction() as sess:
        sess['user_id'] = school_id
        sess['user_type'] = 'school'
        sess['days_remaining'] = 365

    rv = client.get('/form/1')
    assert rv.status_code == 200
    body = rv.get_data(as_text=True)
    assert 'Accounting' in body, 'Accounting (DB-only subject) should appear in Data Entry subjects'
