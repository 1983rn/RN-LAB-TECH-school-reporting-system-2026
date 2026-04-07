#!/usr/bin/env python3
"""
Debug Patricia Bwanali's grade and pass/fail status for Form 1
"""
from school_database import SchoolDatabase

def check_patricia_status():
    db = SchoolDatabase()
    # Find Patricia's student_id in Form 1
    students = db.get_students_by_grade(1)
    patricia = None
    for s in students:
        if s['first_name'].lower() == 'patricia' and 'bwanali' in s['last_name'].lower():
            patricia = s
            break
    if not patricia:
        print("Patricia Bwanali (Form 1) not found.")
        return
    print(f"Patricia Bwanali found: ID={patricia['student_id']}, Grade Level={patricia['grade_level']}")
    # Get her marks for the current academic year and term
    marks = db.get_student_marks(patricia['student_id'], 'Term 1', '2024-2025')
    print("\nSubject Grades:")
    passed_subjects = 0
    for m in marks.values():
        mark = m['mark']
        status = 'PASS' if mark >= 50 else 'FAIL'
        print(f"{mark:5.1f} {status}")
        if mark >= 50:
            passed_subjects += 1
    print(f"\nTotal subjects passed (>=50): {passed_subjects}")
    # Get report card data
    report = db.generate_termly_report_card(patricia['student_id'], 'Term 1', '2024-2025')
    stats = report['overall_statistics']
    print(f"\nSystem Pass/Fail: {stats['overall_status']}")
    print(f"System Grade: {stats['overall_grade']}")
    print(f"System Average: {stats['overall_average']}")
    print(f"System Passed Subjects: {stats['passed_subjects']}")
    print(f"System English Passed: {stats['english_passed']}")
    print(f"System English %: {stats['english_percentage']}")
    print(f"System Status Reason: {stats['status_reason']}")

if __name__ == "__main__":
    check_patricia_status()
