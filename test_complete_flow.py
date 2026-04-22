#!/usr/bin/env python3
"""
Complete test to simulate user flow and identify persistence issue
This test simulates the exact flow users experience in the web interface
"""

import os
import sys
import json
import time
from datetime import datetime

# Add current directory to path 
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from school_database import SchoolDatabase

def test_complete_user_flow():
    """Test complete user flow to identify persistence issue"""
    
    print("=== Testing Complete User Flow for Mark Persistence ===")
    
    # Initialize database
    db = SchoolDatabase()
    
    # Test parameters
    test_school_id = 1
    test_student_id = 375  # Use existing student from previous tests
    test_term = "Term 1"
    test_academic_year = "2025-2026"
    test_form_level = 1
    
    print(f"Testing with student {test_student_id}")
    
    try:
        # Step 1: Simulate user loading existing marks
        print("\n1. Simulating user loading existing marks...")
        initial_marks = db.get_student_marks(test_student_id, test_term, test_academic_year, test_school_id)
        print(f"Initial marks in database: {json.dumps(initial_marks, indent=2)}")
        
        # Step 2: Simulate user editing marks
        print("\n2. Simulating user editing marks...")
        edited_marks = {
            'Mathematics': 95,  # Changed from existing
            'English': 88,     # Changed from existing
            'Science': 76,      # Changed from existing
            'History': 82       # New subject
        }
        
        print(f"User wants to save: {json.dumps(edited_marks, indent=2)}")
        
        # Step 3: Save each mark individually (like frontend does)
        print("\n3. Saving marks individually (like frontend)...")
        for subject, mark in edited_marks.items():
            print(f"  Saving {subject}: {mark}")
            db.save_student_mark(
                test_student_id, 
                subject, 
                mark, 
                test_term, 
                test_academic_year, 
                test_form_level, 
                test_school_id
            )
            # Small delay to simulate real usage
            time.sleep(0.1)
        
        # Step 4: Verify marks were saved
        print("\n4. Verifying marks after save...")
        saved_marks = db.get_student_marks(test_student_id, test_term, test_academic_year, test_school_id)
        print(f"Marks after save: {json.dumps(saved_marks, indent=2)}")
        
        # Step 5: Check if all marks match
        print("\n5. Checking mark consistency...")
        all_match = True
        for subject, expected_mark in edited_marks.items():
            if subject in saved_marks:
                actual_mark = saved_marks[subject]['mark']
                if actual_mark == expected_mark:
                    print(f"✅ {subject}: {actual_mark} (correct)")
                else:
                    print(f"❌ {subject}: Expected {expected_mark}, Got {actual_mark}")
                    all_match = False
            else:
                print(f"❌ {subject}: Not found in database")
                all_match = False
        
        # Step 6: Test with new connection (simulate page refresh)
        print("\n6. Testing with fresh connection (simulate page refresh)...")
        db_fresh = SchoolDatabase()
        fresh_marks = db_fresh.get_student_marks(test_student_id, test_term, test_academic_year, test_school_id)
        print(f"Marks with fresh connection: {json.dumps(fresh_marks, indent=2)}")
        
        # Step 7: Final consistency check
        print("\n7. Final consistency check...")
        fresh_match = True
        for subject, expected_mark in edited_marks.items():
            if subject in fresh_marks:
                actual_mark = fresh_marks[subject]['mark']
                if actual_mark == expected_mark:
                    print(f"✅ {subject}: {actual_mark} (persisted)")
                else:
                    print(f"❌ {subject}: Expected {expected_mark}, Got {actual_mark} (NOT PERSISTED)")
                    fresh_match = False
            else:
                print(f"❌ {subject}: Not found after refresh")
                fresh_match = False
        
        # Step 8: Test database corruption/inconsistency
        print("\n8. Checking for database inconsistencies...")
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as count FROM student_marks 
                WHERE student_id = ? AND term = ? AND academic_year = ? AND school_id = ?
            """, (test_student_id, test_term, test_academic_year, test_school_id))
            
            total_count = cursor.fetchone()[0]
            print(f"Total marks in database for this student/period: {total_count}")
            
            # Get all marks for this student
            cursor.execute("""
                SELECT subject, mark, grade, date_entered FROM student_marks 
                WHERE student_id = ? AND term = ? AND academic_year = ? AND school_id = ?
                ORDER BY date_entered DESC
            """, (test_student_id, test_term, test_academic_year, test_school_id))
            
            all_db_marks = cursor.fetchall()
            print("All marks in database (most recent first):")
            for row in all_db_marks:
                print(f"  {row[0]}: {row[1]} (Grade: {row[2]}, Date: {row[3]})")
        
        # Final result
        print("\n" + "="*60)
        if all_match and fresh_match:
            print("🎉 MARK PERSISTENCE WORKING CORRECTLY!")
            print("   The issue might be in frontend caching or API layer.")
        else:
            print("💥 MARK PERSISTENCE ISSUE CONFIRMED!")
            if not all_match:
                print("   - Marks not matching immediately after save")
            if not fresh_match:
                print("   - Marks not persisting after connection refresh")
        
        # Step 9: Test potential race condition
        print("\n9. Testing for potential race conditions...")
        test_mark = 99
        test_subject = "TestSubject"
        
        print(f"Saving test mark: {test_subject} = {test_mark}")
        db.save_student_mark(
            test_student_id, test_subject, test_mark, test_term, 
            test_academic_year, test_form_level, test_school_id
        )
        
        # Immediate check
        immediate_check = db.get_student_marks(test_student_id, test_term, test_academic_year, test_school_id)
        immediate_result = immediate_check.get(test_subject, {}).get('mark', None)
        
        # Check after delay
        time.sleep(0.5)
        delayed_check = db.get_student_marks(test_student_id, test_term, test_academic_year, test_school_id)
        delayed_result = delayed_check.get(test_subject, {}).get('mark', None)
        
        print(f"Immediate check: {immediate_result}")
        print(f"Delayed check: {delayed_result}")
        
        if immediate_result == delayed_result == test_mark:
            print("✅ No race condition detected")
        else:
            print("❌ Potential race condition or transaction issue")
        
        # Clean up test data
        print("\n10. Cleaning up test data...")
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM student_marks 
                WHERE student_id = ? AND subject = ? AND term = ? AND academic_year = ? AND school_id = ?
            """, (test_student_id, test_subject, test_term, test_academic_year, test_school_id))
            conn.commit()
        print("✅ Test data cleaned up")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_user_flow()
