#!/usr/bin/env python3
"""
Add sample marks for testing report generation
"""

from school_database import SchoolDatabase
import random

def add_sample_marks():
    db = SchoolDatabase()
    
    subjects = ['Agriculture', 'Biology', 'Bible Knowledge', 'Chemistry', 
               'Chichewa', 'Computer Studies', 'English', 'Geography', 
               'History', 'Life Skills/SOS', 'Mathematics', 'Physics', 'Business Studies', 'Home Economics']
    
    # Get all students
    all_students = []
    for form_level in [1, 2, 3, 4]:
        students = db.get_students_by_grade(form_level)
        all_students.extend(students)
    
    print(f"Adding sample marks for {len(all_students)} students...")
    
    for student in all_students:
        student_id = student['student_id']
        form_level = student['grade_level']
        
        print(f"Adding marks for {student['first_name']} {student['last_name']} (Form {form_level})")
        
        for subject in subjects:
            # Generate realistic marks (40-95)
            mark = random.randint(40, 95)
            
            try:
                db.save_student_mark(student_id, subject, mark, 'Term 1', '2024-2025', form_level)
            except Exception as e:
                print(f"Error saving mark for {subject}: {e}")
    
    print("Sample marks added successfully!")
    print("You can now generate reports for any student.")

if __name__ == "__main__":
    add_sample_marks()