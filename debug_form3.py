#!/usr/bin/env python3
"""
Debug script to check Form 3 students issue
"""

import sqlite3
import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from school_database import SchoolDatabase

def debug_form3_students():
    print("Debugging Form 3 students issue...")
    print("=" * 50)
    
    # Direct database query
    try:
        conn = sqlite3.connect('school_reports.db')
        cursor = conn.cursor()
        
        # Check all students by grade level
        print("\n1. Direct database query - All students by grade:")
        cursor.execute("SELECT COUNT(*) as count, grade_level FROM students GROUP BY grade_level ORDER BY grade_level")
        grade_counts = cursor.fetchall()
        for count, grade in grade_counts:
            print(f"   Grade {grade}: {count} students")
        
        # Check Form 3 students specifically
        print("\n2. Form 3 students in database:")
        cursor.execute("SELECT student_id, first_name, last_name, grade_level, status FROM students WHERE grade_level = 3")
        form3_students = cursor.fetchall()
        if form3_students:
            for student in form3_students:
                print(f"   ID: {student[0]}, Name: {student[1]} {student[2]}, Grade: {student[3]}, Status: {student[4]}")
        else:
            print("   No Form 3 students found in database!")
        
        conn.close()
        
    except Exception as e:
        print(f"Error with direct database query: {e}")
    
    # Using SchoolDatabase class
    try:
        print("\n3. Using SchoolDatabase class:")
        db = SchoolDatabase()
        
        for form_level in [1, 2, 3, 4]:
            students = db.get_students_by_grade(form_level)
            print(f"   Form {form_level}: {len(students)} students")
            if form_level == 3 and students:
                for student in students:
                    print(f"      - {student['first_name']} {student['last_name']} (ID: {student['student_id']})")
        
    except Exception as e:
        print(f"Error with SchoolDatabase class: {e}")
    
    # Test the API endpoint logic
    try:
        print("\n4. Testing API endpoint logic:")
        db = SchoolDatabase()
        all_students = []
        for form_level in [1, 2, 3, 4]:
            form_students = db.get_students_by_grade(form_level)
            all_students.extend(form_students)
            print(f"   Added {len(form_students)} students from Form {form_level}")
        
        print(f"   Total students for API: {len(all_students)}")
        
        # Group by form level like the frontend does
        students_by_form = {}
        for student in all_students:
            form = student['grade_level']
            if form not in students_by_form:
                students_by_form[form] = []
            students_by_form[form].append(student)
        
        print("   Students grouped by form:")
        for form in sorted(students_by_form.keys()):
            print(f"      Form {form}: {len(students_by_form[form])} students")
            
    except Exception as e:
        print(f"Error testing API logic: {e}")

if __name__ == "__main__":
    debug_form3_students()
