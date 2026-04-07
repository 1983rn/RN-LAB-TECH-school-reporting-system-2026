#!/usr/bin/env python3
"""
Test the grade fix for Forms 1&2 - failed students must have grade F
"""

from school_database import SchoolDatabase

def test_grade_fix():
    db = SchoolDatabase()
    
    print("=== Testing Grade Fix for Forms 1&2 ===\n")
    
    # Test Form 1 students
    form1_students = db.get_students_by_grade(1)
    print(f"Testing {len(form1_students)} Form 1 students...")
    
    failed_with_wrong_grade = 0
    passed_with_f_grade = 0
    
    for student in form1_students[:10]:  # Test first 10 students
        student_id = student['student_id']
        report = db.generate_termly_report_card(student_id, 'Term 3', '2024-2025')
        
        overall_status = report['overall_statistics']['overall_status']
        overall_grade = report['overall_statistics']['overall_grade']
        
        print(f"{student['first_name']} {student['last_name']}: Status={overall_status}, Grade={overall_grade}")
        
        # Check the rule: Failed students MUST have grade F
        if overall_status == 'FAIL' and overall_grade != 'F':
            failed_with_wrong_grade += 1
            print(f"  ❌ ERROR: Failed student has grade {overall_grade} instead of F")
        
        # Check: Passed students should NOT have grade F
        if overall_status == 'PASS' and overall_grade == 'F':
            passed_with_f_grade += 1
            print(f"  ❌ ERROR: Passed student has grade F")
        
        if overall_status == 'FAIL' and overall_grade == 'F':
            print(f"  ✅ CORRECT: Failed student has grade F")
        elif overall_status == 'PASS' and overall_grade != 'F':
            print(f"  ✅ CORRECT: Passed student has grade {overall_grade}")
    
    print(f"\n=== SUMMARY ===")
    print(f"Failed students with wrong grade: {failed_with_wrong_grade}")
    print(f"Passed students with F grade: {passed_with_f_grade}")
    
    if failed_with_wrong_grade == 0 and passed_with_f_grade == 0:
        print("✅ ALL TESTS PASSED - Grade rule is working correctly!")
    else:
        print("❌ TESTS FAILED - Grade rule needs fixing")

if __name__ == "__main__":
    test_grade_fix()