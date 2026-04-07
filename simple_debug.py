#!/usr/bin/env python3
"""
Simple debug script to check Form 3 students issue without pandas
"""

import sqlite3

def debug_students():
    try:
        conn = sqlite3.connect('school_reports.db')
        cursor = conn.cursor()
        
        print("=== DEBUGGING FORM 3 STUDENTS ISSUE ===")
        
        # Check all students by grade level
        print("\n1. Student count by grade level:")
        cursor.execute("SELECT COUNT(*) as count, grade_level FROM students GROUP BY grade_level ORDER BY grade_level")
        grade_counts = cursor.fetchall()
        for count, grade in grade_counts:
            print(f"   Grade {grade}: {count} students")
        
        # Check Form 3 students specifically
        print("\n2. Form 3 students details:")
        cursor.execute("SELECT student_id, first_name, last_name, grade_level, status FROM students WHERE grade_level = 3")
        form3_students = cursor.fetchall()
        if form3_students:
            for student in form3_students:
                print(f"   ID: {student[0]}, Name: {student[1]} {student[2]}, Grade: {student[3]}, Status: {student[4]}")
        else:
            print("   ❌ NO FORM 3 STUDENTS FOUND!")
        
        # Check if there are any inactive Form 3 students
        print("\n3. Checking inactive Form 3 students:")
        cursor.execute("SELECT student_id, first_name, last_name, grade_level, status FROM students WHERE grade_level = 3 AND status != 'Active'")
        inactive_form3 = cursor.fetchall()
        if inactive_form3:
            for student in inactive_form3:
                print(f"   INACTIVE - ID: {student[0]}, Name: {student[1]} {student[2]}, Status: {student[4]}")
        else:
            print("   No inactive Form 3 students found")
        
        # Check all students regardless of status
        print("\n4. ALL Form 3 students (any status):")
        cursor.execute("SELECT student_id, first_name, last_name, grade_level, status FROM students WHERE grade_level = 3")
        all_form3 = cursor.fetchall()
        if all_form3:
            for student in all_form3:
                print(f"   ID: {student[0]}, Name: {student[1]} {student[2]}, Status: {student[4]}")
        else:
            print("   ❌ NO FORM 3 STUDENTS AT ALL!")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_students()
