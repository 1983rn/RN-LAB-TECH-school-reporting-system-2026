#!/usr/bin/env python3

import sqlite3
import os
from termly_report_generator import TermlyReportGenerator
from school_database import SchoolDatabase

def test_enrollment_count_fix():
    """Test that report generation shows correct enrollment count for NANJATI"""
    
    db_path = "school_reports.db"
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        return False
    
    # Initialize components
    db = SchoolDatabase()
    
    # Get NANJATI school info
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT school_id, school_name FROM schools WHERE school_name LIKE '%NANJATI%'")
    school = cursor.fetchone()
    
    if not school:
        print("NANJATI school not found")
        return False
    
    school_id, school_name = school
    print(f"Testing enrollment count for: {school_name} (ID: {school_id})")
    
    # Get actual Form 1 student count
    students = db.get_students_by_grade(1, school_id)
    actual_count = len(students)
    print(f"Actual Form 1 students in database: {actual_count}")
    
    # Test the report generator with school_id
    generator = TermlyReportGenerator(
        school_name="NANJATI CDSS",
        school_address="Test Address",
        school_phone="Test Phone",
        school_email="test@email.com"
    )
    
    # Test pass/fail summary generation with school_id
    try:
        summary = generator.generate_pass_fail_summary(1, 'Term 1', '2024-2025', school_id)
        
        if summary:
            # Extract total students from summary
            lines = summary.split('\\n')
            total_students_line = None
            for line in lines:
                if 'Total Students:' in line:
                    total_students_line = line
                    break
            
            if total_students_line:
                # Extract number from line like "Total Students: 91"
                import re
                match = re.search(r'Total Students: (\\d+)', total_students_line)
                if match:
                    reported_count = int(match.group(1))
                    print(f"Report shows total students: {reported_count}")
                    
                    if reported_count == actual_count:
                        print("SUCCESS: Report shows correct enrollment count!")
                        return True
                    else:
                        print(f"MISMATCH: Report shows {reported_count}, but database has {actual_count}")
                        return False
                else:
                    print("Could not extract student count from report")
                    return False
            else:
                print("Could not find 'Total Students' line in report")
                return False
        else:
            print("No summary generated")
            return False
            
    except Exception as e:
        print(f"Error generating summary: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("Testing Enrollment Count Fix")
    print("=" * 40)
    
    success = test_enrollment_count_fix()
    
    print("\\n" + "=" * 40)
    if success:
        print("TEST PASSED: Enrollment count is now correct!")
        print("The report generation will show the accurate number")
        print("of students (91) for NANJATI Form 1.")
    else:
        print("TEST FAILED: Issue still exists")
        print("The report may still show incorrect enrollment numbers.")