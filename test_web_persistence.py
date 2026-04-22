#!/usr/bin/env python3
"""
Test script to test mark persistence through the web application
This simulates the actual user flow including login, save, and refresh
"""

import os
import sys
import json
import requests
from datetime import datetime

# Add current directory to path 
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_web_persistence():
    """Test mark persistence through web application"""
    
    print("=== Testing Web Application Mark Persistence ===")
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    # Test credentials (using existing school)
    login_data = {
        'username': 'school1',  # Adjust if needed
        'password': 'password123',  # Adjust if needed
        'user_type': 'school'
    }
    
    try:
        # Step 1: Login
        print("\n1. Attempting login...")
        login_response = session.post(
            f"{base_url}/api/login",
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Login Status: {login_response.status_code}")
        if login_response.status_code == 200:
            login_result = login_response.json()
            print(f"Login Response: {json.dumps(login_result, indent=2)}")
            
            if login_result.get('success'):
                print("✅ Login successful")
            else:
                print(f"❌ Login failed: {login_result.get('message')}")
                return
        else:
            print(f"❌ Login HTTP error: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return
        
        # Step 2: Get available students
        print("\n2. Getting available students...")
        try:
            # Try to access form 1 data entry page to get students
            form_response = session.get(f"{base_url}/form/1")
            if form_response.status_code == 200:
                print("✅ Form data entry page accessible")
                
                # Extract student info from page (simplified approach)
                # In real scenario, we'd parse HTML or use API to get students
                print("Note: Assuming student ID 375 exists (from previous tests)")
                test_student_id = 375
                
            else:
                print(f"❌ Cannot access form page: {form_response.status_code}")
                return
                
        except Exception as e:
            print(f"❌ Error accessing form page: {e}")
            return
        
        # Step 3: Save marks via API
        print("\n3. Saving marks via authenticated API...")
        test_marks = {
            'student_id': test_student_id,
            'marks': {
                'Mathematics': 91,
                'English': 83,
                'Science': 77
            },
            'term': 'Term 1',
            'academic_year': '2025-2026',
            'form_level': 1
        }
        
        save_response = session.post(
            f"{base_url}/api/save-student-marks",
            json=test_marks,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Save Status: {save_response.status_code}")
        if save_response.status_code == 200:
            save_result = save_response.json()
            print(f"Save Response: {json.dumps(save_result, indent=2)}")
            
            if save_result.get('success'):
                print("✅ Marks saved successfully")
            else:
                print(f"❌ Save failed: {save_result.get('message')}")
        else:
            print(f"❌ Save HTTP error: {save_response.status_code}")
            print(f"Response: {save_response.text}")
            return
        
        # Step 4: Load marks immediately
        print("\n4. Loading marks immediately...")
        load_params = {
            'student_id': test_student_id,
            'term': 'Term 1',
            'academic_year': '2025-2026'
        }
        
        load_response = session.get(
            f"{base_url}/api/load-student-marks",
            params=load_params,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Load Status: {load_response.status_code}")
        if load_response.status_code == 200:
            load_result = load_response.json()
            print(f"Load Response: {json.dumps(load_result, indent=2)}")
            
            if load_result.get('success'):
                marks = load_result.get('marks', {})
                print("✅ Marks loaded successfully")
                
                # Check if marks match what we saved
                for subject, expected_mark in test_marks['marks'].items():
                    if subject in marks and marks[subject] == expected_mark:
                        print(f"✅ {subject}: {expected_mark}")
                    else:
                        actual = marks.get(subject, 'NOT FOUND')
                        print(f"❌ {subject}: Expected {expected_mark}, Got {actual}")
            else:
                print(f"❌ Load failed: {load_result.get('message')}")
        else:
            print(f"❌ Load HTTP error: {load_response.status_code}")
            print(f"Response: {load_response.text}")
        
        # Step 5: Simulate page refresh (new session)
        print("\n5. Simulating page refresh (new session)...")
        new_session = requests.Session()
        
        # Login again
        login_response2 = new_session.post(
            f"{base_url}/api/login",
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if login_response2.status_code == 200 and login_response2.json().get('success'):
            print("✅ New login successful")
            
            # Load marks with new session
            load_response2 = new_session.get(
                f"{base_url}/api/load-student-marks",
                params=load_params,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Load (new session) Status: {load_response2.status_code}")
            if load_response2.status_code == 200:
                load_result2 = load_response2.json()
                print(f"Load (new session) Response: {json.dumps(load_result2, indent=2)}")
                
                if load_result2.get('success'):
                    marks2 = load_result2.get('marks', {})
                    print("✅ Marks loaded with new session")
                    
                    # Check persistence
                    persistence_ok = True
                    for subject, expected_mark in test_marks['marks'].items():
                        if subject in marks2 and marks2[subject] == expected_mark:
                            print(f"✅ {subject}: {expected_mark} (persisted)")
                        else:
                            actual = marks2.get(subject, 'NOT FOUND')
                            print(f"❌ {subject}: Expected {expected_mark}, Got {actual} (NOT PERSISTED)")
                            persistence_ok = False
                    
                    if persistence_ok:
                        print("\n🎉 ALL MARKS PERSISTED ACROSS SESSIONS!")
                    else:
                        print("\n💥 MARK PERSISTENCE ISSUE DETECTED!")
                else:
                    print(f"❌ Load (new session) failed: {load_result2.get('message')}")
            else:
                print(f"❌ Load (new session) HTTP error: {load_response2.status_code}")
        else:
            print("❌ New login failed")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Please start the web application first.")
        print("   Run: python app.py")
        print("   Then make sure you have valid school credentials to test with.")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_web_persistence()
