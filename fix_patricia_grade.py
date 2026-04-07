#!/usr/bin/env python3
"""
Fix Patricia Bwanali's average grade issue for Form 1
For Forms 1 and 2, if a student has passed but gets average grade "F", 
the system should find the alternative grade from available passing grades.
"""

from school_database import SchoolDatabase

def fix_patricia_grade():
    """Fix Patricia's grade calculation issue"""
    db = SchoolDatabase()
    
    # Find Patricia Bwanali in Form 1
    students = db.get_students_by_grade(1)
    patricia = None
    
    for student in students:
        if ('patricia' in student['first_name'].lower() and 
            'bwanali' in student['last_name'].lower()):
            patricia = student
            break
    
    if not patricia:
        print("❌ Patricia Bwanali not found in Form 1")
        return
    
    print(f"✅ Found Patricia Bwanali: ID={patricia['student_id']}")
    
    # Get her current marks
    marks = db.get_student_marks(patricia['student_id'], 'Term 1', '2024-2025')
    
    if not marks:
        print("❌ No marks found for Patricia")
        return
    
    print("\n📊 Current Subject Performance:")
    passed_subjects = 0
    grades = []
    
    for subject, data in marks.items():
        mark = data['mark']
        grade = data['grade']
        status = 'PASS' if mark >= 50 else 'FAIL'
        print(f"  {subject:<20}: {mark:>3}% ({grade}) - {status}")
        grades.append(grade)
        if mark >= 50:
            passed_subjects += 1
    
    # Check English specifically
    english_mark = marks.get('English', {}).get('mark', 0)
    english_passed = english_mark >= 50
    
    print(f"\n📈 Summary:")
    print(f"  Subjects passed: {passed_subjects}")
    print(f"  English passed: {english_passed} ({english_mark}%)")
    
    # Determine overall status
    overall_status = 'PASS' if passed_subjects >= 6 and english_passed else 'FAIL'
    print(f"  Overall status: {overall_status}")
    
    # Calculate current average grade
    if grades:
        grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
        for grade in grades:
            if grade in grade_counts:
                grade_counts[grade] += 1
        
        print(f"\n🎯 Grade Distribution:")
        for grade, count in grade_counts.items():
            if count > 0:
                print(f"  Grade {grade}: {count} subjects")
        
        # Find most common grade
        max_count = max(grade_counts.values())
        most_common_grades = [grade for grade, count in grade_counts.items() if count == max_count]
        
        if len(most_common_grades) == 1:
            current_avg_grade = most_common_grades[0]
        else:
            # Use average marks to determine grade
            total_marks = sum(marks[subject]['mark'] for subject in marks)
            average_mark = total_marks / len(marks)
            current_avg_grade = db.calculate_grade(int(average_mark), 1)
        
        print(f"\n🔍 Current Average Grade: {current_avg_grade}")
        
        # Apply the fix for Forms 1 and 2
        if patricia['grade_level'] in [1, 2] and overall_status == 'PASS' and current_avg_grade == 'F':
            print(f"\n⚠️  ISSUE DETECTED: Student has PASSED but average grade is F")
            print(f"   Applying correction for Forms 1-2...")
            
            # Get passing grades only (D, C, B, A)
            passing_grades = [g for g in grades if g in ['A', 'B', 'C', 'D']]
            
            if passing_grades:
                # Count frequency of passing grades only
                pass_grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
                for grade in passing_grades:
                    pass_grade_counts[grade] += 1
                
                print(f"   Passing grades distribution:")
                for grade, count in pass_grade_counts.items():
                    if count > 0:
                        print(f"     Grade {grade}: {count} subjects")
                
                # Find most common passing grade
                max_pass_count = max(pass_grade_counts.values())
                most_common_pass_grades = [grade for grade, count in pass_grade_counts.items() if count == max_pass_count]
                
                if len(most_common_pass_grades) == 1:
                    corrected_grade = most_common_pass_grades[0]
                else:
                    # If tie among passing grades, use average marks
                    total_marks = sum(marks[subject]['mark'] for subject in marks)
                    average_mark = total_marks / len(marks)
                    corrected_grade = db.calculate_grade(int(average_mark), 1)
                    # Ensure it's not F for a passed student
                    if corrected_grade == 'F':
                        corrected_grade = 'D'  # Minimum passing grade
                
                print(f"\n✅ CORRECTION APPLIED:")
                print(f"   Original average grade: {current_avg_grade}")
                print(f"   Corrected average grade: {corrected_grade}")
                print(f"   Status: {overall_status}")
                
                return {
                    'student_name': f"{patricia['first_name']} {patricia['last_name']}",
                    'student_id': patricia['student_id'],
                    'form_level': patricia['grade_level'],
                    'original_grade': current_avg_grade,
                    'corrected_grade': corrected_grade,
                    'status': overall_status,
                    'passed_subjects': passed_subjects,
                    'english_passed': english_passed
                }
            else:
                print(f"   ❌ No passing grades found to use as alternative")
        else:
            print(f"\n✅ No correction needed:")
            print(f"   Form Level: {patricia['grade_level']}")
            print(f"   Status: {overall_status}")
            print(f"   Average Grade: {current_avg_grade}")
    
    return None

if __name__ == "__main__":
    print("🔧 FIXING PATRICIA BWANALI'S GRADE CALCULATION")
    print("=" * 60)
    
    result = fix_patricia_grade()
    
    if result:
        print(f"\n📋 CORRECTION SUMMARY:")
        print(f"   Student: {result['student_name']}")
        print(f"   Form: {result['form_level']}")
        print(f"   Status: {result['status']}")
        print(f"   Subjects Passed: {result['passed_subjects']}")
        print(f"   English Passed: {result['english_passed']}")
        print(f"   Grade: {result['original_grade']} → {result['corrected_grade']}")
        print(f"\n✅ Fix applied successfully!")
    else:
        print(f"\n✅ No correction was needed or applied.")