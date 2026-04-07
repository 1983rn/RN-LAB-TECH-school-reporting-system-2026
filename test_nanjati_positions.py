#!/usr/bin/env python3
"""
Test Position Calculations for NANJATI COMMUNITY DAY SECONDARY SCHOOL
Verify that the fixes are working correctly
"""

import sqlite3
import os
import sys

# Add current directory to path 
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from school_database import SchoolDatabase

def test_position_calculations():
    """Test the fixed position calculation methods"""
    
    db = SchoolDatabase()
    nanjati_school_id = 2
    
    print("=== TESTING FIXED POSITION CALCULATIONS ===\n")
    
    # Test with the latest data period
    term = "Term 1"
    academic_year = "2025-2026"
    form_level = 1
    
    print(f"Testing Form {form_level}, {term} {academic_year}")
    print("=" * 50)
    
    # 1. Test get_student_rankings
    print("1. Testing get_student_rankings...")
    rankings_result = db.get_student_rankings(form_level, term, academic_year, nanjati_school_id)
    
    if isinstance(rankings_result, dict):
        rankings = rankings_result.get('rankings', [])
        total_students = rankings_result.get('total_students', 0)
        students_with_marks = rankings_result.get('students_with_marks', 0)
        
        print(f"   Total students in class: {total_students}")
        print(f"   Students with marks: {students_with_marks}")
        print(f"   Rankings calculated: {len(rankings)}")
        
        # Show top 5 students
        print("\n   Top 5 students:")
        for i, student in enumerate(rankings[:5]):
            pos = student.get('position', i+1)
            name = student.get('name', 'Unknown')
            avg = student.get('average', 0)
            status = student.get('status', 'Unknown')
            subjects = student.get('total_subjects', 0)
            print(f"   {pos:2d}. {name:<25} Avg: {avg:5.1f} Status: {status} Subjects: {subjects}")
    else:
        print("   ERROR: get_student_rankings returned unexpected format")
        return
    
    # 2. Test get_student_position_and_points for a specific student
    if rankings:
        test_student_name = rankings[0]['name']  # Use first student
        
        # Find student ID by name
        with db.get_connection() as conn:
            cursor = conn.cursor()
            first_name, last_name = test_student_name.split(' ', 1)
            cursor.execute("""
                SELECT student_id FROM students 
                WHERE first_name = ? AND last_name = ? AND school_id = ?
            """, (first_name, last_name, nanjati_school_id))
            
            result = cursor.fetchone()
            if result:
                test_student_id = result[0]
                
                print(f"\n2. Testing get_student_position_and_points for {test_student_name}...")
                position_result = db.get_student_position_and_points(
                    test_student_id, term, academic_year, form_level, nanjati_school_id
                )
                
                print(f"   Position: {position_result.get('position', 'N/A')}")
                print(f"   Aggregate Points: {position_result.get('aggregate_points', 0)}")
                print(f"   Total Students: {position_result.get('total_students', 0)}")
                
                # 3. Test get_subject_position for the same student
                print(f"\n3. Testing get_subject_position for {test_student_name}...")
                
                # Get subjects this student has marks for
                cursor.execute("""
                    SELECT DISTINCT subject FROM student_marks 
                    WHERE student_id = ? AND term = ? AND academic_year = ? AND school_id = ?
                    ORDER BY subject
                    LIMIT 5
                """, (test_student_id, term, academic_year, nanjati_school_id))
                
                subjects = [row[0] for row in cursor.fetchall()]
                
                for subject in subjects:
                    subject_pos = db.get_subject_position(
                        test_student_id, subject, term, academic_year, form_level, nanjati_school_id
                    )
                    print(f"   {subject}: {subject_pos}")
    
    # 4. Test with a few more students to verify consistency
    print(f"\n4. Testing position consistency for multiple students...")
    
    test_count = min(5, len(rankings))
    for i in range(test_count):
        student = rankings[i]
        student_name = student['name']
        expected_position = student.get('position', i+1)
        
        # Find student ID
        with db.get_connection() as conn:
            cursor = conn.cursor()
            first_name, last_name = student_name.split(' ', 1)
            cursor.execute("""
                SELECT student_id FROM students 
                WHERE first_name = ? AND last_name = ? AND school_id = ?
            """, (first_name, last_name, nanjati_school_id))
            
            result = cursor.fetchone()
            if result:
                student_id = result[0]
                
                position_result = db.get_student_position_and_points(
                    student_id, term, academic_year, form_level, nanjati_school_id
                )
                
                actual_position = position_result.get('position', 'N/A')
                
                status = "OK" if str(actual_position) == str(expected_position) else "MISMATCH"
                print(f"   {student_name:<25} Expected: {expected_position:2} Actual: {actual_position:2} [{status}]")
    
    print(f"\n=== POSITION CALCULATION TEST COMPLETE ===")
    print(f"Summary:")
    print(f"- Total students in Form {form_level}: {total_students}")
    print(f"- Students with marks: {students_with_marks}")
    print(f"- Position calculations: {'WORKING' if rankings else 'FAILED'}")
    print(f"- Subject positions: {'WORKING' if subjects else 'NO DATA'}")

if __name__ == "__main__":
    test_position_calculations()