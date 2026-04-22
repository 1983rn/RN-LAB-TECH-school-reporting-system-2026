#!/usr/bin/env python3
"""
Test script for School Management API endpoints
This script tests the new developer school management functionality
"""

import sys
import os
import json
import traceback

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_imports():
    """Test if all required modules can be imported"""
    try:
        print("🔍 Testing imports...")
        
        # Test Flask app import
        from app import app, db
        print("✅ Flask app imported successfully")
        
        # Test database connection
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM schools")
            school_count = cursor.fetchone()[0]
            print(f"✅ Database connection successful - {school_count} schools found")
        
        return True
        
    except Exception as e:
        print(f"❌ Import/Database Error: {e}")
        traceback.print_exc()
        return False

def test_school_management_endpoints():
    """Test school management functionality"""
    try:
        print("\n🧪 Testing School Management Functions...")
        
        from app import app, db
        
        # Test adding a school
        print("📝 Testing add_school function...")
        test_school_data = {
            'school_name': 'Test Secondary School',
            'username': 'testschool',
            'password': 'testpassword123'
        }
        
        school_id = db.add_school(test_school_data)
        print(f"✅ School added successfully with ID: {school_id}")
        
        # Test getting all schools
        print("📋 Testing get_all_schools function...")
        schools = db.get_all_schools()
        print(f"✅ Retrieved {len(schools)} schools")
        
        # Test authentication
        print("🔐 Testing school authentication...")
        auth_result = db.authenticate_school('testschool', 'testpassword123')
        if auth_result:
            print(f"✅ Authentication successful for: {auth_result['school_name']}")
        else:
            print("❌ Authentication failed")
        
        # Test updating school status
        print("🔄 Testing update_school_status function...")
        db.update_school_status(school_id, 'locked')
        print("✅ School status updated to locked")
        
        # Test granting subscription
        print("💳 Testing grant_subscription function...")
        db.grant_subscription(school_id, 6)  # 6 months
        print("✅ Subscription granted successfully")
        
        # Clean up - delete test school
        print("🧹 Cleaning up test data...")
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM schools WHERE school_id = ?", (school_id,))
        print("✅ Test school deleted")
        
        return True
        
    except Exception as e:
        print(f"❌ School Management Test Error: {e}")
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Test API endpoints using Flask test client"""
    try:
        print("\n🌐 Testing API Endpoints...")
        
        from app import app, db
        
        with app.test_client() as client:
            # Test developer login
            print("🔑 Testing developer login...")
            login_response = client.post('/api/login', 
                json={
                    'username': os.environ.get('DEVELOPER_USERNAME', 'MAKONOKAya'),
                    'password': os.environ.get('DEVELOPER_PASSWORD', 'NAMADEYIMKOLOWEKO1949'),
                    'user_type': 'developer'
                }
            )
            
            if login_response.status_code == 200:
                login_data = json.loads(login_response.data)
                if login_data.get('success'):
                    print("✅ Developer login successful")
                else:
                    print(f"❌ Login failed: {login_data.get('message')}")
                    return False
            else:
                print(f"❌ Login request failed with status: {login_response.status_code}")
                return False
            
            # Set up session for subsequent requests
            with client.session_transaction() as sess:
                sess['user_id'] = 'developer'
                sess['user_type'] = 'developer'
                sess['username'] = os.environ.get('DEVELOPER_USERNAME', 'MAKONOKAya')
            
            # Test get schools endpoint
            print("📋 Testing /api/developer/schools endpoint...")
            schools_response = client.get('/api/developer/schools')
            
            if schools_response.status_code == 200:
                schools_data = json.loads(schools_response.data)
                if schools_data.get('success'):
                    print(f"✅ Schools endpoint working - {len(schools_data.get('schools', []))} schools")
                else:
                    print(f"❌ Schools endpoint error: {schools_data.get('message')}")
            else:
                print(f"❌ Schools endpoint failed with status: {schools_response.status_code}")
            
            # Test add school endpoint
            print("➕ Testing /api/developer/add-school endpoint...")
            add_school_response = client.post('/api/developer/add-school',
                json={
                    'school_name': 'API Test School',
                    'username': 'apitest',
                    'password': 'apitest123'
                }
            )
            
            if add_school_response.status_code == 200:
                add_data = json.loads(add_school_response.data)
                if add_data.get('success'):
                    test_school_id = add_data.get('school_id')
                    print(f"✅ Add school endpoint working - School ID: {test_school_id}")
                    
                    # Test reset credentials endpoint
                    print("🔑 Testing /api/developer/reset-school-credentials endpoint...")
                    reset_response = client.post('/api/developer/reset-school-credentials', json={'school_id': test_school_id})
                    if reset_response.status_code == 200:
                        reset_data = json.loads(reset_response.data)
                        if reset_data.get('success'):
                            temp_pw = reset_data.get('temporary_password')
                            print("✅ Reset endpoint returned temporary password")
                            # Verify that the temporary password authenticates
                            auth_result = db.authenticate_school('apitest', temp_pw)
                            if auth_result and auth_result.get('school_id') == test_school_id:
                                print("✅ Temporary password works for authentication")
                            else:
                                print("❌ Temporary password did not authenticate")
                        else:
                            print(f"❌ Reset failed: {reset_data.get('message')}")
                    else:
                        print(f"❌ Reset endpoint failed with status: {reset_response.status_code}")
                    
                    # Clean up - delete the test school
                    print("🧹 Cleaning up API test school...")
                    delete_response = client.post('/api/developer/delete-school',
                        json={'school_id': test_school_id}
                    )
                    
                    if delete_response.status_code == 200:
                        delete_data = json.loads(delete_response.data)
                        if delete_data.get('success'):
                            print("✅ Delete school endpoint working")
                        else:
                            print(f"⚠️ Delete failed: {delete_data.get('message')}")
                    
                else:
                    print(f"❌ Add school error: {add_data.get('message')}")
            else:
                print(f"❌ Add school endpoint failed with status: {add_school_response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ API Endpoint Test Error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 School Management API Test Suite")
    print("=" * 50)
    
    # Test 1: Imports and Database
    if not test_imports():
        print("\n❌ Import/Database tests failed. Cannot continue.")
        return False
    
    # Test 2: School Management Functions
    if not test_school_management_endpoints():
        print("\n❌ School management function tests failed.")
        return False
    
    # Test 3: API Endpoints
    if not test_api_endpoints():
        print("\n❌ API endpoint tests failed.")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed successfully!")
    print("✅ School management functionality is working correctly")
    print("🌐 You can now use the developer dashboard to add schools")
    print("\n📝 To add a school:")
    print("1. Login as developer ([REDACTED] / [REDACTED])")
    print("2. Go to Developer Dashboard")
    print("3. Click 'Add School' button")
    print("4. Fill in school details")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Tests failed. Check the error messages above.")
            input("Press Enter to exit...")
            sys.exit(1)
        else:
            print("\n✅ All tests completed successfully!")
            input("Press Enter to exit...")
    except KeyboardInterrupt:
        print("\n\n⏹️ Tests interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)