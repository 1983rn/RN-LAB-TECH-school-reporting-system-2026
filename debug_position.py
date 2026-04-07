#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from school_database import SchoolDatabase

def debug_position_calculation():
    """Debug position calculation for Falla Communti Day Secondary School"""
    db = SchoolDatabase()
    
    print("=== DEBUGGING POSITION CALCULATION ===\n")
    
    # Check all forms to see where students are
    for form_level in [1, 2, 3, 4]:
        print(f"Form {form_level}:")
        print("-" * 30)
        
        # 1. Check all enrolled students
        all_students = db.get_students_by_grade(form_level)
        print(f"Total enrolled students: {len(all_students)}")
        
        if all_students:
            for i, student in enumerate(all_students):
                print(f"  {i+1}. {student['first_name']} {student['last_name']} (ID: {student['student_id']}, School: {student.get('school_id', 'N/A')})")
            
            # 2. Check student rankings
            rankings = db.get_student_rankings(form_level, "Term 1", "2025-2026")
            print(f"Rankings returned: {len(rankings)} students")
            for i, student in enumerate(rankings):
                print(f"  {i+1}. {student['name']} - Avg: {student.get('average', 'N/A')} - Status: {student.get('status', 'N/A')} - Pos: {student.get('position', 'N/A')}")
            
            # 3. Check subject positions for first student
            first_student = all_students[0]
            student_id = first_student['student_id']
            student_name = f"{first_student['first_name']} {first_student['last_name']}"
            
            print(f"\nSubject positions for: {student_name}")
            print("-" * 25)
            
            subjects = ['English', 'Mathematics', 'Biology', 'Geography', 'History']
            for subject in subjects:
                position = db.get_subject_position(student_id, subject, "Term 1", "2025-2026", form_level)
                print(f"  {subject}: {position}")
            
            # 4. Check marks in database
            marks = db.get_student_marks(student_id, "Term 1", "2025-2026")
            print(f"\nMarks for {student_name}:")
            print("-" * 25)
            if marks:
                for subject, data in marks.items():
                    print(f"  {subject}: {data['mark']}")
            else:
                print("  No marks found")
        
        print("\n" + "=" * 50 + "\n")

if __name__ == "__main__":
    debug_position_calculation()
