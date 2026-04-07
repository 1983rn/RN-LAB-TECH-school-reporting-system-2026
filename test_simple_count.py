#!/usr/bin/env python3

import sqlite3
import os
from school_database import SchoolDatabase

def test_student_count_direct():
    """Test that the database methods return correct student count for NANJATI"""
    
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
    print(f"Testing for: {school_name} (ID: {school_id})")
    
    # Test 1: Direct database query
    cursor.execute("SELECT COUNT(*) FROM students WHERE grade_level = 1 AND school_id = ? AND status = 'Active'", (school_id,))
    direct_count = cursor.fetchone()[0]
    print(f"Direct database query: {direct_count} Form 1 students")
    
    # Test 2: Using database method WITHOUT school_id (old way - should get ALL schools)
    students_all = db.get_students_by_grade(1)
    all_count = len(students_all)
    print(f"get_students_by_grade(1) - ALL schools: {all_count} students")
    
    # Test 3: Using database method WITH school_id (new way - should get only NANJATI)
    students_nanjati = db.get_students_by_grade(1, school_id)
    nanjati_count = len(students_nanjati)
    print(f"get_students_by_grade(1, {school_id}) - NANJATI only: {nanjati_count} students")
    
    # Verify the fix
    if direct_count == nanjati_count == 91:
        print("\\n✅ SUCCESS: All methods return correct count (91)")
        success = True
    else:
        print(f"\\n❌ ISSUE: Expected 91, got direct={direct_count}, nanjati={nanjati_count}")
        success = False
    
    # Show the difference
    if all_count != nanjati_count:
        print(f"\\n📊 The fix works: Without school_id filter = {all_count}, With school_id filter = {nanjati_count}")
        print("This confirms that the report generation will now show the correct enrollment.")
    
    conn.close()
    return success

if __name__ == "__main__":
    print("Testing Student Count Fix")
    print("=" * 50)
    
    success = test_student_count_direct()
    
    print("\\n" + "=" * 50)
    if success:
        print("✅ FIX CONFIRMED: The enrollment count issue is resolved!")
        print("\\nReport cards will now show:")
        print("- Total enrollment: 91 (correct)")
        print("- Only NANJATI students in reports")
        print("- Accurate statistics")
    else:
        print("❌ Issue still exists - needs further investigation")