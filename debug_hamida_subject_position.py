#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from school_database import SchoolDatabase

def debug_hamida_subject_position():
    """Debug subject position for HAMIDA KAIWE"""
    db = SchoolDatabase()
    
    print("=== DEBUGGING HAMIDA SUBJECT POSITION ===\n")
    
    # Test with HAMIDA KAIWE in Form 1, Term 3 2025-2026
    student_id = 176
    subject = "English"
    term = "Term 3"
    academic_year = "2025-2026"
    form_level = 1
    
    print(f"Testing: Student {student_id}, Subject: {subject}, Term: {term}, Year: {academic_year}")
    print("-" * 50)
    
    # Get all students in form
    all_students = db.get_students_by_grade(form_level)
    print(f"Total students in Form {form_level}: {len(all_students)}")
    
    # Get marks for this specific subject
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT s.student_id, s.first_name, s.last_name, sm.mark
        FROM students s
        LEFT JOIN student_marks sm ON s.student_id = sm.student_id 
            AND sm.subject = ? AND sm.term = ? AND sm.academic_year = ?
        WHERE s.grade_level = ? AND s.status = 'Active'
        ORDER BY sm.mark DESC
    """, (subject, term, academic_year, form_level))
    
    results = cursor.fetchall()
    print(f"\nSubject marks for {subject}:")
    print("ID\tName\t\tMark")
    print("-" * 40)
    for result in results:
        sid, fname, lname, mark = result
        mark_str = str(mark) if mark is not None else "NULL"
        print(f"{sid}\t{fname} {lname}\t{mark_str}")
    
    print(f"\nTotal results: {len(results)}")
    
    # Test the function
    position = db.get_subject_position(student_id, subject, term, academic_year, form_level)
    print(f"\nFunction result for student {student_id}: {position}")
    
    conn.close()

if __name__ == "__main__":
    debug_hamida_subject_position()
