import pytest
from school_database import SchoolDatabase
from scripts.add_science_subjects_migration import run_migration, NEW_SUBJECTS


def test_run_migration_adds_subjects():
    db = SchoolDatabase()

    # Run migration
    run_migration(db)

    # Verify for all schools, the subjects exist for each form level
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT school_id FROM schools")
        school_ids = [row[0] for row in cursor.fetchall()]

    assert len(school_ids) > 0, "No schools found in DB to verify migration"

    for sid in school_ids:
        for form_level in [1, 2, 3, 4]:
            # Direct DB verification per subject/form/school
            with db.get_connection() as conn:
                cursor = conn.cursor()
                for sub in NEW_SUBJECTS:
                    cursor.execute("SELECT COUNT(*) FROM subject_teachers WHERE subject = ? AND form_level = ? AND (school_id = ? OR school_id IS NULL OR school_id = 0)", (sub, form_level, sid))
                    count = cursor.fetchone()[0]
                    assert count > 0, f"{sub} missing for school {sid} form {form_level} (count={count})"


from app import app as flask_app

def test_settings_page_contains_subjects():
    client = flask_app.test_client()

    # Fetch a school id to set in session
    db = SchoolDatabase()
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT school_id FROM schools LIMIT 1")
        row = cursor.fetchone()
    assert row is not None, "No school exists to test settings page"
    school_id = row[0]

    # Simulate login as school (set days_remaining to avoid subscription redirect)
    with client.session_transaction() as session:
        session['user_id'] = school_id
        session['user_type'] = 'school'
        session['days_remaining'] = 365

    rv = client.get('/settings')
    body = rv.get_data(as_text=True)
    for sub in NEW_SUBJECTS:
        assert sub in body, f"{sub} not rendered on settings page"