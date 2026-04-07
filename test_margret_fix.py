#!/usr/bin/env python3
"""
Test script to verify Margret Muhaliwa's pass/fail status after fixes
"""

import sys
import os
sys.path.append('.')

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from school_database import SchoolDatabase
    
    def test_margret_status():
        db = SchoolDatabase()
        
        # Test specific student - Margret Muhaliwa (ID 115)
        student_id = 115
        
        print(f"=== Testing Student ID {student_id} ===")
        
        # Get student by ID
        student = db.get_student_by_id(student_id)
        if not student:
            print(f"Student ID {student_id} not found")
            return
            
        print(f"Student: {student['first_name']} {student['last_name']}")
        print(f"Form Level: {student['grade_level']}")
        
        # Get marks for Term 3, 2024-2025 (most recent with data)
        marks = db.get_student_marks(115, 'Term 3', '2024-2025')
        print(f"\nMarks for Term 3, 2024-2025:")
        
        total_subjects = len(marks)
        passed_subjects_40 = 0
        passed_subjects_50 = 0
        english_mark = 0
        
        for subject, data in marks.items():
            mark = data['mark']
            grade = data['grade']
            status_40 = "PASS" if mark >= 40 else "FAIL"
            status_50 = "PASS" if mark >= 50 else "FAIL"
            
            print(f"  {subject}: {mark}% (Grade {grade}) - 40+ threshold: {status_40}, 50+ threshold: {status_50}")
            
            if mark >= 40:
                passed_subjects_40 += 1
            if mark >= 50:
                passed_subjects_50 += 1
                
            if subject == 'English':
                english_mark = mark
        
        # Test pass/fail logic
        form_level = student['grade_level']
        english_passed = db.is_english_passed(english_mark, form_level)
        
        # Use correct threshold for form level
        if form_level in [1, 2]:
            passed_subjects = passed_subjects_50
            threshold_text = "50+"
        else:
            passed_subjects = passed_subjects_40
            threshold_text = "40+"
            
        overall_status = db.determine_pass_fail_status(passed_subjects, english_passed)
        
        print(f"\n=== Pass/Fail Analysis ===")
        print(f"Form Level: {form_level}")
        print(f"Pass Threshold: {threshold_text}%")
        print(f"Total Subjects: {total_subjects}")
        print(f"Passed Subjects ({threshold_text}): {passed_subjects}")
        print(f"English Mark: {english_mark}%")
        print(f"English Passed (Form {form_level} threshold): {english_passed}")
        print(f"Overall Status: {overall_status}")
        
        print(f"\n=== Criteria Check ===")
        print(f"Need 6+ subjects passed: {passed_subjects >= 6} ({passed_subjects}/6)")
        print(f"Need English passed: {english_passed}")
        print(f"Should PASS: {passed_subjects >= 6 and english_passed}")
        
        # Test rankings to see if it's consistent
        rankings = db.get_student_rankings(form_level, 'Term 1', '2024-2025')
        margret_ranking = None
        for i, ranking in enumerate(rankings):
            if 'Margret' in ranking['name'] and 'Muhaliwa' in ranking['name']:
                margret_ranking = ranking
                margret_ranking['position'] = i + 1
                break
                
        if margret_ranking:
            print(f"\n=== Ranking Data ===")
            print(f"Position: {margret_ranking['position']}")
            print(f"Average: {margret_ranking['average']:.1f}%")
            print(f"Status in Rankings: {margret_ranking['status']}")
            print(f"Subjects Passed in Rankings: {margret_ranking['subjects_passed']}")
        
    if __name__ == "__main__":
        test_margret_status()
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the correct directory")
except Exception as e:
    print(f"Error: {e}")
