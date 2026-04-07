#!/usr/bin/env python3

import sqlite3
import os

def check_actual_db():
    """Check the actual database file directly"""
    db_path = "school_reports.db"
    
    if os.path.exists(db_path):
        print(f"Database file exists: {db_path}")
        print(f"File size: {os.path.getsize(db_path)} bytes")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check students table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='students'")
        if cursor.fetchone():
            cursor.execute("SELECT COUNT(*) FROM students")
            student_count = cursor.fetchone()[0]
            print(f"Students in database: {student_count}")
            
            if student_count > 0:
                cursor.execute("SELECT student_id, first_name, last_name, grade_level, status FROM students LIMIT 5")
                students = cursor.fetchall()
                print("Sample students:")
                for student in students:
                    print(f"  ID: {student[0]}, Name: {student[1]} {student[2]}, Form: {student[3]}, Status: {student[4]}")
            
            # Check marks table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='student_marks'")
            if cursor.fetchone():
                cursor.execute("SELECT COUNT(*) FROM student_marks")
                marks_count = cursor.fetchone()[0]
                print(f"Marks in database: {marks_count}")
                
                if marks_count > 0:
                    cursor.execute("SELECT DISTINCT student_id, term, academic_year FROM student_marks LIMIT 5")
                    marks = cursor.fetchall()
                    print("Sample marks:")
                    for mark in marks:
                        print(f"  Student: {mark[0]}, Term: {mark[1]}, Year: {mark[2]}")
        else:
            print("No students table found")
        
        conn.close()
    else:
        print(f"Database file not found: {db_path}")

if __name__ == "__main__":
    check_actual_db()
