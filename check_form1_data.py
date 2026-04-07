#!/usr/bin/env python3
"""
Check Form 1 student count and marks for NANJATI
"""

from school_database import SchoolDatabase

def check_form1_data():
    db = SchoolDatabase()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Find NANJATI school
            cursor.execute("SELECT school_id FROM schools WHERE school_name LIKE '%NANJATI%'")
            school_id = cursor.fetchone()[0]
            
            # Count total Form 1 students
            cursor.execute("""
                SELECT COUNT(*) FROM students 
                WHERE school_id = ? AND grade_level = 1 AND status = 'Active'
            """, (school_id,))
            total_students = cursor.fetchone()[0]
            
            # Count Form 1 students with marks in Term 1 2025-2026
            cursor.execute("""
                SELECT COUNT(DISTINCT s.student_id) 
                FROM students s
                JOIN student_marks sm ON s.student_id = sm.student_id
                WHERE s.school_id = ? AND s.grade_level = 1 
                AND sm.term = 'Term 1' AND sm.academic_year = '2025-2026'
            """, (school_id,))
            students_with_marks = cursor.fetchone()[0]
            
            print(f"Total Form 1 students: {total_students}")
            print(f"Form 1 students with marks: {students_with_marks}")
            
            # Check if positioning method is using correct filter
            rankings = db.get_student_rankings(1, 'Term 1', '2025-2026', school_id)
            print(f"Students in rankings: {rankings['total_students']}")
            print(f"Students with marks in rankings: {rankings['students_with_marks']}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_form1_data()