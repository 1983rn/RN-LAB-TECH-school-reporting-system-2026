#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from school_database import SchoolDatabase

def check_db_path():
    """Check what database path is being used"""
    db = SchoolDatabase()
    print(f"Database path being used: {db.db_path}")
    print(f"File exists: {os.path.exists(db.db_path)}")
    if os.path.exists(db.db_path):
        print(f"File size: {os.path.getsize(db.db_path)} bytes")
    
    # Try direct connection to check students
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM students")
    student_count = cursor.fetchone()[0]
    print(f"Students found via direct connection: {student_count}")
    conn.close()

if __name__ == "__main__":
    check_db_path()
