#!/usr/bin/env python3
"""
Test script to verify that term and academic year selection updates work correctly
"""

import requests
import json

# Test configuration
BASE_URL = "http://localhost:5000"
TEST_SCHOOL_USERNAME = "NANJATI_CDSS"
TEST_SCHOOL_PASSWORD = "NANJATI2024"

def test_period_update():
    """Test the period update functionality"""
    
    # Create a session
    session = requests.Session()
    
    try:
        # 1. Login as school
        print("1. Logging in as school...")
        login_response = session.post(f"{BASE_URL}/api/login", json={
            "username": TEST_SCHOOL_USERNAME,
            "password": TEST_SCHOOL_PASSWORD,
            "user_type": "school"
        })
        
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.text}")
            return False
        
        login_data = login_response.json()
        if not login_data.get('success'):
            print(f"Login failed: {login_data.get('message')}")
            return False
        
        print("✓ Login successful")
        
        # 2. Test updating selected period
        print("\n2. Testing period update...")
        period_response = session.post(f"{BASE_URL}/api/update-selected-period", json={
            "term": "Term 1",
            "academic_year": "2024-2025"
        })
        
        if period_response.status_code != 200:
            print(f"Period update failed: {period_response.text}")
            return False
        
        period_data = period_response.json()
        if not period_data.get('success'):
            print(f"Period update failed: {period_data.get('message')}")
            return False
        
        print("✓ Period update successful")
        
        # 3. Test getting available periods
        print("\n3. Testing get available periods...")
        periods_response = session.get(f"{BASE_URL}/api/get-available-periods")
        
        if periods_response.status_code != 200:
            print(f"Get periods failed: {periods_response.text}")
            return False
        
        periods_data = periods_response.json()
        if not periods_data.get('success'):
            print(f"Get periods failed: {periods_data.get('message')}")
            return False
        
        print("✓ Get periods successful")
        print(f"Available periods data: {json.dumps(periods_data['data'], indent=2)}")
        
        # 4. Test another period update
        print("\n4. Testing another period update...")
        period_response2 = session.post(f"{BASE_URL}/api/update-selected-period", json={
            "term": "Term 2",
            "academic_year": "2024-2025"
        })
        
        if period_response2.status_code != 200:
            print(f"Second period update failed: {period_response2.text}")
            return False
        
        period_data2 = period_response2.json()
        if not period_data2.get('success'):
            print(f"Second period update failed: {period_data2.get('message')}")
            return False
        
        print("✓ Second period update successful")
        
        print("\n✅ All tests passed! Period update functionality is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    print("Testing Period Update Functionality")
    print("=" * 50)
    
    success = test_period_update()
    
    if success:
        print("\n🎉 All tests completed successfully!")
    else:
        print("\n💥 Some tests failed. Check the output above for details.")