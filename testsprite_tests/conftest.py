import os
import pytest
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import tempfile

# Patch environment variables before importing app
# We use a test database to avoid messing with production data
TEST_DB_NAME = "school_reports_test"
base_db_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/school_reports')
# Force IPv4 127.0.0.1 to avoid ::1 IPv6 authentication errors
base_db_url = base_db_url.replace('localhost', '127.0.0.1')

if 'school_reports' in base_db_url:
    TEST_DATABASE_URL = base_db_url.replace('school_reports', TEST_DB_NAME)
else:
    TEST_DATABASE_URL = f"{base_db_url.rsplit('/', 1)[0]}/{TEST_DB_NAME}"

os.environ['DATABASE_URL'] = TEST_DATABASE_URL

# Import app components after setting the environment
from app import app as flask_app
from school_database import SchoolDatabase
from multi_user_manager import SchoolUserManager


def setup_test_database():
    """Create a fresh test database for the session."""
    from urllib.parse import urlparse, unquote
    postgres_url = TEST_DATABASE_URL.replace(TEST_DB_NAME, 'postgres')
    
    parsed = urlparse(postgres_url)
    db_kwargs = {
        'dbname': parsed.path.lstrip('/'),
        'user': unquote(parsed.username) if parsed.username else None,
        'password': unquote(parsed.password) if parsed.password else None,
        'host': parsed.hostname,
        'port': parsed.port
    }
    
    try:
        conn = psycopg2.connect(**db_kwargs)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Terminate any existing connections to the test DB
        cur.execute(f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{TEST_DB_NAME}' AND pid <> pg_backend_pid();")
        
        # Drop if exists
        cur.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")
        # Create fresh
        cur.execute(f"CREATE DATABASE {TEST_DB_NAME}")
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"\\n\\n!!! Failed to setup test database: {e} !!!\\n\\n")
        raise e  # Let pytest crash so we can see the exact error output


@pytest.fixture(scope="session", autouse=True)
def setup_teardown_db():
    """Run once for the entire test session."""
    if not setup_test_database():
        pytest.skip(f"Could not connect to PostgreSQL to create {TEST_DB_NAME}. Skipping tests.")
    
    # Initialize schema
    db = SchoolDatabase(db_path=TEST_DATABASE_URL)
    
    yield db
    
    # Optional teardown: we leave it for inspection, or you can drop it.
    pass


@pytest.fixture
def app():
    """Returns the Flask app instance."""
    flask_app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,  # Useful if forms use CSRF
        "SECRET_KEY": "test_secret_key"
    })
    yield flask_app


@pytest.fixture
def client(app):
    """Returns a test client for the Flask app."""
    return app.test_client()


@pytest.fixture
def db():
    """Returns the database instance."""
    return SchoolDatabase(db_path=TEST_DATABASE_URL)


@pytest.fixture
def user_manager(db):
    """Returns the user manager instance."""
    return SchoolUserManager(db)

@pytest.fixture
def auth_client(client, user_manager, db):
    """A test client that is pre-authenticated."""
    # Create a dummy school and user
    with db.get_connection() as conn:
        cursor = conn.cursor()
        # Ensure clean state for school
        cursor.execute("DELETE FROM school_users")
        cursor.execute("DELETE FROM schools")
        
        cursor.execute(
            "INSERT INTO schools (school_name, username, password_hash) VALUES (%s, %s, %s) RETURNING school_id",
            ("Test School", "testschool", "hashed_pass")
        )
        school_id = cursor.fetchone()[0]
        
        cursor.execute(
            "INSERT INTO school_users (school_id, username, password_hash, full_name, role) VALUES (%s, %s, %s, %s, %s) RETURNING user_id",
            (school_id, "admin", "hashed_pass", "Admin User", "Admin")
        )
        user_id = cursor.fetchone()[0]
        conn.commit()

    with client.session_transaction() as sess:
        sess['school_id'] = school_id
        sess['user_id'] = user_id
        sess['school_user_id'] = user_id
        sess['user_type'] = "school_user"
        sess['username'] = "admin"
        sess['role'] = "Admin"
        sess['school_name'] = "Test School"
        sess['assigned_forms'] = [1, 2, 3, 4]
    
    return client
