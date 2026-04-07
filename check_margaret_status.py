#!/usr/bin/env python3
"""
Check Margaret Muhaliwa's grades and pass/fail status for Form 3
"""
from school_database import SchoolDatabase

def check_margaret_status():
    db = SchoolDatabase()
    # Find Margaret's student_id in Form 3
    students = db.get_students_by_grade(3)
    margaret = None
    for s in students:
        if s['first_name'].lower() == 'margaret' and 'muhaliwa' in s['last_name'].lower():
            margaret = s
            break
    if not margaret:
        print("Margaret Muhaliwa (Form 3) not found.")
        return
    print(f"Margaret Muhaliwa found: ID={margaret['student_id']}, Grade Level={margaret['grade_level']}")
    # Get her marks for the current academic year and term
    marks = db.get_student_marks(margaret['student_id'], 'Term 1', '2024-2025')
    print("\nSubject Grades:")
    passed_subjects = 0
    english_mark = None
    for m in marks:
        subject = m['subject_name']
        mark = m['percentage']
        status = 'PASS' if mark >= 40 else 'FAIL'
        print(f"{subject:20} {mark:5.1f} {status}")
        if subject.lower() == 'english':
            english_mark = mark
        if mark >= 40:
            passed_subjects += 1
    if english_mark is None:
        print("English mark not found!")
        return
    english_passed = english_mark >= 40
    print(f"\nTotal subjects passed (>=40): {passed_subjects}")
    print(f"English mark: {english_mark} ({'PASS' if english_passed else 'FAIL'})")
    # Determine overall status
    if passed_subjects >= 6 and english_passed:
        print("\nFINAL REMARK: PASS")
    else:
        print("\nFINAL REMARK: FAIL")

if __name__ == "__main__":
    check_margaret_status()
