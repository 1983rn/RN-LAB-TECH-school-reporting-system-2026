from app import app as flask_app
from school_database import SchoolDatabase


def test_update_and_delete_subject_teacher_api():
    db = SchoolDatabase()
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT school_id FROM schools LIMIT 1")
        row = cursor.fetchone()
    assert row is not None, "No school exists for testing"
    school_id = row[0]

    client = flask_app.test_client()

    # Set session to school
    with client.session_transaction() as session:
        session['user_id'] = school_id
        session['user_type'] = 'school'
        session['days_remaining'] = 365

    # Update subject teacher
    payload = {
        'subject': 'Business Studies',
        'form_level': 1,
        'teacher_name': 'Test Teacher BS'
    }
    rv = client.post('/api/update-subject-teacher', json=payload)
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['success'] is True

    # Verify in DB
    teachers = db.get_subject_teachers(form_level=1, school_id=school_id)
    assert 'Business Studies' in teachers
    assert teachers['Business Studies'] == 'Test Teacher BS'

    # Delete the assignment
    rv2 = client.post('/api/delete-subject-teacher', json={'subject': 'Business Studies', 'form_level': 1})
    assert rv2.status_code == 200
    d2 = rv2.get_json()
    assert d2['success'] is True

    # Verify deletion
    teachers_after = db.get_subject_teachers(form_level=1, school_id=school_id)
    assert 'Business Studies' not in teachers_after
