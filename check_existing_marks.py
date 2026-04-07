#!/usr/bin/env python3
"""
Check Existing Marks for NANJATI COMMUNITY DAY SECONDARY SCHOOL
Verify what marks are already in the database
"""

import sqlite3
import os

def check_nanjati_marks():
    """Check existing marks for NANJATI students"""
    
    db_path = "school_reports.db"
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    nanjati_school_id = 2
    
    print("=== CHECKING EXISTING NANJATI MARKS ===\n")
    
    # Check all available periods for NANJATI
    cursor.execute("""
        SELECT DISTINCT sm.term, sm.academic_year, COUNT(DISTINCT s.student_id) as student_count, COUNT(*) as mark_count
        FROM student_marks sm
        JOIN students s ON sm.student_id = s.student_id
        WHERE s.school_id = ? AND s.grade_level = 1
        GROUP BY sm.term, sm.academic_year
        ORDER BY sm.academic_year DESC, sm.term
    """, (nanjati_school_id,))
    
    periods = cursor.fetchall()
    print("Available periods with marks:")
    for period in periods:
        print(f"  {period[0]} {period[1]}: {period[2]} students, {period[3]} marks")
    
    # Check the specific period mentioned
    term = "Term 1"
    academic_year = "2025-2026"
    
    print(f"\nDetailed check for {term} {academic_year}:")
    print("=" * 50)
    
    # Get total students
    cursor.execute("""
        SELECT COUNT(*) FROM students 
        WHERE school_id = ? AND grade_level = 1 AND status = 'Active'
    """, (nanjati_school_id,))
    total_students = cursor.fetchone()[0]
    
    # Get students with marks for this period
    cursor.execute("""
        SELECT DISTINCT s.student_id, s.first_name, s.last_name, COUNT(sm.mark_id) as mark_count
        FROM students s
        LEFT JOIN student_marks sm ON s.student_id = sm.student_id 
            AND sm.term = ? AND sm.academic_year = ? AND sm.school_id = ?
        WHERE s.school_id = ? AND s.grade_level = 1 AND s.status = 'Active'
        GROUP BY s.student_id, s.first_name, s.last_name
        ORDER BY mark_count DESC, s.first_name, s.last_name
    """, (term, academic_year, nanjati_school_id, nanjati_school_id))
    
    students_data = cursor.fetchall()
    
    students_with_marks = sum(1 for s in students_data if s[3] > 0)
    students_without_marks = sum(1 for s in students_data if s[3] == 0)
    
    print(f"Total Form 1 students: {total_students}")
    print(f"Students with marks: {students_with_marks}")
    print(f"Students without marks: {students_without_marks}")
    
    # Show students with marks
    if students_with_marks > 0:
        print(f"\nStudents with marks ({students_with_marks}):")
        for student in students_data:
            if student[3] > 0:
                print(f"  {student[1]} {student[2]}: {student[3]} subjects")
    
    # Show students without marks (if any)
    if students_without_marks > 0:
        print(f"\nStudents WITHOUT marks ({students_without_marks}):")
        for student in students_data:
            if student[3] == 0:
                print(f"  {student[1]} {student[2]}")
    
    # Check if there are marks in other periods that might be relevant
    print(f"\nChecking for marks in other periods...")
    cursor.execute("""
        SELECT DISTINCT sm.term, sm.academic_year, s.first_name, s.last_name, COUNT(*) as marks
        FROM student_marks sm
        JOIN students s ON sm.student_id = s.student_id
        WHERE s.school_id = ? AND s.grade_level = 1
            AND NOT (sm.term = ? AND sm.academic_year = ?)
        GROUP BY sm.term, sm.academic_year, s.student_id
        ORDER BY sm.academic_year DESC, sm.term, s.first_name
        LIMIT 10
    """, (nanjati_school_id, term, academic_year))
    
    other_marks = cursor.fetchall()
    if other_marks:
        print("Sample marks from other periods:")
        for mark in other_marks[:5]:
            print(f"  {mark[0]} {mark[1]}: {mark[2]} {mark[3]} ({mark[4]} subjects)")
    else:
        print("No marks found in other periods")
    
    conn.close()
    print(f"\n=== MARKS CHECK COMPLETE ===")

if __name__ == "__main__":
    check_nanjati_marks()