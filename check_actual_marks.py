#!/usr/bin/env python3

import sqlite3
import os

def check_actual_marks():
    """Check what term/year combinations actually have marks"""
    db_path = "data/school_reports.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== ACTUAL MARKS IN DATABASE ===\n")
    
    # Check all term/year combinations with marks
    cursor.execute("""
        SELECT term, academic_year, COUNT(*) as mark_count
        FROM student_marks
        GROUP BY term, academic_year
        ORDER BY academic_year, term
    """)
    
    combinations = cursor.fetchall()
    print("Term/Year combinations with marks:")
    print("Term\tYear\tCount")
    print("-" * 30)
    for term, year, count in combinations:
        print(f"{term}\t{year}\t{count}")
    
    # Check specific student's marks
    print(f"\nMarks for student 166 (ALFRED MTUMBE):")
    cursor.execute("""
        SELECT subject, term, academic_year, mark
        FROM student_marks
        WHERE student_id = 166
        ORDER BY academic_year, term, subject
    """)
    
    marks = cursor.fetchall()
    print("Subject\tTerm\tYear\tMark")
    print("-" * 50)
    for subject, term, year, mark in marks:
        print(f"{subject}\t{term}\t{year}\t{mark}")
    
    conn.close()

if __name__ == "__main__":
    check_actual_marks()
