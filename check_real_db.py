#!/usr/bin/env python3

import sqlite3
import os

def check_actual_database():
    """Check the actual database file in data directory"""
    
    # Check both possible locations
    db_paths = [
        "data/school_reports.db",
        "school_reports.db"
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"Found database: {db_path}")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check NANJATI data
            cursor.execute("""
                SELECT DISTINCT sm.term, sm.academic_year, COUNT(DISTINCT s.student_id) as students, COUNT(*) as marks
                FROM student_marks sm
                JOIN students s ON sm.student_id = s.student_id
                WHERE s.school_id = 2 AND s.grade_level = 1
                GROUP BY sm.term, sm.academic_year
                ORDER BY sm.academic_year DESC, sm.term
            """)
            
            periods = cursor.fetchall()
            print(f"NANJATI Form 1 marks by period:")
            for period in periods:
                print(f"  {period[0]} {period[1]}: {period[2]} students, {period[3]} marks")
            
            conn.close()
            break
    else:
        print("No database found")

if __name__ == "__main__":
    check_actual_database()