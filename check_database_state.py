#!/usr/bin/env python3
"""
Check current database state
"""

import sqlite3
import os

def check_database_state():
    db_path = "school_reports.db"
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return
    
    print("=== DATABASE STATE CHECK ===\n")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check schools
        cursor.execute("SELECT COUNT(*) FROM schools")
        school_count = cursor.fetchone()[0]
        print(f"Schools: {school_count}")
        
        if school_count > 0:
            cursor.execute("SELECT school_id, school_name, username FROM schools")
            schools = cursor.fetchall()
            for school_id, name, username in schools:
                print(f"  - {name} (ID: {school_id}, Username: {username})")
        
        # Check students
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]
        print(f"\nStudents: {student_count}")
        
        if student_count > 0:
            cursor.execute("""
                SELECT s.school_id, sch.school_name, s.grade_level, COUNT(*) 
                FROM students s
                LEFT JOIN schools sch ON s.school_id = sch.school_id
                GROUP BY s.school_id, s.grade_level
                ORDER BY s.school_id, s.grade_level
            """)
            student_groups = cursor.fetchall()
            for school_id, school_name, grade_level, count in student_groups:
                school_display = school_name if school_name else f"School ID {school_id}"
                print(f"  - {school_display} Form {grade_level}: {count} students")
        
        # Check marks
        cursor.execute("SELECT COUNT(*) FROM student_marks")
        marks_count = cursor.fetchone()[0]
        print(f"\nMarks: {marks_count}")
        
        if marks_count > 0:
            cursor.execute("""
                SELECT sm.term, sm.academic_year, COUNT(*) 
                FROM student_marks sm
                GROUP BY sm.term, sm.academic_year
                ORDER BY sm.academic_year, sm.term
            """)
            marks_groups = cursor.fetchall()
            for term, year, count in marks_groups:
                print(f"  - {term} {year}: {count} marks")
        
        # Check Term 3 2024-2025 specifically
        cursor.execute("""
            SELECT COUNT(*) FROM student_marks 
            WHERE term = 'Term 3' AND academic_year = '2024-2025'
        """)
        term3_count = cursor.fetchone()[0]
        print(f"\nTerm 3 2024-2025 marks: {term3_count}")
        
        conn.close()
        
        print("\n=== RECOMMENDATIONS ===")
        if school_count == 0:
            print("🔧 No schools found. Run restore_nanjati_term3_data.py to add Nanjati CDSS")
        elif term3_count == 0:
            print("🔧 No Term 3 marks found. Run restore_nanjati_term3_data.py to restore data")
        else:
            print("✅ Database appears to have data. Check if Nanjati CDSS needs restoration.")
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_database_state()