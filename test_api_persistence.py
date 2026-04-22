#!/usr/bin/env python3
"""
Test script to test the API endpoints for mark persistence
"""

import os
import sys
import json
import requests
from datetime import datetime

# Add current directory to path 
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_api_endpoints():
    """Test the actual API endpoints used by frontend"""
    
    print("=== Testing API Mark Persistence ===")
    
    # API base URL (assuming local development)
    base_url = "http://localhost:5000"
    
    # Test data
    test_data = {
        'student_id': 375,  # Use existing student from previous test
        'marks': {
            'Mathematics': 88,
            'English': 76,
            'Science': 94
        },
        'term': 'Term 1',
        'academic_year': '2025-2026',
        'form_level': 1
    }
    
    try:
        # Test 1: Save marks via API
        print("\n1. Testing save API endpoint...")
        save_url = f"{base_url}/api/save-student-marks"
        
        try:
            response = requests.post(
                save_url,
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            print(f"Save API Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Save API Response: {json.dumps(result, indent=2)}")
                if result.get('success'):
                    print("✅ Marks saved via API")
                else:
                    print(f"❌ API save failed: {result.get('message')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to Flask app. Please start the web application first.")
            print("   Run: python app.py")
            return
        except Exception as e:
            print(f"❌ Save API test failed: {e}")
            return
        
        # Test 2: Load marks via API
        print("\n2. Testing load API endpoint...")
        load_url = f"{base_url}/api/load-student-marks"
        params = {
            'student_id': test_data['student_id'],
            'term': test_data['term'],
            'academic_year': test_data['academic_year']
        }
        
        try:
            response = requests.get(
                load_url,
                params=params,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            print(f"Load API Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Load API Response: {json.dumps(result, indent=2)}")
                
                if result.get('success'):
                    marks = result.get('marks', {})
                    print("✅ Marks loaded via API")
                    
                    # Check if our test marks are present
                    for subject, expected_mark in test_data['marks'].items():
                        if subject in marks and marks[subject] == expected_mark:
                            print(f"✅ {subject}: {expected_mark}")
                        else:
                            actual = marks.get(subject, 'NOT FOUND')
                            print(f"❌ {subject}: Expected {expected_mark}, Got {actual}")
                else:
                    print(f"❌ API load failed: {result.get('message')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Load API test failed: {e}")
        
        # Test 3: Test with cache-busting
        print("\n3. Testing load API with cache-busting...")
        params['_t'] = int(datetime.now().timestamp() * 1000)
        
        try:
            response = requests.get(
                load_url,
                params=params,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            print(f"Load API (no-cache) Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Load API (no-cache) Response: {json.dumps(result, indent=2)}")
                
                # Check cache headers
                cache_control = response.headers.get('Cache-Control', 'No cache header')
                print(f"Cache-Control header: {cache_control}")
                
        except Exception as e:
            print(f"❌ Load API (no-cache) test failed: {e}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_endpoints()
