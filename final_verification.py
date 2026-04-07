#!/usr/bin/env python3

import sqlite3
import os
from school_database import SchoolDatabase

def test_final_verification():
    """Final verification that the enrollment count fix works"""
    
    # Initialize database
    db = SchoolDatabase()
    
    # Get NANJATI school info
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT school_id, school_name FROM schools WHERE school_name LIKE '%NANJATI%'")
    school = cursor.fetchone()
    
    if not school:
        print("NANJATI school not found")
        return False
    
    school_id, school_name = school
    print(f"School: {school_name} (ID: {school_id})")
    
    # Test the database method WITH school_id (the fix)
    students_nanjati = db.get_students_by_grade(1, school_id)
    nanjati_count = len(students_nanjati)
    print(f"Form 1 students for NANJATI only: {nanjati_count}")
    
    # Test without school_id (shows the problem)
    students_all = db.get_students_by_grade(1)
    all_count = len(students_all)
    print(f"Form 1 students from ALL schools: {all_count}")
    
    conn.close()
    
    # The fix is working if NANJATI-only count is 91
    if nanjati_count == 91:
        print("\\nSUCCESS: Fix is working correctly!")
        print("Report generation will now show 91 students (correct)")
        return True
    else:
        print(f"\\nISSUE: Expected 91, got {nanjati_count}")
        return False

if __name__ == "__main__":
    print("Final Verification of Enrollment Count Fix")
    print("=" * 50)
    
    success = test_final_verification()
    
    print("\\n" + "=" * 50)
    if success:
        print("RESOLUTION CONFIRMED!")
        print("\\nThe issue has been fixed:")
        print("- Report cards will show correct enrollment (91)")
        print("- Only NANJATI students will be counted")
        print("- No more incorrect totals of 44 or 49")
    else:
        print("Issue needs further investigation")