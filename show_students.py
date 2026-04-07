#!/usr/bin/env python3
"""
Show available students for report generation
"""

from school_database import SchoolDatabase

def show_students():
    db = SchoolDatabase()
    
    print("Available students for report generation:")
    print("=" * 60)
    
    for form_level in [1, 2, 3, 4]:
        students = db.get_students_by_grade(form_level)
        print(f"\nForm {form_level} ({len(students)} students):")
        print("-" * 40)
        
        for student in students:
            # Check if student has marks
            marks = db.get_student_marks(student['student_id'], 'Term 1', '2024-2025')
            mark_count = len(marks)
            
            print(f"ID: {student['student_id']:2d} | {student['first_name']} {student['last_name']:<15} | {mark_count} subjects")
    
    print("\n" + "=" * 60)
    print("You can now generate reports for any of these students!")
    print("Use Student ID in the web application.")

if __name__ == "__main__":
    show_students()