#!/usr/bin/env python3
"""
Debug script to check student data in the database
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from school_database import SchoolDatabase

def debug_student_data():
    """Debug student data to understand why names aren't showing"""
    try:
        db = SchoolDatabase()
        print(f"Database path: {db.db_path}")
        print(f"Using Postgres: {getattr(db, 'use_postgres', False)}")
        
        # Get all schools
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check schools
            if getattr(db, 'use_postgres', False):
                cursor.execute("SELECT school_id, school_name FROM schools ORDER BY school_id")
            else:
                cursor.execute("SELECT school_id, school_name FROM schools ORDER BY school_id")
            
            schools = cursor.fetchall()
            print(f"\nFound {len(schools)} schools:")
            for school in schools:
                print(f"  School ID: {school[0]}, Name: {school[1]}")
        
        # Check students for each school and form
        for school_id, school_name in schools:
            print(f"\n=== School: {school_name} (ID: {school_id}) ===")
            
            for form_level in [1, 2, 3, 4]:
                print(f"\n--- Form {form_level} ---")
                
                # Get students by grade
                try:
                    students = db.get_students_by_grade(form_level, school_id)
                    print(f"Found {len(students)} students")
                    
                    if students:
                        print("Student details:")
                        for student in students[:5]:  # Show first 5 students
                            print(f"  ID: {student.get('student_id')}, Name: {student.get('first_name')} {student.get('last_name')}, Status: {student.get('status')}, Grade: {student.get('grade_level')}")
                        
                        if len(students) > 5:
                            print(f"  ... and {len(students) - 5} more students")
                    else:
                        print("  No students found")
                        
                        # Let's check if there are any students at all for this school
                        with db.get_connection() as conn:
                            cursor = conn.cursor()
                            if getattr(db, 'use_postgres', False):
                                cursor.execute("SELECT student_id, first_name, last_name, grade_level, status FROM students WHERE school_id = %s ORDER BY grade_level, first_name", (school_id,))
                            else:
                                cursor.execute("SELECT student_id, first_name, last_name, grade_level, status FROM students WHERE school_id = ? ORDER BY grade_level, first_name", (school_id,))
                            
                            all_students = cursor.fetchall()
                            print(f"  Total students in school: {len(all_students)}")
                            
                            for student in all_students[:5]:
                                print(f"    ID: {student[0]}, Name: {student[1]} {student[2]}, Grade: {student[3]}, Status: {student[4]}")
                            
                            if len(all_students) > 5:
                                print(f"    ... and {len(all_students) - 5} more students")
                
                except Exception as e:
                    print(f"  Error getting students: {e}")
        
        # Check school settings
        print(f"\n=== School Settings ===")
        for school_id, school_name in schools:
            try:
                settings = db.get_school_settings(school_id)
                print(f"\nSchool {school_name} (ID: {school_id}):")
                print(f"  Selected Term: {settings.get('selected_term')}")
                print(f"  Selected Academic Year: {settings.get('selected_academic_year')}")
                print(f"  Terms: {settings.get('terms')}")
                print(f"  Academic Years: {settings.get('academic_years')}")
            except Exception as e:
                print(f"  Error getting settings: {e}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_student_data()
