
import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from school_database import SchoolDatabase
    print("Initializing SchoolDatabase...")
    db = SchoolDatabase()
    print("Checking connection...")
    with db.get_connection() as conn:
        print("Successfully connected to PostgreSQL!")
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"PostgreSQL version: {version[0]}")
    print("\nVERIFICATION SUCCESSFUL!")
except Exception as e:
    print(f"\nVERIFICATION FAILED: {e}")
    sys.exit(1)
