from app import app as flask_app
from school_database import SchoolDatabase


def test_ranking_page_has_academic_year_and_term_selects():
    db = SchoolDatabase()
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT school_id FROM schools LIMIT 1")
        row = cursor.fetchone()
    assert row is not None
    school_id = row[0]

    client = flask_app.test_client()
    with client.session_transaction() as sess:
        sess['user_id'] = school_id
        sess['user_type'] = 'school'
        sess['days_remaining'] = 365

    rv = client.get('/ranking-analysis')
    assert rv.status_code == 200
    body = rv.get_data(as_text=True)

    # Check that termSelect contains at least one term option
    assert 'id="termSelect"' in body
    assert '<option' in body

    # Check academicYear select contains at least one year option (e.g., 2025-2026)
    assert 'id="academicYear"' in body
    assert '2025-2026' in body, 'Expected 2025-2026 to appear in Academic Year select'