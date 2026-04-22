#!/usr/bin/env python3
"""
Test session isolation and API behavior to identify persistence issue
This tests if there are issues with session handling or API layer
"""

import os
import sys
import json
from datetime import datetime
from unittest.mock import Mock, patch

# Add current directory to path 
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from school_database import SchoolDatabase

def test_session_isolation():
    """Test session isolation and API behavior"""
    
    print("=== Testing Session Isolation and API Behavior ===")
    
    # Initialize database
    db = SchoolDatabase()
    
    # Test parameters
    test_school_id = 1
    test_student_id = 375
    test_term = "Term 1"
    test_academic_year = "2025-2026"
    test_form_level = 1
    
    try:
        # Step 1: Test different school_id scenarios
        print("\n1. Testing school_id isolation...")
        
        # Save with correct school_id
        test_mark = 91
        test_subject = "Physics"
        
        print(f"Saving mark with school_id={test_school_id}")
        db.save_student_mark(
            test_student_id, test_subject, test_mark, test_term, 
            test_academic_year, test_form_level, test_school_id
        )
        
        # Retrieve with correct school_id
        marks_correct = db.get_student_marks(test_student_id, test_term, test_academic_year, test_school_id)
        print(f"With correct school_id: {marks_correct.get(test_subject, {}).get('mark', 'NOT FOUND')}")
        
        # Retrieve with wrong school_id
        wrong_school_id = 999
        marks_wrong = db.get_student_marks(test_student_id, test_term, test_academic_year, wrong_school_id)
        print(f"With wrong school_id: {marks_wrong.get(test_subject, {}).get('mark', 'NOT FOUND')}")
        
        # Step 2: Test session data simulation
        print("\n2. Simulating session data scenarios...")
        
        # Simulate different session scenarios
        session_scenarios = [
            {"user_type": "school", "user_id": test_school_id, "school_user_id": None},
            {"user_type": "school_user", "user_id": None, "school_id": test_school_id, "school_user_id": 123},
            {"user_type": "school", "user_id": None, "school_user_id": None},  # Missing auth
            {"user_type": None, "user_id": None, "school_user_id": None}  # No session
        ]
        
        def get_current_school_id_mock(session_data):
            """Mock version of get_current_school_id function"""
            if session_data.get('user_type') == 'school':
                return session_data.get('user_id')
            elif session_data.get('user_type') == 'school_user':
                return session_data.get('school_id')
            return None
        
        for i, session_data in enumerate(session_scenarios):
            print(f"\n  Scenario {i+1}: {session_data}")
            school_id = get_current_school_id_mock(session_data)
            print(f"    get_current_school_id() returns: {school_id}")
            
            if school_id:
                marks = db.get_student_marks(test_student_id, test_term, test_academic_year, school_id)
                physics_mark = marks.get(test_subject, {}).get('mark', 'NOT FOUND')
                print(f"    Physics mark: {physics_mark}")
            else:
                print(f"    Cannot retrieve marks (no school_id)")
        
        # Step 3: Test API request simulation
        print("\n3. Simulating API request handling...")
        
        # Mock Flask request and session
        class MockRequest:
            def __init__(self, json_data, args_data):
                self.json_data = json_data
                self.args_data = args_data
            
            def get_json(self):
                return self.json_data
            
            def args(self):
                return self.args_data
        
        class MockSession:
            def __init__(self, session_data):
                self.data = session_data
            
            def get(self, key, default=None):
                return self.data.get(key, default)
        
        # Test save API simulation
        mock_session = MockSession({"user_type": "school", "user_id": test_school_id})
        mock_request = MockRequest(
            {
                "student_id": test_student_id,
                "marks": {"Chemistry": 87},
                "term": test_term,
                "academic_year": test_academic_year,
                "form_level": test_form_level
            },
            {}
        )
        
        print("Simulating API save request...")
        try:
            # Simulate the save logic from app.py
            school_id = test_school_id  # From session
            if not school_id:
                print("❌ School authentication required")
                return
            
            data = mock_request.get_json()
            student_id = data['student_id']
            form_level = data['form_level']
            term = data['term']
            academic_year = data['academic_year']
            marks = data['marks']
            
            print(f"API would save: student_id={student_id}, marks={marks}")
            
            # Save marks
            for subject, mark in marks.items():
                if mark is not None and str(mark).strip():
                    mark_value = int(str(mark).strip())
                    db.save_student_mark(student_id, subject, mark_value, term, academic_year, form_level, school_id)
                    print(f"  Saved {subject}: {mark_value}")
            
            # Verify save
            saved_marks = db.get_student_marks(student_id, term, academic_year, school_id)
            print(f"Marks after API save: {json.dumps({k: v['mark'] for k, v in saved_marks.items()}, indent=4)}")
            
        except Exception as e:
            print(f"❌ API simulation failed: {e}")
        
        # Step 4: Test load API simulation
        print("\n4. Simulating API load request...")
        
        mock_request_load = MockRequest({}, {
            "student_id": test_student_id,
            "term": test_term,
            "academic_year": test_academic_year
        })
        
        try:
            # Simulate the load logic from app.py
            school_id = test_school_id  # From session
            if not school_id:
                print("❌ School authentication required")
                return
            
            student_id = int(mock_request_load.args.get("student_id"))
            term = mock_request_load.args.get("term")
            academic_year = mock_request_load.args.get("academic_year")
            
            print(f"API would load: student_id={student_id}, term={term}, year={academic_year}")
            
            marks = db.get_student_marks(student_id, term, academic_year, school_id)
            marks_data = {subject: data['mark'] for subject, data in marks.items()}
            
            print(f"API would return: {json.dumps(marks_data, indent=4)}")
            
        except Exception as e:
            print(f"❌ Load API simulation failed: {e}")
        
        # Step 5: Test potential caching issues
        print("\n5. Testing for potential caching issues...")
        
        # Test multiple rapid saves/loads
        test_values = [71, 72, 73, 74, 75]
        test_subject_rapid = "Biology"
        
        for i, value in enumerate(test_values):
            print(f"  Rapid test {i+1}: Saving {test_subject_rapid} = {value}")
            db.save_student_mark(
                test_student_id, test_subject_rapid, value, test_term,
                test_academic_year, test_form_level, test_school_id
            )
            
            # Immediate load
            marks = db.get_student_marks(test_student_id, test_term, test_academic_year, test_school_id)
            loaded_value = marks.get(test_subject_rapid, {}).get('mark', 'NOT FOUND')
            print(f"    Immediately loaded: {loaded_value}")
            
            if loaded_value != value:
                print(f"    ❌ MISMATCH! Expected {value}, got {loaded_value}")
            else:
                print(f"    ✅ Match")
        
        # Step 6: Test concurrent access simulation
        print("\n6. Testing concurrent access simulation...")
        
        # Save a mark with one connection
        test_subject_concurrent = "Geography"
        test_mark_concurrent = 84
        
        print(f"Saving {test_subject_concurrent} = {test_mark_concurrent}")
        db.save_student_mark(
            test_student_id, test_subject_concurrent, test_mark_concurrent, test_term,
            test_academic_year, test_form_level, test_school_id
        )
        
        # Check with multiple connections
        for i in range(3):
            db_test = SchoolDatabase()
            marks = db_test.get_student_marks(test_student_id, test_term, test_academic_year, test_school_id)
            loaded = marks.get(test_subject_concurrent, {}).get('mark', 'NOT FOUND')
            print(f"  Connection {i+1}: {test_subject_concurrent} = {loaded}")
        
        # Clean up test data
        print("\n7. Cleaning up test data...")
        test_subjects = [test_subject, "Chemistry", test_subject_rapid, test_subject_concurrent]
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            for subject in test_subjects:
                cursor.execute("""
                    DELETE FROM student_marks 
                    WHERE student_id = ? AND subject = ? AND term = ? AND academic_year = ? AND school_id = ?
                """, (test_student_id, subject, test_term, test_academic_year, test_school_id))
            conn.commit()
            print(f"  Cleaned up {len(test_subjects)} test subjects")
        
        print("\n" + "="*60)
        print("🔍 SESSION ISOLATION TEST COMPLETE")
        print("   If database tests pass, the issue is likely:")
        print("   1. Frontend caching (browser or application level)")
        print("   2. Session management in web application")
        print("   3. API response caching")
        print("   4. Form submission issues (duplicate prevention, CSRF, etc.)")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_session_isolation()
