import pytest
from multi_user_manager import SchoolUserManager
from school_database import SchoolDatabase
import hashlib

def test_user_creation(user_manager: SchoolUserManager, db: SchoolDatabase):
    """Test creating a user and verifying they exist."""
    with db.get_connection() as conn:
        conn.cursor().execute("DELETE FROM school_users")
        conn.cursor().execute("DELETE FROM schools")
        conn.cursor().execute(
            "INSERT INTO schools (school_id, school_name, username, password_hash) VALUES (1, 'Test', 'test', 'hash') ON CONFLICT DO NOTHING"
        )
        conn.commit()

    success = user_manager.create_school_user(
        school_id=1,
        username="teacher1",
        password="password123",
        full_name="Teacher One",
        role="Teacher",
        email="teacher1@example.com",
        assigned_forms=[1, 2]
    )

    assert success is True

    # Verify user in database
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, role, password_hash FROM school_users WHERE username = %s AND school_id = %s", ("teacher1", 1))
        user = cursor.fetchone()
    
    assert user is not None
    assert user[0] == "teacher1"
    assert user[1] == "Teacher"
    assert user[2] == hashlib.sha256("password123".encode()).hexdigest()

def test_user_authentication(user_manager: SchoolUserManager, db: SchoolDatabase):
    """Test user login."""
    # Authenticate with valid credentials
    user = user_manager.authenticate_school_user("teacher1", "password123", school_id=1)
    assert user is not None
    assert user['username'] == "teacher1"
    assert user['role'] == "Teacher"

    # Authenticate with invalid password
    user = user_manager.authenticate_school_user("teacher1", "wrongpassword", school_id=1)
    assert user is None

    # Authenticate with non-existent user
    user = user_manager.authenticate_school_user("ghost", "password123", school_id=1)
    assert user is None

def test_login_route(client):
    """Test the login endpoint."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

    # Assuming there's a post route for login
    # We won't test full form post here without CSRF token handling, 
    # but we can verify the protected route redirects to login
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.headers.get('Location', '')
