#!/usr/bin/env python3
"""
Check database schema to understand table structure
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from school_database import SchoolDatabase

def check_database_schema():
    """Check the actual database schema"""
    
    try:
        db = SchoolDatabase()
        
        print("=== Database Schema Check ===\n")
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check students table structure
            print("1. Students Table Structure")
            print("-" * 40)
            
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'students'
                ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            for col in columns:
                print(f"  {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
            
            # Check student_marks table structure
            print("\n2. Student Marks Table Structure")
            print("-" * 40)
            
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'student_marks'
                ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            for col in columns:
                print(f"  {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
            
            # Check student_term_enrollment table structure
            print("\n3. Student Term Enrollment Table Structure")
            print("-" * 40)
            
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'student_term_enrollment'
                ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            for col in columns:
                print(f"  {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
            
            # Check sample data
            print("\n4. Sample Data Analysis")
            print("-" * 40)
            
            # Sample students
            cursor.execute("""
                SELECT student_id, first_name, last_name, school_id, grade_level
                FROM students
                LIMIT 5
            """)
            
            students = cursor.fetchall()
            print("Sample students:")
            for student in students:
                print(f"  ID: {student[0]}, Name: {student[1]} {student[2]}, School: {student[3]}, Form: {student[4]}")
            
            # Sample marks
            cursor.execute("""
                SELECT sm.mark_id, sm.student_id, sm.subject, sm.mark, sm.school_id, sm.form_level, sm.term, sm.academic_year
                FROM student_marks sm
                LIMIT 5
            """)
            
            marks = cursor.fetchall()
            print("\nSample marks:")
            for mark in marks:
                print(f"  ID: {mark[0]}, Student: {mark[1]}, Subject: {mark[2]}, Mark: {mark[3]}, School: {mark[4]}, Form: {mark[5]}, Term: {mark[6]}, Year: {mark[7]}")
            
            # Sample enrollments
            cursor.execute("""
                SELECT ste.student_id, ste.school_id, ste.form_level, ste.term, ste.academic_year
                FROM student_term_enrollment ste
                LIMIT 5
            """)
            
            enrollments = cursor.fetchall()
            print("\nSample enrollments:")
            for enrollment in enrollments:
                print(f"  Student: {enrollment[0]}, School: {enrollment[1]}, Form: {enrollment[2]}, Term: {enrollment[3]}, Year: {enrollment[4]}")
        
        print("\n=== Schema Check Complete ===")
        
    except Exception as e:
        print(f"Error checking schema: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database_schema()
