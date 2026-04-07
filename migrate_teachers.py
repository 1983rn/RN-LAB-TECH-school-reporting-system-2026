#!/usr/bin/env python3
"""
Database migration script to update subject_teachers table for form-specific teachers
"""

import sqlite3
import os

def migrate_database():
    db_path = "school_reports.db"
    
    if not os.path.exists(db_path):
        print("Database not found. Run the main application first.")
        return
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Check if migration is needed
            cursor.execute("PRAGMA table_info(subject_teachers)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'form_level' not in columns:
                print("Migrating subject_teachers table...")
                
                # Create new table
                cursor.execute("""
                    CREATE TABLE subject_teachers_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        subject TEXT NOT NULL,
                        form_level INTEGER NOT NULL,
                        teacher_name TEXT NOT NULL,
                        updated_date TEXT DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(subject, form_level)
                    )
                """)
                
                # Migrate existing data to all forms
                cursor.execute("SELECT subject, teacher_name FROM subject_teachers")
                old_data = cursor.fetchall()
                
                subjects = ['Agriculture', 'Bible Knowledge', 'Biology', 'Chemistry', 
                           'Chichewa', 'Computer Studies', 'English', 'Geography', 
                           'History', 'Life Skills/SOS', 'Mathematics', 'Physics', 'Business Studies', 'Home Economics']
                
                for form_level in [1, 2, 3, 4]:
                    for subject in subjects:
                        # Find existing teacher or use default
                        teacher_name = f"{subject} Teacher F{form_level}"
                        for old_subject, old_teacher in old_data:
                            if old_subject == subject:
                                teacher_name = f"{old_teacher} F{form_level}"
                                break
                        
                        cursor.execute("""
                            INSERT INTO subject_teachers_new (subject, form_level, teacher_name)
                            VALUES (?, ?, ?)
                        """, (subject, form_level, teacher_name))
                
                # Replace old table
                cursor.execute("DROP TABLE subject_teachers")
                cursor.execute("ALTER TABLE subject_teachers_new RENAME TO subject_teachers")
                
                print("Migration completed successfully!")
            else:
                print("Database already migrated.")
                
    except Exception as e:
        print(f"Migration error: {e}")

if __name__ == "__main__":
    migrate_database()