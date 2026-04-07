#!/usr/bin/env python3
"""
Migrate database to support multi-school data isolation
"""

import sqlite3
from datetime import datetime

def migrate_database():
    try:
        conn = sqlite3.connect('school_reports.db')
        cursor = conn.cursor()
        
        print("Starting multi-school migration...")
        
        # 1. Add school_id column to students table
        try:
            cursor.execute("ALTER TABLE students ADD COLUMN school_id INTEGER")
            print("+ Added school_id column to students table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("+ school_id column already exists in students table")
            else:
                raise
        
        # 2. Add school_id column to student_marks table
        try:
            cursor.execute("ALTER TABLE student_marks ADD COLUMN school_id INTEGER")
            print("+ Added school_id column to student_marks table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("+ school_id column already exists in student_marks table")
            else:
                raise
        
        # 3. Add school_id column to subject_teachers table
        try:
            cursor.execute("ALTER TABLE subject_teachers ADD COLUMN school_id INTEGER")
            print("+ Added school_id column to subject_teachers table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("+ school_id column already exists in subject_teachers table")
            else:
                raise
        
        # 4. Add school_id column to school_settings table
        try:
            cursor.execute("ALTER TABLE school_settings ADD COLUMN school_id INTEGER")
            print("+ Added school_id column to school_settings table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("+ school_id column already exists in school_settings table")
            else:
                raise
        
        # 5. Create a default school if none exists
        cursor.execute("SELECT COUNT(*) FROM schools")
        school_count = cursor.fetchone()[0]
        
        if school_count == 0:
            # Create default school
            import hashlib
            password_hash = hashlib.sha256("demo123".encode()).hexdigest()
            cursor.execute("""
                INSERT INTO schools (school_name, username, password_hash, status, subscription_status, days_remaining)
                VALUES (?, ?, ?, 'active', 'trial', 90)
            """, ("DEMO SECONDARY SCHOOL", "demo", password_hash))
            default_school_id = cursor.lastrowid
            print(f"+ Created default school (ID: {default_school_id})")
        else:
            # Get the first school as default
            cursor.execute("SELECT school_id FROM schools LIMIT 1")
            default_school_id = cursor.fetchone()[0]
            print(f"+ Using existing school as default (ID: {default_school_id})")
        
        # 6. Update existing records to belong to default school
        cursor.execute("UPDATE students SET school_id = ? WHERE school_id IS NULL", (default_school_id,))
        updated_students = cursor.rowcount
        print(f"+ Updated {updated_students} students to belong to default school")
        
        cursor.execute("UPDATE student_marks SET school_id = ? WHERE school_id IS NULL", (default_school_id,))
        updated_marks = cursor.rowcount
        print(f"+ Updated {updated_marks} student marks to belong to default school")
        
        cursor.execute("UPDATE subject_teachers SET school_id = ? WHERE school_id IS NULL", (default_school_id,))
        updated_teachers = cursor.rowcount
        print(f"+ Updated {updated_teachers} subject teacher records to belong to default school")
        
        cursor.execute("UPDATE school_settings SET school_id = ? WHERE school_id IS NULL", (default_school_id,))
        updated_settings = cursor.rowcount
        print(f"+ Updated {updated_settings} school settings to belong to default school")
        
        conn.commit()
        conn.close()
        
        print("\n[SUCCESS] Multi-school migration completed successfully!")
        print(f"Default school ID: {default_school_id}")
        print("Each school now has isolated data.")
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        if conn:
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    migrate_database()
