
from school_database import SchoolDatabase
import os

def check_counts():
    db = SchoolDatabase()
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check schools
            cursor.execute("SELECT school_id, school_name FROM schools")
            schools = cursor.fetchall()
            print(f"Schools: {schools}")
            
            for school_id, name in schools:
                print(f"\nChecking School: {name} (ID: {school_id})")
                
                # Check student counts by grade
                cursor.execute("SELECT grade_level, COUNT(*) FROM students WHERE school_id = %s GROUP BY grade_level", (school_id,))
                grade_counts = cursor.fetchall()
                print(f"  Student counts by grade: {grade_counts}")
                
                # Check active student counts by grade
                cursor.execute("SELECT grade_level, COUNT(*) FROM students WHERE school_id = %s AND (status = 'Active' OR status IS NULL OR status = '') GROUP BY grade_level", (school_id,))
                active_counts = cursor.fetchall()
                print(f"  Active student counts by grade: {active_counts}")
                
                for grade, count in active_counts:
                    # Test get_student_rankings
                    rankings = db.get_student_rankings(grade, "Term 1", "2024-2025", school_id)
                    print(f"  Grade {grade} rankings summary: total_students={rankings.get('total_students')}, students_with_marks={rankings.get('students_with_marks')}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_counts()
