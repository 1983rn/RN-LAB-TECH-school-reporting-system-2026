#!/usr/bin/env python3

import sqlite3
import os

def check_nanjati_form1_details():
    """Check detailed Form 1 data for NANJATI CDSS"""
    db_path = "school_reports.db"
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get NANJATI school info
    cursor.execute("SELECT school_id, school_name, username FROM schools WHERE school_name LIKE '%NANJATI%'")
    school = cursor.fetchone()
    
    if not school:
        print("NANJATI school not found")
        return
    
    school_id, school_name, username = school
    print(f"School: {school_name} (ID: {school_id}, Username: {username})")
    print("=" * 60)
    
    # Get Form 1 students
    cursor.execute("""
        SELECT student_id, first_name, last_name, status
        FROM students 
        WHERE school_id = ? AND grade_level = 1
        ORDER BY first_name, last_name
    """, (school_id,))
    
    students = cursor.fetchall()
    print(f"\nForm 1 Students ({len(students)} total):")
    print("-" * 40)
    
    for i, student in enumerate(students, 1):
        student_id, first_name, last_name, status = student
        print(f"{i:2d}. {first_name} {last_name} (ID: {student_id}, Status: {status})")
    
    if not students:
        print("No Form 1 students found")
        return
    
    # Check available terms and years for marks
    cursor.execute("""
        SELECT DISTINCT sm.term, sm.academic_year, COUNT(*) as mark_count
        FROM student_marks sm
        JOIN students s ON sm.student_id = s.student_id
        WHERE s.school_id = ? AND s.grade_level = 1
        GROUP BY sm.term, sm.academic_year
        ORDER BY sm.academic_year DESC, sm.term
    """, (school_id,))
    
    periods = cursor.fetchall()
    print(f"\nAvailable Mark Periods:")
    print("-" * 30)
    
    if periods:
        for period in periods:
            term, year, count = period
            print(f"  {term} {year}: {count} marks")
        
        # Show marks for the most recent period
        latest_term, latest_year = periods[0][0], periods[0][1]
        print(f"\nMarks for {latest_term} {latest_year}:")
        print("=" * 50)
        
        cursor.execute("""
            SELECT s.first_name, s.last_name, sm.subject, sm.mark
            FROM student_marks sm
            JOIN students s ON sm.student_id = s.student_id
            WHERE s.school_id = ? AND s.grade_level = 1 
                AND sm.term = ? AND sm.academic_year = ?
            ORDER BY s.first_name, s.last_name, sm.subject
        """, (school_id, latest_term, latest_year))
        
        marks = cursor.fetchall()
        
        if marks:
            current_student = None
            for mark in marks:
                first_name, last_name, subject, mark_value = mark
                student_name = f"{first_name} {last_name}"
                
                if student_name != current_student:
                    if current_student is not None:
                        print()  # Add blank line between students
                    print(f"\n{student_name}:")
                    current_student = student_name
                
                print(f"  {subject}: {mark_value}")
        else:
            print("No marks found for this period")
    else:
        print("No marks found for any period")
    
    conn.close()

if __name__ == "__main__":
    check_nanjati_form1_details()