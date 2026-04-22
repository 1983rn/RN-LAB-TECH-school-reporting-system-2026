#!/usr/bin/env python3
"""
Test script to reproduce and diagnose the mark persistence issue
"""

import os
import sys
import json
from datetime import datetime

# Add current directory to path 
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from school_database import SchoolDatabase

def test_mark_persistence():
    """Test if marks are being saved and retrieved correctly"""
    
    print("=== Testing Mark Persistence Issue ===")
    
    # Initialize database
    db = SchoolDatabase()
    
    # Test parameters
    test_school_id = 1
    test_student_id = 1
    test_term = "Term 1"
    test_academic_year = "2025-2026"
    test_form_level = 1
    test_subject = "Mathematics"
    test_mark = 85
    
    print(f"Test Parameters:")
    print(f"  School ID: {test_school_id}")
    print(f"  Student ID: {test_student_id}")
    print(f"  Term: {test_term}")
    print(f"  Academic Year: {test_academic_year}")
    print(f"  Form Level: {test_form_level}")
    print(f"  Subject: {test_subject}")
    print(f"  Mark: {test_mark}")
    print()
    
    try:
        # Step 1: Check if student exists and belongs to school
        print("Step 1: Checking student ownership...")
        student = db.get_student_by_id(test_student_id, test_school_id)
        if not student:
            print(f"❌ Student {test_student_id} not found for school {test_school_id}")
            # Try to find any student
            students = db.get_students_by_grade(test_form_level, test_school_id)
            if students:
                test_student_id = students[0]['student_id']
                print(f"✅ Using existing student: {test_student_id} - {students[0]['first_name']} {students[0]['last_name']}")
            else:
                print("❌ No students found. Creating test student...")
                student_data = {
                    'first_name': 'Test',
                    'last_name': 'Student',
                    'grade_level': test_form_level
                }
                test_student_id = db.add_student(student_data, test_school_id)
                print(f"✅ Created test student with ID: {test_student_id}")
        
        # Step 2: Save a mark
        print("\nStep 2: Saving mark...")
        db.save_student_mark(
            test_student_id, 
            test_subject, 
            test_mark, 
            test_term, 
            test_academic_year, 
            test_form_level, 
            test_school_id
        )
        print(f"✅ Mark saved: {test_subject} = {test_mark}")
        
        # Step 3: Immediately retrieve the mark
        print("\nStep 3: Retrieving mark immediately...")
        marks = db.get_student_marks(test_student_id, test_term, test_academic_year, test_school_id)
        print(f"Retrieved marks: {json.dumps(marks, indent=2)}")
        
        if test_subject in marks:
            retrieved_mark = marks[test_subject]['mark']
            if retrieved_mark == test_mark:
                print(f"✅ Mark retrieved correctly: {retrieved_mark}")
            else:
                print(f"❌ Mark mismatch! Expected: {test_mark}, Got: {retrieved_mark}")
        else:
            print(f"❌ Mark not found for subject: {test_subject}")
        
        # Step 4: Test with new connection (simulate page refresh)
        print("\nStep 4: Testing with new database connection (simulating page refresh)...")
        
        # Create new database instance
        db2 = SchoolDatabase()
        marks2 = db2.get_student_marks(test_student_id, test_term, test_academic_year, test_school_id)
        print(f"Retrieved marks with new connection: {json.dumps(marks2, indent=2)}")
        
        if test_subject in marks2:
            retrieved_mark2 = marks2[test_subject]['mark']
            if retrieved_mark2 == test_mark:
                print(f"✅ Mark persisted correctly: {retrieved_mark2}")
            else:
                print(f"❌ Mark not persisted! Expected: {test_mark}, Got: {retrieved_mark2}")
        else:
            print(f"❌ Mark not found after refresh for subject: {test_subject}")
        
        # Step 5: Check database directly
        print("\nStep 5: Checking database directly...")
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM student_marks 
                WHERE student_id = ? AND subject = ? AND term = ? AND academic_year = ? AND school_id = ?
            """, (test_student_id, test_subject, test_term, test_academic_year, test_school_id))
            
            rows = cursor.fetchall()
            print(f"Direct database query returned {len(rows)} rows:")
            for row in rows:
                print(f"  Row: {row}")
        
        # Step 6: Test multiple saves
        print("\nStep 6: Testing multiple mark saves...")
        test_marks = [
            ("English", 78),
            ("Science", 92),
            ("History", 65)
        ]
        
        for subject, mark in test_marks:
            db.save_student_mark(
                test_student_id, subject, mark, test_term, test_academic_year, 
                test_form_level, test_school_id
            )
            print(f"✅ Saved: {subject} = {mark}")
        
        # Step 7: Verify all marks
        print("\nStep 7: Verifying all marks...")
        final_marks = db.get_student_marks(test_student_id, test_term, test_academic_year, test_school_id)
        print(f"Final marks: {json.dumps(final_marks, indent=2)}")
        
        all_persisted = True
        for subject, expected_mark in [(test_subject, test_mark)] + test_marks:
            if subject in final_marks and final_marks[subject]['mark'] == expected_mark:
                print(f"✅ {subject}: {expected_mark}")
            else:
                actual = final_marks.get(subject, {}).get('mark', 'NOT FOUND')
                print(f"❌ {subject}: Expected {expected_mark}, Got {actual}")
                all_persisted = False
        
        if all_persisted:
            print("\n🎉 ALL MARKS PERSISTED CORRECTLY!")
        else:
            print("\n💥 MARK PERSISTENCE ISSUE DETECTED!")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mark_persistence()
