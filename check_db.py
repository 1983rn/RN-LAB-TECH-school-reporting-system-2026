#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from school_database import SchoolDatabase

def check_database_content():
    """Check what's actually in the database"""
    db = SchoolDatabase()
    
    print("=== DATABASE CONTENT CHECK ===\n")
    
    # Check all students regardless of status
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM students")
            total_students = cursor.fetchone()[0]
            print(f"Total students in database (all statuses): {total_students}")
            
            # Check by status
            cursor.execute("SELECT status, COUNT(*) FROM students GROUP BY status")
            status_counts = cursor.fetchall()
            print("Students by status:")
            for status, count in status_counts:
                print(f"  {status}: {count}")
            
            # Check by grade level
            cursor.execute("SELECT grade_level, COUNT(*) FROM students GROUP BY grade_level")
            grade_counts = cursor.fetchall()
            print("\nStudents by grade level:")
            for grade, count in grade_counts:
                print(f"  Form {grade}: {count}")
            
            # Check by school_id
            cursor.execute("SELECT school_id, COUNT(*) FROM students GROUP BY school_id")
            school_counts = cursor.fetchall()
            print("\nStudents by school_id:")
            for school_id, count in school_counts:
                print(f"  School {school_id}: {count}")
            
            # Show first few students
            cursor.execute("SELECT student_id, first_name, last_name, grade_level, status, school_id FROM students LIMIT 10")
            students = cursor.fetchall()
            print("\nFirst 10 students:")
            for student in students:
                print(f"  ID: {student[0]}, Name: {student[1]} {student[2]}, Form: {student[3]}, Status: {student[4]}, School: {student[5]}")
                
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    check_database_content()
