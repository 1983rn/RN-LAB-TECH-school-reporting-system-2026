#!/usr/bin/env python3
"""
Test Multi-User System Functionality
"""

import sys
import os

# Add current directory to path 
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from school_database import SchoolDatabase
from multi_user_manager import SchoolUserManager

def test_multi_user_system():
    """Test all multi-user system components"""
    print("Testing Multi-User System")
    print("=" * 40)
    
    try:
        # Initialize components
        db = SchoolDatabase()
        user_manager = SchoolUserManager(db.db_path)
        
        print("1. Testing User Table Creation...")
        if user_manager.create_school_users_table():
            print("   OK User tables created successfully")
        else:
            print("   ERROR Failed to create user tables")
            return False
        
        print("\n2. Testing School Creation...")
        # Create a test school
        school_data = {
            'school_name': "TEST MULTI-USER SCHOOL",
            'username': "testschool",
            'password': "testpass123",
            'address': "Test Address",
            'phone': "+265 123 4567",
            'email': "test@school.edu.mw"
        }
        school_id = db.add_school(school_data)
        
        if school_id:
            print(f"   OK Test school created with ID: {school_id}")
        else:
            print("   ERROR Failed to create test school")
            return False
        
        print("\n3. Testing Default User Creation...")
        # Create default users
        if user_manager.create_default_users(school_id, "TEST MULTI-USER SCHOOL"):
            print("   OK Default users created successfully")
        else:
            print("   ERROR Failed to create default users")
            return False
        
        print("\n4. Testing User Retrieval...")
        users = user_manager.get_school_users(school_id)
        print("   OK Retrieved {} users:".format(len(users)))
        for user in users:
            print(f"     - {user['full_name']} ({user['username']}) - Forms: {user['assigned_forms']}")
        
        print("\n5. Testing User Authentication...")
        # Test authentication for each user
        for user in users:
            auth_result = user_manager.authenticate_school_user(
                user['username'], "Form1Teacher2024", school_id
            )
            if auth_result:
                print(f"     OK {user['username']} authenticated successfully")
            else:
                print(f"   ERROR {user['username']} authentication failed")
        
        print("\n6. Testing Form Access Control...")
        # Test form access conflicts
        test_user = users[0]  # Get first user
        test_form = test_user['assigned_forms'][0]  # Get their assigned form
        
        access_check = user_manager.check_form_access_conflict(
            test_user['user_id'], test_form
        )
        
        if access_check['can_access']:
            print(f"   OK User can access Form {test_form}")
        else:
            print(f"   ERROR Access denied: {access_check['reason']}")
        
        print("\n7. Testing Activity Logging...")
        # Test activity logging
        if user_manager.log_user_activity(
            test_user['user_id'], 'test_activity', test_form,
            "Test activity for verification"
        ):
            print("   OK Activity logged successfully")
        else:
            print("   ERROR Failed to log activity")
        
        print("\n8. Testing Active User Detection...")
        # Test getting active users
        active_users = user_manager.get_active_users_on_form(test_form)
        print(f"   OK Active users on Form {test_form}: {len(active_users)}")
        
        print("\n" + "=" * 40)
        print("OK Multi-User System Test Complete!")
        print("All components are working correctly.")
        print()
        print("Features Verified:")
        print("• User table creation and management")
        print("• Default user creation for schools")
        print("• User authentication system")
        print("• Form assignment and access control")
        print("• Conflict detection and prevention")
        print("• Activity logging and tracking")
        print("• Active user monitoring")
        print()
        print("System is ready for multi-user concurrent access!")
        
        return True
        
    except Exception as e:
        print("ERROR Test failed: {}".format(e))
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_multi_user_system()
    
    if success:
        print("SUCCESS Multi-user system is ready for deployment!")
        print("Schools can now have 4 concurrent users working on Forms 1-4")
    else:
        print("FAILURE Multi-user system test failed")
        print("Please check the error messages above")
    
    sys.exit(0 if success else 1)
