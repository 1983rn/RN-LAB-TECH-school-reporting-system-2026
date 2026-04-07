#!/usr/bin/env python3
"""
Debug script to check Margret Muhaliwa's pass/fail status
"""

import sys
sys.path.append('.')
from school_database import SchoolDatabase

def debug_margret():
    db = SchoolDatabase()
    
    # Find Margret Muhaliwa
    students = db.get_students_by_grade(3)
    margret = None
    for student in students:
        if 'Margret' in student['first_name'] and 'Muhaliwa' in student['last_name']:
            margret = student
            break
    
    if margret:
        print(f'Found student: {margret["first_name"]} {margret["last_name"]} (ID: {margret["student_id"]})')
        
        # Get her marks
        marks = db.get_student_marks(margret['student_id'], 'Term 1', '2024-2025')
        print(f'Marks: {marks}')
        
        # Check each subject
        print("\nSubject breakdown:")
        for subject, data in marks.items():
            passed = "PASS" if data['mark'] >= 50 else "FAIL"
            print(f"  {subject}: {data['mark']}% ({data['grade']}) - {passed}")
        
        # Check pass/fail calculation
        passed_subjects = sum(1 for data in marks.values() if data['mark'] >= 50)
        english_mark = marks.get('English', {}).get('mark', 0)
        english_passed = db.is_english_passed(english_mark, 3)
        overall_status = db.determine_pass_fail_status(passed_subjects, english_passed)
        
        print(f'\nCalculation:')
        print(f'  Total subjects: {len(marks)}')
        print(f'  Passed subjects (>=50%): {passed_subjects}')
        print(f'  English mark: {english_mark}%')
        print(f'  English passed (>=40% for Form 3): {english_passed}')
        print(f'  Overall status: {overall_status}')
        
        # Check criteria
        print(f'\nPass criteria check:')
        print(f'  Need 6+ subjects passed: {passed_subjects >= 6} ({passed_subjects}/6)')
        print(f'  Need English passed: {english_passed}')
        print(f'  Should PASS: {passed_subjects >= 6 and english_passed}')
        
    else:
        print('Margret Muhaliwa not found in Form 3')
        print('Available Form 3 students:')
        for student in students:
            print(f"  {student['first_name']} {student['last_name']}")

if __name__ == "__main__":
    debug_margret()
