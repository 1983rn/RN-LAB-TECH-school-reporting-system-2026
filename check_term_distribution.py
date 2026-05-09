import os
import sys
from school_database import SchoolDatabase

def check_distribution():
    db = SchoolDatabase()
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check 2025-2026 marks distribution across schools
            cursor.execute("""
                SELECT school_id, term, COUNT(*) 
                FROM student_marks 
                WHERE academic_year = '2025-2026'
                GROUP BY school_id, term
                ORDER BY school_id, term
            """)
            
            results = cursor.fetchall()
            print("2025-2026 Marks Distribution:")
            print("School ID | Term | Count")
            print("-" * 30)
            for school_id, term, count in results:
                print(f"{school_id:9} | {term:5} | {count:6}")
            
            # Check if any school has marks in BOTH Term 1 and Term 2 for 2025-2026
            cursor.execute("""
                SELECT school_id FROM student_marks 
                WHERE academic_year = '2025-2026' AND term = 'Term 1'
                INTERSECT
                SELECT school_id FROM student_marks 
                WHERE academic_year = '2025-2026' AND term = 'Term 2'
            """)
            
            conflicted_schools = [row[0] for row in cursor.fetchall()]
            if conflicted_schools:
                print("\nSchools with marks in BOTH Term 1 and Term 2 for 2025-2026:")
                for sid in conflicted_schools:
                    print(f"School ID: {sid}")
            else:
                print("\nNo schools have overlapping marks in Term 1 and Term 2 for 2025-2026.")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_distribution()
