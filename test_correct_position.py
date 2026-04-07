#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from school_database import SchoolDatabase

def test_correct_position():
    """Test position calculation with correct term/year"""
    db = SchoolDatabase()
    
    print("=== TESTING CORRECT POSITION CALCULATION ===\n")
    
    # Test with Term 3 2025-2026 (where most marks exist)
    term = "Term 3"
    academic_year = "2025-2026"
    form_level = 1
    
    print(f"Testing: Form {form_level}, {term}, {academic_year}")
    print("-" * 50)
    
    # Get students
    students = db.get_students_by_grade(form_level)
    print(f"Total students: {len(students)}")
    
    # Test first few students' positions
    for i, student in enumerate(students[:3]):
        student_id = student['student_id']
        student_name = f"{student['first_name']} {student['last_name']}"
        
        # Overall position
        position_data = db.get_student_position_and_points(student_id, term, academic_year, form_level)
        overall_pos = position_data.get('position', 'N/A')
        total_students = position_data.get('total_students', 'N/A')
        
        print(f"\n{student_name}:")
        print(f"  Overall Position: {overall_pos}/{total_students}")
        
        # Subject positions
        subjects = ['English', 'Mathematics', 'Biology']
        for subject in subjects:
            subject_pos = db.get_subject_position(student_id, subject, term, academic_year, form_level)
            print(f"  {subject}: {subject_pos}")

if __name__ == "__main__":
    test_correct_position()
