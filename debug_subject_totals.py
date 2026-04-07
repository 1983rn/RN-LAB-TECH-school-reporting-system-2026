#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from school_database import SchoolDatabase

def debug_subject_totals():
    """Debug total students count per subject"""
    db = SchoolDatabase()
    
    print("=== DEBUGGING SUBJECT TOTALS ===\n")
    
    # Test for Form 1, Term 3 2025-2026
    form_level = 1
    term = "Term 3"
    academic_year = "2025-2026"
    
    # Get all students in form
    students = db.get_students_by_grade(form_level)
    print(f"Total enrolled students in Form {form_level}: {len(students)}")
    
    # Check each subject for actual marks count
    subjects = ['English', 'Mathematics', 'Biology', 'Geography', 'History', 'Agriculture']
    
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    for subject in subjects:
        print(f"\n--- {subject} ---")
        
        # Count students with marks for this subject
        if hasattr(db, 'db_path') and 'school_reports' in db.db_path:
            # Multi-school database
            cursor.execute("""
                SELECT COUNT(DISTINCT sm.student_id) as count
                FROM student_marks sm
                JOIN students s ON sm.student_id = s.student_id
                WHERE s.grade_level = ? AND sm.subject = ? AND sm.term = ? AND sm.academic_year = ? 
                    AND s.status = 'Active' AND sm.mark IS NOT NULL
            """, (form_level, subject, term, academic_year))
        else:
            # Single school database
            cursor.execute("""
                SELECT COUNT(DISTINCT sm.student_id) as count
                FROM student_marks sm
                JOIN students s ON sm.student_id = s.student_id
                WHERE s.grade_level = ? AND sm.subject = ? AND sm.term = ? AND sm.academic_year = ? 
                    AND s.status = 'Active' AND sm.mark IS NOT NULL
            """, (form_level, subject, term, academic_year))
        
        result = cursor.fetchone()
        students_with_marks = result[0] if result else 0
        
        print(f"Students with marks: {students_with_marks}")
        
        # Test function result
        if students:
            test_student_id = students[0]['student_id']
            position = db.get_subject_position(test_student_id, subject, term, academic_year, form_level)
            print(f"Function result: {position}")
            print(f"Expected format: position/{students_with_marks}")
    
    conn.close()

if __name__ == "__main__":
    debug_subject_totals()
