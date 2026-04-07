#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from school_database import SchoolDatabase

def test_student_with_marks():
    """Test student who has actual marks"""
    db = SchoolDatabase()
    
    print("=== TESTING STUDENT WITH MARKS ===\n")
    
    # Test ALFRED MTUMBE (who has marks)
    students = db.get_students_by_grade(1)
    alfred = None
    for student in students:
        if "ALFRED" in student['first_name'] and "MTUMBE" in student['last_name']:
            alfred = student
            break
    
    if not alfred:
        print("ALFRED MTUMBE not found!")
        return
    
    print(f"Testing: {alfred['first_name']} {alfred['last_name']} (ID: {alfred['student_id']})")
    
    term = "Term 3"
    academic_year = "2025-2026"
    form_level = 1
    
    # Test his positions
    subjects = ['English', 'Mathematics', 'Biology']
    print(f"\nSubject Positions for {alfred['first_name']} {alfred['last_name']}:")
    print("-" * 50)
    
    for subject in subjects:
        position = db.get_subject_position(alfred['student_id'], subject, term, academic_year, form_level)
        print(f"  {subject}: {position}")
    
    # Check his actual marks
    marks = db.get_student_marks(alfred['student_id'], term, academic_year)
    print(f"\nActual marks ({len(marks)} subjects):")
    for subject, data in marks.items():
        print(f"  {subject}: {data['mark']}")

if __name__ == "__main__":
    test_student_with_marks()
