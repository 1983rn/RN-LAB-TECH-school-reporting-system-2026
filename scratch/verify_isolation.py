
import os
import psycopg2
from school_database import SchoolDatabase
from performance_analyzer import PerformanceAnalyzer
from termly_report_generator import TermlyReportGenerator

def test_isolation():
    db = SchoolDatabase()
    analyzer = PerformanceAnalyzer()
    generator = TermlyReportGenerator()
    
    # Create two test schools
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # School A
        cursor.execute("INSERT INTO schools (school_name, username, password_hash) VALUES (%s, %s, %s) ON CONFLICT (username) DO UPDATE SET school_name = EXCLUDED.school_name RETURNING school_id", 
                       ("School A", "school_a", "hash"))
        school_a_id = cursor.fetchone()[0]
        
        # School B
        cursor.execute("INSERT INTO schools (school_name, username, password_hash) VALUES (%s, %s, %s) ON CONFLICT (username) DO UPDATE SET school_name = EXCLUDED.school_name RETURNING school_id", 
                       ("School B", "school_b", "hash"))
        school_b_id = cursor.fetchone()[0]
        
        # Clear existing students for these schools to have a clean test
        cursor.execute("DELETE FROM students WHERE school_id IN (%s, %s)", (school_a_id, school_b_id))
        
        # Add student to School A
        cursor.execute("INSERT INTO students (first_name, last_name, grade_level, school_id, student_number) VALUES (%s, %s, %s, %s, %s) RETURNING student_id",
                       ("Alice", "Smith", 1, school_a_id, "A001"))
        alice_id = cursor.fetchone()[0]
        
        # Add mark for Alice
        cursor.execute("INSERT INTO student_marks (student_id, subject, mark, grade, term, academic_year, form_level, school_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                       (alice_id, "English", 85, "A", "Term 1", "2024-2025", 1, school_a_id))
        
        conn.commit()

    print(f"Test data setup: Alice (ID: {alice_id}) in School A (ID: {school_a_id})")

    # Verify PerformanceAnalyzer isolation
    print("\nVerifying PerformanceAnalyzer isolation...")
    
    # Query School A
    rankings_a = analyzer.get_best_performing_students_by_class(1, "Term 1", "2024-2025", school_id=school_a_id)
    print(f"School A rankings count: {len(rankings_a['top_students']) if rankings_a else 0}")
    
    # Query School B
    rankings_b = analyzer.get_best_performing_students_by_class(1, "Term 1", "2024-2025", school_id=school_b_id)
    print(f"School B rankings count: {len(rankings_b['top_students']) if rankings_b else 0}")
    
    if rankings_b and len(rankings_b['top_students']) > 0:
        print("FAILED: School B sees School A data!")
    else:
        print("SUCCESS: School B data is isolated.")

    # Verify TermlyReportGenerator isolation
    print("\nVerifying TermlyReportGenerator isolation...")
    
    # Alice's report in School A
    report_a = generator.generate_progress_report(alice_id, "Term 1", "2024-2025", school_id=school_a_id)
    if report_a:
        print("SUCCESS: School A can generate Alice's report.")
    else:
        print("FAILED: School A cannot generate its own student's report.")
        
    # Alice's report in School B (should fail)
    report_b = generator.generate_progress_report(alice_id, "Term 1", "2024-2025", school_id=school_b_id)
    if report_b:
        print("FAILED: School B can generate Alice's report!")
    else:
        print("SUCCESS: School B cannot see School A's student.")

    # Verify School Settings isolation
    print("\nVerifying School Settings isolation...")
    settings_a = db.get_school_settings(school_a_id)
    print(f"School A Name: '{settings_a.get('school_name')}'")
    
    settings_b = db.get_school_settings(school_b_id)
    print(f"School B Name: '{settings_b.get('school_name')}'")
    
    if settings_b.get('school_name') == "School A":
         print("FAILED: School B settings leaked School A name!")
    else:
         print("SUCCESS: Settings are isolated.")

if __name__ == "__main__":
    test_isolation()
