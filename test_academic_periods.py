#!/usr/bin/env python3
"""
Test script to verify that changing academic periods doesn't interfere with grades
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from school_database import SchoolDatabase
import tempfile

def test_academic_periods_protection():
    """Test that changing academic periods doesn't affect existing grades"""
    
    # Create a temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        test_db_path = tmp_file.name
    
    try:
        # Initialize database
        db = SchoolDatabase(test_db_path)
        print("✓ Database initialized")
        
        # Add a test student
        student_data = {
            'first_name': 'Test',
            'last_name': 'Student',
            'grade_level': 1,
            'date_of_birth': '2010-01-01'
        }
        student_id = db.add_student(student_data)
        print(f"✓ Test student added with ID: {student_id}")
        
        # Add some test grades
        original_term = "Term 1"
        original_year = "2024-2025"
        
        test_marks = {
            'Mathematics': 85,
            'English': 78,
            'Science': 92
        }
        
        for subject, mark in test_marks.items():
            db.save_student_mark(student_id, subject, mark, original_term, original_year, 1)
        
        print(f"✓ Test grades saved for {original_term} {original_year}")
        
        # Verify grades exist
        marks_before = db.get_student_marks(student_id, original_term, original_year)
        print(f"✓ Retrieved {len(marks_before)} marks before changes")
        
        # Test 1: Add new academic periods via settings
        new_settings = {
            'school_name': 'Test School',
            'academic_years': ['2024-2025', '2025-2026', '2026-2027'],  # Added new years
            'terms': ['Term 1', 'Term 2', 'Term 3', 'Term 4']  # Added new term
        }
        
        db.update_school_settings(new_settings)
        print("✓ Updated settings with new academic periods")
        
        # Verify original grades still exist
        marks_after = db.get_student_marks(student_id, original_term, original_year)
        print(f"✓ Retrieved {len(marks_after)} marks after changes")
        
        # Compare marks
        if len(marks_before) == len(marks_after):
            print("✓ Same number of marks preserved")
        else:
            print(f"✗ Mark count changed: {len(marks_before)} -> {len(marks_after)}")
            assert False, "Mark count changed"
        
        # Check individual marks
        for subject in test_marks:
            if subject in marks_before and subject in marks_after:
                if marks_before[subject]['mark'] == marks_after[subject]['mark']:
                    print(f"✓ {subject} mark preserved: {marks_after[subject]['mark']}")
                else:
                    print(f"✗ {subject} mark changed: {marks_before[subject]['mark']} -> {marks_after[subject]['mark']}")
                    assert False, f"{subject} mark changed"
            else:
                print(f"✗ {subject} mark missing")
                assert False, f"{subject} mark missing"
        
        # Test 2: Check available periods functionality
        periods_data = db.get_available_terms_and_years()
        print(f"✓ Available periods retrieved: {len(periods_data['periods_with_data'])} periods with data")
        
        # Verify our test data appears in periods with data
        found_test_period = False
        for period in periods_data['periods_with_data']:
            if period['term'] == original_term and period['year'] == original_year:
                found_test_period = True
                break
        
        if found_test_period:
            print(f"✓ Test period {original_term} {original_year} found in periods with data")
        else:
            print(f"✗ Test period {original_term} {original_year} not found in periods with data")
            assert False, "Test period not found in periods with data"
        # Test 3: Add grades for new period
        new_term = "Term 4"  # This is a newly added term
        new_year = "2025-2026"  # This is a newly added year
        
        db.save_student_mark(student_id, 'Mathematics', 90, new_term, new_year, 1)
        print(f"✓ Added grade for new period {new_term} {new_year}")
        
        # Verify both old and new grades exist
        old_marks = db.get_student_marks(student_id, original_term, original_year)
        new_marks = db.get_student_marks(student_id, new_term, new_year)
        
        if len(old_marks) == 3 and len(new_marks) == 1:
            print("✓ Both old and new grades coexist correctly")
        else:
            print(f"✗ Grade coexistence failed: old={len(old_marks)}, new={len(new_marks)}")
            assert False, "Grade coexistence failed"
        
        print("\n🎉 All tests passed! Academic periods can be changed safely without affecting grades.")
        assert True
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Test failed with error: {e}"
    
    finally:
        # Clean up temporary database
        try:
            os.unlink(test_db_path)
        except:
            pass

if __name__ == '__main__':
    print("Testing Academic Periods Protection System")
    print("=" * 50)
    
    success = test_academic_periods_protection()
    
    if success:
        print("\n✅ SYSTEM READY: Terms and Academic Years can be changed safely!")
        sys.exit(0)
    else:
        print("\n❌ SYSTEM NEEDS ATTENTION: Issues found with academic periods protection")
        sys.exit(1)
