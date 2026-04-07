#!/usr/bin/env python3
"""
Add Sample Marks for NANJATI Students
This will add marks for students who don't have any marks yet
"""

import sqlite3
import os
import random

def add_sample_marks_for_nanjati():
    """Add sample marks for NANJATI students who don't have marks"""
    
    db_path = "school_reports.db"
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    nanjati_school_id = 2
    term = "Term 1"
    academic_year = "2025-2026"
    form_level = 1
    
    print("=== ADDING SAMPLE MARKS FOR NANJATI STUDENTS ===\n")
    
    # Get students without marks
    cursor.execute("""
        SELECT s.student_id, s.first_name, s.last_name
        FROM students s
        LEFT JOIN student_marks sm ON s.student_id = sm.student_id 
            AND sm.term = ? AND sm.academic_year = ? AND sm.school_id = ?
        WHERE s.school_id = ? AND s.grade_level = ? AND s.status = 'Active'
            AND sm.student_id IS NULL
        ORDER BY s.first_name, s.last_name
    """, (term, academic_year, nanjati_school_id, nanjati_school_id, form_level))
    
    students_without_marks = cursor.fetchall()
    print(f"Students without marks: {len(students_without_marks)}")
    
    if not students_without_marks:
        print("All students already have marks!")
        conn.close()
        return
    
    # Subjects for Form 1
    subjects = [
        'Agriculture', 'Bible Knowledge', 'Biology', 'Chemistry', 
        'Chichewa', 'Computer Studies', 'English', 'Geography', 
        'History', 'Life Skills/SOS', 'Mathematics', 'Physics', 
        'Business Studies', 'Home Economics'
    ]
    
    print(f"Adding marks for {len(students_without_marks)} students...")
    
    for student_id, first_name, last_name in students_without_marks:
        print(f"  Adding marks for {first_name} {last_name}...")
        
        # Generate realistic marks (mix of pass and fail)
        for subject in subjects:
            # Generate marks with some variation
            if subject == 'English':
                # Make English slightly harder
                mark = random.randint(35, 85)
            elif subject in ['Mathematics', 'Physics', 'Chemistry']:
                # Science subjects - varied difficulty
                mark = random.randint(30, 80)
            else:
                # Other subjects
                mark = random.randint(40, 90)
            
            # Calculate grade based on form level
            if mark >= 80:
                grade = 'A'
            elif mark >= 70:
                grade = 'B'
            elif mark >= 60:
                grade = 'C'
            elif mark >= 50:
                grade = 'D'
            else:
                grade = 'F'
            
            # Insert mark
            cursor.execute("""
                INSERT OR REPLACE INTO student_marks 
                (student_id, subject, mark, grade, term, academic_year, form_level, school_id, date_entered)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (student_id, subject, mark, grade, term, academic_year, form_level, nanjati_school_id))
    
    conn.commit()
    
    # Verify the results
    cursor.execute("""
        SELECT COUNT(DISTINCT s.student_id)
        FROM students s
        JOIN student_marks sm ON s.student_id = sm.student_id
        WHERE s.school_id = ? AND s.grade_level = ? AND s.status = 'Active'
            AND sm.term = ? AND sm.academic_year = ? AND sm.school_id = ?
    """, (nanjati_school_id, form_level, term, academic_year, nanjati_school_id))
    
    students_with_marks = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM students 
        WHERE school_id = ? AND grade_level = ? AND status = 'Active'
    """, (nanjati_school_id, form_level))
    
    total_students = cursor.fetchone()[0]
    
    print(f"\nResults:")
    print(f"- Total Form 1 students: {total_students}")
    print(f"- Students with marks: {students_with_marks}")
    print(f"- Added marks for: {len(students_without_marks)} students")
    
    conn.close()
    print("\n=== SAMPLE MARKS ADDED SUCCESSFULLY ===")

if __name__ == "__main__":
    add_sample_marks_for_nanjati()