#!/usr/bin/env python3

import sqlite3
import os
from termly_report_generator import TermlyReportGenerator

def test_nanjati_report_generation():
    """Test that report generation works with the cleaned up NANJATI data"""
    
    db_path = "school_reports.db"
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get NANJATI school info
    cursor.execute("SELECT school_id, school_name FROM schools WHERE school_name LIKE '%NANJATI%'")
    school = cursor.fetchone()
    
    if not school:
        print("NANJATI school not found")
        return
    
    school_id, school_name = school
    print(f"Testing report generation for: {school_name} (ID: {school_id})")
    
    # Get Form 1 students after cleanup
    cursor.execute("""
        SELECT student_id, first_name, last_name
        FROM students 
        WHERE school_id = ? AND grade_level = 1
        ORDER BY first_name, last_name
        LIMIT 5
    """, (school_id,))
    
    students = cursor.fetchall()
    print(f"Found {len(students)} Form 1 students (showing first 5):")
    
    for student in students:
        student_id, first_name, last_name = student
        print(f"  {first_name} {last_name} (ID: {student_id})")
    
    if students:
        # Test report generation for first student
        test_student = students[0]
        student_id, first_name, last_name = test_student
        
        print(f"\nTesting report generation for: {first_name} {last_name}")
        
        # Check if student has marks
        cursor.execute("""
            SELECT COUNT(*) FROM student_marks 
            WHERE student_id = ?
        """, (student_id,))
        
        marks_count = cursor.fetchone()[0]
        print(f"Student has {marks_count} mark records")
        
        if marks_count > 0:
            # Get available terms and years for this student
            cursor.execute("""
                SELECT DISTINCT term, academic_year 
                FROM student_marks 
                WHERE student_id = ?
                ORDER BY academic_year DESC, term
            """, (student_id,))
            
            periods = cursor.fetchall()
            print(f"Available periods: {periods}")
            
            if periods:
                term, academic_year = periods[0]
                print(f"Generating report for {term} {academic_year}...")
                
                try:
                    # Initialize report generator
                    generator = TermlyReportGenerator(
                        school_name="NANJATI CDSS",
                        school_address="Test Address",
                        school_phone="Test Phone",
                        school_email="test@email.com"
                    )
                    
                    # Generate report
                    report = generator.generate_progress_report(student_id, term, academic_year, school_id)
                    
                    if report:
                        print("✅ Report generated successfully!")
                        print("Report preview (first 500 characters):")
                        print("-" * 50)
                        print(report[:500] + "..." if len(report) > 500 else report)
                        print("-" * 50)
                        return True
                    else:
                        print("❌ Report generation returned empty result")
                        return False
                        
                except Exception as e:
                    print(f"❌ Error generating report: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
            else:
                print("No periods with marks found")
        else:
            print("No marks found for this student")
    else:
        print("No students found")
    
    conn.close()
    return False

if __name__ == "__main__":
    test_nanjati_report_generation()