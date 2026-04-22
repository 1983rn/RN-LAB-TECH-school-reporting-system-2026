#!/usr/bin/env python3
"""
Test script to verify the new term/academic year reset functionality
This ensures that when a new term/academic year starts, the student list is empty
"""

import os
import sys
import json
from datetime import datetime

# Add current directory to path 
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from school_database import SchoolDatabase

def test_term_reset_functionality():
    """Test that new terms/academic years show empty student lists"""
    
    print("=== Testing Term/Academic Year Reset Functionality ===")
    
    # Initialize database
    db = SchoolDatabase()
    
    # Test parameters
    test_school_id = 1
    test_form_level = 1
    test_student_id = 375  # Use existing student
    
    # Define test terms and academic years
    existing_term = "Term 1"
    existing_year = "2025-2026"
    new_term = "Term 2"
    new_year = "2025-2026"
    future_year = "2026-2027"
    
    try:
        # Step 1: Verify existing term has students
        print("\n1. Testing existing term (should have students)...")
        existing_students = db.get_students_enrolled_in_term(
            test_form_level, existing_term, existing_year, test_school_id
        )
        print(f"Students in {existing_term} {existing_year}: {len(existing_students)}")
        
        if existing_students:
            print("  Sample students:")
            for i, student in enumerate(existing_students[:3]):
                print(f"    {i+1}. {student['first_name']} {student['last_name']} (ID: {student['student_id']})")
        else:
            print("  No students found - this is unexpected")
        
        # Step 2: Test new term (should be empty)
        print(f"\n2. Testing new term {new_term} (should be empty)...")
        new_term_students = db.get_students_enrolled_in_term(
            test_form_level, new_term, existing_year, test_school_id
        )
        print(f"Students in {new_term} {existing_year}: {len(new_term_students)}")
        
        if len(new_term_students) == 0:
            print("  ** CORRECT: New term shows empty student list **")
        else:
            print("  ** ERROR: New term should be empty but shows students **")
            for student in new_term_students[:3]:
                print(f"    Unexpected: {student['first_name']} {student['last_name']}")
        
        # Step 3: Test future academic year (should be empty)
        print(f"\n3. Testing future academic year {future_year} (should be empty)...")
        future_year_students = db.get_students_enrolled_in_term(
            test_form_level, existing_term, future_year, test_school_id
        )
        print(f"Students in {existing_term} {future_year}: {len(future_year_students)}")
        
        if len(future_year_students) == 0:
            print("  ** CORRECT: Future academic year shows empty student list **")
        else:
            print("  ** ERROR: Future year should be empty but shows students **")
        
        # Step 4: Test enrolling a student in new term
        print(f"\n4. Testing student enrollment in new term...")
        
        # First check if student exists
        student = db.get_student_by_id(test_student_id, test_school_id)
        if student:
            print(f"  Using existing student: {student['first_name']} {student['last_name']}")
            
            # Enroll student in new term
            enrollment_success = db.enroll_student_in_term(
                test_student_id, test_form_level, new_term, existing_year, test_school_id
            )
            
            if enrollment_success:
                print(f"  Successfully enrolled student in {new_term} {existing_year}")
                
                # Check if student now appears
                updated_students = db.get_students_enrolled_in_term(
                    test_form_level, new_term, existing_year, test_school_id
                )
                print(f"  Students in {new_term} after enrollment: {len(updated_students)}")
                
                if len(updated_students) == 1:
                    enrolled_student = updated_students[0]
                    if enrolled_student['student_id'] == test_student_id:
                        print("  ** CORRECT: Enrolled student appears in new term **")
                    else:
                        print("  ** ERROR: Wrong student appeared **")
                else:
                    print("  ** ERROR: Expected 1 student, got more **")
            else:
                print("  ** ERROR: Failed to enroll student **")
        else:
            print(f"  Student {test_student_id} not found")
        
        # Step 5: Test that old term data is preserved
        print(f"\n5. Testing that old term data is preserved...")
        old_term_after = db.get_students_enrolled_in_term(
            test_form_level, existing_term, existing_year, test_school_id
        )
        print(f"Students in {existing_term} {existing_year} after new term enrollment: {len(old_term_after)}")
        
        if len(old_term_after) >= len(existing_students):
            print("  ** CORRECT: Old term data preserved **")
        else:
            print("  ** ERROR: Old term data was affected **")
        
        # Step 6: Test different form levels
        print(f"\n6. Testing different form levels...")
        for form_level in [2, 3, 4]:
            students_form = db.get_students_enrolled_in_term(
                form_level, new_term, existing_year, test_school_id
            )
            print(f"  Form {form_level} {new_term}: {len(students_form)} students")
        
        # Step 7: Test database consistency
        print(f"\n7. Testing database consistency...")
        
        # Count total students in database
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Count all students for this school
            cursor.execute("SELECT COUNT(*) FROM students WHERE school_id = ?", (test_school_id,))
            total_students = cursor.fetchone()[0]
            print(f"  Total students in database: {total_students}")
            
            # Count enrollments by term
            cursor.execute("""
                SELECT term, academic_year, COUNT(*) as count 
                FROM student_term_enrollment 
                WHERE school_id = ? 
                GROUP BY term, academic_year 
                ORDER BY academic_year, term
            """, (test_school_id,))
            
            enrollments = cursor.fetchall()
            print("  Enrollments by term:")
            for term, year, count in enrollments:
                print(f"    {term} {year}: {count} students")
        
        # Step 8: Test the system behavior as expected by the web interface
        print(f"\n8. Simulating web interface behavior...")
        
        # Simulate what the web app does when loading a form
        def simulate_form_loading(form_level, term, academic_year):
            """Simulate the web app's student loading logic"""
            students = db.get_students_enrolled_in_term(form_level, term, academic_year, test_school_id)
            
            # Check if this is a new academic year/term by looking for existing marks
            has_marks = db.check_marks_exist_for_period(form_level, term, academic_year, test_school_id)
            
            is_new_term = not has_marks and not students
            
            return {
                'students': students,
                'has_marks': has_marks,
                'is_new_term': is_new_term,
                'student_count': len(students)
            }
        
        # Test existing term
        existing_result = simulate_form_loading(test_form_level, existing_term, existing_year)
        print(f"  {existing_term} {existing_year}:")
        print(f"    Students: {existing_result['student_count']}")
        print(f"    Has marks: {existing_result['has_marks']}")
        print(f"    Is new term: {existing_result['is_new_term']}")
        
        # Test new term (before enrollment)
        new_term_result = simulate_form_loading(test_form_level, "Term 3", existing_year)
        print(f"  Term 3 {existing_year}:")
        print(f"    Students: {new_term_result['student_count']}")
        print(f"    Has marks: {new_term_result['has_marks']}")
        print(f"    Is new term: {new_term_result['is_new_term']}")
        
        if new_term_result['is_new_term']:
            print("    ** CORRECT: Web interface will show empty state **")
        else:
            print("    ** ERROR: Web interface won't show empty state **")
        
        # Clean up test enrollment
        print(f"\n9. Cleaning up test enrollment...")
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM student_term_enrollment 
                WHERE student_id = ? AND term = ? AND academic_year = ? AND school_id = ?
            """, (test_student_id, new_term, existing_year, test_school_id))
            conn.commit()
            print("  Test enrollment cleaned up")
        
        print("\n" + "="*60)
        print("TERM RESET FUNCTIONALITY TEST COMPLETE")
        print("\nExpected Behavior:")
        print("1. New terms/academic years show empty student lists")
        print("2. Previous term data is preserved")
        print("3. Students must be enrolled for each term separately")
        print("4. Web interface shows appropriate empty state for new terms")
        
    except Exception as e:
        print(f"\n** Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_term_reset_functionality()
