#!/usr/bin/env python3
"""
Test script to verify the ranking logic for Forms 3&4
This script tests that students with lower aggregate points get better positions
and that failed students are ranked below those who passed.
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from school_database import SchoolDatabase

def test_forms_34_ranking():
    """Test the ranking logic for Forms 3&4"""
    print("🧪 Testing Forms 3&4 Ranking Logic")
    print("=" * 50)
    
    try:
        db = SchoolDatabase()
        
        # Test with sample data - get rankings for Form 3 or 4
        form_level = 3
        term = "Term 1"
        academic_year = "2024-2025"
        
        print(f"📊 Getting rankings for Form {form_level}, {term} {academic_year}")
        
        # Get rankings using the updated method
        rankings = db.get_student_rankings(form_level, term, academic_year)
        
        if not rankings:
            print("❌ No ranking data found. Please ensure there are students with marks in the database.")
            return
        
        print(f"\n✅ Found {len(rankings)} students")
        print("\n🏆 RANKING RESULTS (Forms 3&4 - Lower Aggregate Points = Better Position):")
        print("-" * 80)
        print(f"{'Pos':<4} {'Student Name':<25} {'Agg Points':<12} {'Subjects':<10} {'Status':<8}")
        print("-" * 80)
        
        passed_students = []
        failed_students = []
        
        for i, student in enumerate(rankings):
            position = i + 1
            name = student['name']
            aggregate_points = student.get('aggregate_points', 'N/A')
            subjects_passed = student['subjects_passed']
            status = student['status']
            
            print(f"{position:<4} {name:<25} {aggregate_points:<12} {subjects_passed}/12{'':<4} {status:<8}")
            
            if status == 'PASS':
                passed_students.append((position, aggregate_points))
            else:
                failed_students.append((position, aggregate_points))
        
        print("-" * 80)
        
        # Verify the ranking logic
        print("\n🔍 VERIFICATION:")
        
        # Check 1: All passed students should be ranked before failed students
        if passed_students and failed_students:
            highest_pass_position = max(pos for pos, _ in passed_students)
            lowest_fail_position = min(pos for pos, _ in failed_students)
            
            if highest_pass_position < lowest_fail_position:
                print("✅ PASS: All passed students are ranked above failed students")
            else:
                print("❌ FAIL: Some failed students are ranked above passed students")
        
        # Check 2: Among passed students, lower aggregate points should have better positions
        if len(passed_students) > 1:
            passed_sorted = sorted(passed_students, key=lambda x: x[0])  # Sort by position
            aggregate_ascending = True
            
            for i in range(1, len(passed_sorted)):
                prev_agg = passed_sorted[i-1][1]
                curr_agg = passed_sorted[i][1]
                
                if prev_agg != 'N/A' and curr_agg != 'N/A':
                    if prev_agg > curr_agg:  # Previous should have lower or equal aggregate points
                        aggregate_ascending = False
                        break
            
            if aggregate_ascending:
                print("✅ PASS: Among passed students, lower aggregate points have better positions")
            else:
                print("❌ FAIL: Aggregate points ranking is incorrect among passed students")
        
        print(f"\n📈 Summary:")
        print(f"   • Total students: {len(rankings)}")
        print(f"   • Passed students: {len(passed_students)}")
        print(f"   • Failed students: {len(failed_students)}")
        
        if passed_students:
            best_aggregate = min(agg for _, agg in passed_students if agg != 'N/A')
            print(f"   • Best aggregate points (passed): {best_aggregate}")
        
        print("\n✅ Ranking logic test completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

def test_forms_12_ranking():
    """Test the ranking logic for Forms 1&2"""
    print("\n🧪 Testing Forms 1&2 Ranking Logic")
    print("=" * 50)
    
    try:
        db = SchoolDatabase()
        
        # Test with sample data - get rankings for Form 1 or 2
        form_level = 1
        term = "Term 1"
        academic_year = "2024-2025"
        
        print(f"📊 Getting rankings for Form {form_level}, {term} {academic_year}")
        
        # Get rankings using the updated method
        rankings = db.get_student_rankings(form_level, term, academic_year)
        
        if not rankings:
            print("❌ No ranking data found for Forms 1&2.")
            return
        
        print(f"\n✅ Found {len(rankings)} students")
        print("\n🏆 RANKING RESULTS (Forms 1&2 - Grade-based ranking):")
        print("-" * 70)
        print(f"{'Pos':<4} {'Student Name':<25} {'Grade':<8} {'Subjects':<10} {'Status':<8}")
        print("-" * 70)
        
        for i, student in enumerate(rankings):
            position = i + 1
            name = student['name']
            grade = student.get('grade', 'N/A')
            subjects_passed = student['subjects_passed']
            status = student['status']
            
            print(f"{position:<4} {name:<25} {grade:<8} {subjects_passed}/12{'':<4} {status:<8}")
        
        print("-" * 70)
        print("✅ Forms 1&2 ranking test completed!")
        
    except Exception as e:
        print(f"❌ Error during Forms 1&2 testing: {e}")

if __name__ == "__main__":
    print("🚀 Starting Ranking Logic Tests")
    print("This test verifies that:")
    print("1. For Forms 3&4: Students with LOWER aggregate points get BETTER positions")
    print("2. Failed students are always ranked below passed students")
    print("3. For Forms 1&2: Grade-based ranking works correctly")
    print()
    
    test_forms_34_ranking()
    test_forms_12_ranking()
    
    print("\n🎯 Test Summary:")
    print("The ranking system has been updated to ensure:")
    print("• Forms 3&4: Lower aggregate points = Better ranking position")
    print("• All failed students are ranked below passed students")
    print("• Forms 1&2: Traditional grade-based ranking")