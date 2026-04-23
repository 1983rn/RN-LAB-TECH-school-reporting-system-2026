
import os
import sys
import json
from school_database import SchoolDatabase
from termly_report_generator import TermlyReportGenerator

def verify_position_data():
    db = SchoolDatabase()
    generator = TermlyReportGenerator(db=db)
    
    # Get a student from students table
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT student_id, grade_level, school_id, first_name, last_name FROM students LIMIT 1")
        student = cursor.fetchone()
        
    if not student:
        print("No students found.")
        return
        
    s_id, grade, school_id, fname, lname = student
    term = "Term 1"
    year = "2024-2025" # Assuming this exists or works
    
    print(f"Verifying position data for {fname} {lname} (ID: {s_id}, Grade: {grade}, School: {school_id})")
    
    # Test get_student_position_and_points
    pos_data = db.get_student_position_and_points(s_id, term, year, grade, school_id)
    print(f"Database position_data: {pos_data}")
    
    if pos_data.get('total_students') and pos_data.get('total_students') != '--' and pos_data.get('total_students') != 0:
        print("SUCCESS: total_students is populated by database.")
    else:
        print("DATABASE RETURNED EMPTY total_students. Checking generator fallback...")
        
        # Test the fallback logic in a mock context
        # We'll just call a part of the generator logic if possible, or rely on logs
        # Since I can't easily call the private _add_student_to_story, I'll just check if the counts are non-zero
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM students WHERE grade_level = %s AND school_id = %s", (grade, school_id))
            count = cursor.fetchone()[0]
            print(f"Manual count for Grade {grade}, School {school_id}: {count}")
            
    # Check if get_student_rankings is working
    rankings = db.get_student_rankings(grade, term, year, school_id)
    print(f"Rankings total_students: {rankings.get('total_students')}")

if __name__ == "__main__":
    verify_position_data()
