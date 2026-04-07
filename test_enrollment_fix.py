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
        summary = generator.generate_pass_fail_summary(1, 'Term 1', '2024-2025', school_id)\n        \n        if summary:\n            # Extract total students from summary\n            lines = summary.split('\\n')\n            total_students_line = None\n            for line in lines:\n                if 'Total Students:' in line:\n                    total_students_line = line\n                    break\n            \n            if total_students_line:\n                # Extract number from line like \"Total Students: 91\"\n                import re\n                match = re.search(r'Total Students: (\\d+)', total_students_line)\n                if match:\n                    reported_count = int(match.group(1))\n                    print(f\"Report shows total students: {reported_count}\")\n                    \n                    if reported_count == actual_count:\n                        print(\"✅ SUCCESS: Report shows correct enrollment count!\")\n                        return True\n                    else:\n                        print(f\"❌ MISMATCH: Report shows {reported_count}, but database has {actual_count}\")\n                        return False\n                else:\n                    print(\"❌ Could not extract student count from report\")\n                    return False\n            else:\n                print(\"❌ Could not find 'Total Students' line in report\")\n                return False\n        else:\n            print(\"❌ No summary generated\")\n            return False\n            \n    except Exception as e:\n        print(f\"❌ Error generating summary: {e}\")\n        import traceback\n        traceback.print_exc()\n        return False\n    \n    finally:\n        conn.close()\n\nif __name__ == \"__main__\":\n    print(\"Testing Enrollment Count Fix\")\n    print(\"=\" * 40)\n    \n    success = test_enrollment_count_fix()\n    \n    print(\"\\n\" + \"=\" * 40)\n    if success:\n        print(\"✅ TEST PASSED: Enrollment count is now correct!\")\n        print(\"The report generation will show the accurate number\")\n        print(\"of students (91) for NANJATI Form 1.\")\n    else:\n        print(\"❌ TEST FAILED: Issue still exists\")\n        print(\"The report may still show incorrect enrollment numbers.\")