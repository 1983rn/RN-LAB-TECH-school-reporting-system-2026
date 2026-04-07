#!/usr/bin/env python3
"""Test to ensure students remain visible on the data-entry page
when there are no marks for the selected term/academic year.
"""

from app import app, db


def test_student_visible_when_no_marks_for_selected_period():
    # Create a school (developer API is available in other tests, but use db directly here)
    test_username = 'testschool_vis'
    test_password = 'testpw_vis_123'
    school_data = {
        'school_name': 'Test School Visibility',
        'username': test_username,
        'password': test_password
    }

    school_id = db.add_school(school_data)
    student_id = None

    try:
        # Add a student to form 1 for this school
        student_id = db.add_student({'first_name': 'Visible', 'last_name': 'Student', 'form_level': 1}, school_id)

        # Ensure no marks exist for the default term/academic year for this school
        assert not db.check_marks_exist_for_period(1, 'Term 1', '2025-2026', school_id)

        # Use the Flask test client to login as the school and request the form page
        with app.test_client() as client:
            login_resp = client.post('/api/login', json={
                'username': test_username,
                'password': test_password,
                'user_type': 'school'
            })
            assert login_resp.status_code == 200
            login_data = login_resp.get_json()
            assert login_data.get('success') is True

            # Request the data entry page for Form 1
            resp = client.get('/form/1')
            assert resp.status_code == 200
            body = resp.data.decode('utf-8')

            # The student's name should appear on the page even though there are no marks
            assert 'Visible Student' in body

            # Also ensure the "No Students Enrolled" message is NOT shown
            assert 'New Academic Year - No Students Enrolled Yet' not in body

    finally:
        # Clean up test data
        with db.get_connection() as conn:
            cur = conn.cursor()
            if student_id:
                cur.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
            cur.execute("DELETE FROM schools WHERE school_id = ?", (school_id,))
            conn.commit()