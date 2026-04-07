#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from school_database import SchoolDatabase

def test_hamida_position():
    """Test position for HAMIDA KAIWE with all marks"""
    db = SchoolDatabase()
    
    print("=== TESTING HAMIDA KAIWE POSITION ===\n")
    
    # Find HAMIDA KAIWE in Form 1
    students = db.get_students_by_grade(1)
    hamida = None
    for student in students:
        if "HAMIDA" in student['first_name'] and "KAIWE" in student['last_name']:
            hamida = student
            break
    
    if not hamida:
        print("HAMIDA KAIWE not found!")
        return
    
    print(f"Found: {hamida['first_name']} {hamida['last_name']} (ID: {hamida['student_id']})")
    
    # Test with Term 3 2025-2026 (where he has all marks)
    term = "Term 3"
    academic_year = "2025-2026"
    form_level = 1
    
    print(f"\nTesting: Form {form_level}, {term}, {academic_year}")
    print("-" * 50)
    
    # Overall position
    position_data = db.get_student_position_and_points(hamida['student_id'], term, academic_year, form_level)
    overall_pos = position_data.get('position', 'N/A')
    total_students = position_data.get('total_students', 'N/A')
    
    print(f"Overall Position: {overall_pos}/{total_students}")
    
    # Subject positions
    subjects = ['English', 'Mathematics', 'Biology', 'Geography', 'History', 'Agriculture', 'Physical Science', 'Social Studies', 'Chichewa']
    print(f"\nSubject Positions for {hamida['first_name']} {hamida['last_name']}:")
    print("-" * 40)
    
    for subject in subjects:
        position = db.get_subject_position(hamida['student_id'], subject, term, academic_year, form_level)
        print(f"  {subject}: {position}")
    
    # Check his actual marks
    marks = db.get_student_marks(hamida['student_id'], term, academic_year)
    print(f"\nActual marks ({len(marks)} subjects):")
    for subject, data in marks.items():
        print(f"  {subject}: {data['mark']}")

if __name__ == "__main__":
    test_hamida_position()
