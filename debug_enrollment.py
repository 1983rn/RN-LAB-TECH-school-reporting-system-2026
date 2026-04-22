#!/usr/bin/env python3
"""
Debug script to check enrollment issues
"""

import os
import sys

# Add current directory to path 
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from school_database import SchoolDatabase

def debug_enrollment():
    """Debug enrollment issues"""
    
    print("=== Debugging Enrollment Issues ===")
    
    # Initialize database
    db = SchoolDatabase()
    
    # Test parameters
    test_school_id = 2
    test_form_level = 1
    test_term = "Term 1"
    test_academic_year = "2025-2026"
    test_student_id = 10008
    
    try:
        # Check student exists
        student_info = db.get_student_by_id(test_student_id, test_school_id)
        if student_info:
            print(f"Student found: {student_info['first_name']} {student_info['last_name']}")
        else:
            print("Student not found")
            return
        
        # Check enrollment table directly
        print(f"\nChecking enrollment table directly...")
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check all enrollments for this student
            cursor.execute("""
                SELECT * FROM student_term_enrollment 
                WHERE student_id = ? AND school_id = ?
            """, (test_student_id, test_school_id))
            all_enrollments = cursor.fetchall()
            print(f"All enrollments for student {test_student_id}: {len(all_enrollments)}")
            for record in all_enrollments:
                print(f"  {record}")
            
            # Check specific enrollment
            cursor.execute("""
                SELECT * FROM student_term_enrollment 
                WHERE student_id = ? AND form_level = ? AND term = ? AND academic_year = ? AND school_id = ?
            """, (test_student_id, test_form_level, test_term, test_academic_year, test_school_id))
            specific_enrollments = cursor.fetchall()
            print(f"Specific enrollment check: {len(specific_enrollments)}")
            for record in specific_enrollments:
                print(f"  {record}")
        
        # Try enrollment
        print(f"\nAttempting enrollment...")
        enrollment_success = db.enroll_student_in_term(
            test_student_id, test_form_level, test_term, test_academic_year, test_school_id
        )
        print(f"Enrollment result: {enrollment_success}")
        
        # Check again
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM student_term_enrollment 
                WHERE student_id = ? AND form_level = ? AND term = ? AND academic_year = ? AND school_id = ?
            """, (test_student_id, test_form_level, test_term, test_academic_year, test_school_id))
            after_enrollments = cursor.fetchall()
            print(f"After enrollment check: {len(after_enrollments)}")
            for record in after_enrollments:
                print(f"  {record}")
        
        # Test get_students_enrolled_in_term function
        print(f"\nTesting get_students_enrolled_in_term function...")
        students = db.get_students_enrolled_in_term(test_form_level, test_term, test_academic_year, test_school_id)
        print(f"Function returned: {len(students)} students")
        for student in students:
            print(f"  - {student['student_id']}: {student['first_name']} {student['last_name']}")
        
        # Check what the function is actually doing
        print(f"\nChecking function implementation...")
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # This is what get_students_enrolled_in_term should be doing
            cursor.execute("""
                SELECT s.student_id, s.first_name, s.last_name 
                FROM students s
                JOIN student_term_enrollment ste ON s.student_id = ste.student_id
                WHERE ste.form_level = ? AND ste.term = ? AND ste.academic_year = ? AND ste.school_id = ?
                ORDER BY s.first_name, s.last_name
            """, (test_form_level, test_term, test_academic_year, test_school_id))
            direct_query = cursor.fetchall()
            print(f"Direct query result: {len(direct_query)} students")
            for record in direct_query:
                print(f"  - {record}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_enrollment()
