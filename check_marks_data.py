#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from school_database import SchoolDatabase

def check_marks_data():
    """Check what marks exist for Form 1 students"""
    db = SchoolDatabase()
    
    print("=== CHECKING MARKS DATA ===\n")
    
    # Get Form 1 students
    students = db.get_students_by_grade(1)
    print(f"Form 1 students: {len(students)}")
    
    # Check different term/year combinations
    combinations = [
        ("Term 1", "2024-2025"),
        ("Term 1", "2025-2026"),
        ("Term 2", "2024-2025"),
        ("Term 2", "2025-2026"),
    ]
    
    for term, year in combinations:
        print(f"\n--- {term} - {year} ---")
        students_with_marks = 0
        total_marks = 0
        
        for student in students:
            marks = db.get_student_marks(student['student_id'], term, year)
            if marks:
                students_with_marks += 1
                total_marks += len(marks)
        
        print(f"Students with marks: {students_with_marks}/{len(students)}")
        print(f"Total marks: {total_marks}")
        
        # Check first student's subject positions
        if students:
            first_student = students[0]
            student_id = first_student['student_id']
            student_name = f"{first_student['first_name']} {first_student['last_name']}"
            
            subjects = ['English', 'Mathematics', 'Biology']
            print(f"Subject positions for {student_name}:")
            for subject in subjects:
                position = db.get_subject_position(student_id, subject, term, year, 1)
                print(f"  {subject}: {position}")

if __name__ == "__main__":
    check_marks_data()
