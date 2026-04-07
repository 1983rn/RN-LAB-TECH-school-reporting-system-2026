#!/usr/bin/env python3

import sqlite3
import os

def fix_student_status():
    """Fix student status to 'Active' for all students"""
    db_path = "school_reports.db"
    
    if os.path.exists(db_path):
        print(f"Updating student statuses in: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current status distribution
        cursor.execute("SELECT status, COUNT(*) FROM students GROUP BY status")
        status_counts = cursor.fetchall()
        print("Current status distribution:")
        for status, count in status_counts:
            print(f"  {status or 'NULL'}: {count}")
        
        # Update all NULL or empty statuses to 'Active'
        cursor.execute("""
            UPDATE students 
            SET status = 'Active' 
            WHERE status IS NULL OR status = '' OR status = 'None'
        """)
        
        updated_count = cursor.rowcount
        print(f"\nUpdated {updated_count} students to 'Active' status")
        
        # Verify the update
        cursor.execute("SELECT status, COUNT(*) FROM students GROUP BY status")
        new_status_counts = cursor.fetchall()
        print("\nNew status distribution:")
        for status, count in new_status_counts:
            print(f"  {status}: {count}")
        
        conn.commit()
        conn.close()
        
        print(f"\nSuccessfully updated {updated_count} student records!")
    else:
        print(f"Database file not found: {db_path}")

if __name__ == "__main__":
    fix_student_status()
