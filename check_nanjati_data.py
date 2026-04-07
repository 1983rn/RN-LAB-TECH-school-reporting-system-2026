#!/usr/bin/env python3

import sqlite3
import os

def check_nanjati_data():
    """Check NANJATI COMMUNITY DAY SECONDARY SCHOOL data"""
    db_path = "school_reports.db"
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check schools table
    cursor.execute("SELECT school_id, school_name, username FROM schools WHERE school_name LIKE '%NANJATI%' OR username LIKE '%NANJATI%'")
    schools = cursor.fetchall()
    print("NANJATI Schools:")
    for school in schools:
        print(f"  ID: {school[0]}, Name: {school[1]}, Username: {school[2]}")
    
    if not schools:
        print("No NANJATI school found in schools table")
        # Check if there are any students with NANJATI-like names
        cursor.execute("SELECT DISTINCT school_id FROM students WHERE school_id IS NOT NULL")
        school_ids = cursor.fetchall()
        print(f"Available school_ids: {[s[0] for s in school_ids]}")
        
        # Let's check Form 1 students to see if we can identify NANJATI students
        cursor.execute("""
            SELECT student_id, first_name, last_name, school_id 
            FROM students 
            WHERE grade_level = 1 AND status = 'Active'
            ORDER BY first_name, last_name
        """)
        form1_students = cursor.fetchall()
        print(f"\nForm 1 students ({len(form1_students)} total):")
        
        # List of NANJATI students from the user's message
        nanjati_names = [
            "AARON MALACK", "AGATHAR CHISI", "ALFRED KAITANDE", "ALICE BANDA", 
            "ANASTANZIA DAMIANO", "ANNIE FRANCIS", "BEATRICE SUMBULETA", "BESTER PHIRI",
            "BETRICE BALALA", "BLESSINGS DEKESI", "BRANDINA MWANGONDE", "BRENDA KALUMBI",
            "BRIGHT THASO", "CATHRINE KANDAYA", "CATHRINE MANYOWA", "CHARITY PHIRI"
        ]
        
        found_students = []
        for student in form1_students:
            student_name = f"{student[1]} {student[2]}".upper()
            if any(name in student_name or student_name in name for name in nanjati_names):
                found_students.append(student)
                print(f"  FOUND: ID {student[0]}, {student[1]} {student[2]}, School: {student[3]}")
        
        if found_students:
            # Get the school_id of NANJATI students
            nanjati_school_id = found_students[0][3]
            print(f"\nNANJATI school_id appears to be: {nanjati_school_id}")
            
            # Check marks for these students
            cursor.execute("""
                SELECT COUNT(*) FROM student_marks sm
                JOIN students s ON sm.student_id = s.student_id
                WHERE s.school_id = ? AND s.grade_level = 1
            """, (nanjati_school_id,))
            marks_count = cursor.fetchone()[0]
            print(f"Marks for NANJATI Form 1 students: {marks_count}")
            
            # Check specific terms and years
            cursor.execute("""
                SELECT DISTINCT sm.term, sm.academic_year, COUNT(*) as mark_count
                FROM student_marks sm
                JOIN students s ON sm.student_id = s.student_id
                WHERE s.school_id = ? AND s.grade_level = 1
                GROUP BY sm.term, sm.academic_year
                ORDER BY sm.academic_year DESC, sm.term
            """, (nanjati_school_id,))
            periods = cursor.fetchall()
            print("\nAvailable periods for NANJATI Form 1:")
            for period in periods:
                print(f"  {period[0]} {period[1]}: {period[2]} marks")
    
    conn.close()

if __name__ == "__main__":
    check_nanjati_data()