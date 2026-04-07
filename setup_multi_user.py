#!/usr/bin/env python3
"""
Setup Multi-User System for Existing Schools
Creates default users for all existing schools
"""

import sys
import os

# Add current directory to path 
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from school_database import SchoolDatabase
from multi_user_manager import SchoolUserManager

def setup_multi_user_for_existing_schools():
    """Create default users for all existing schools"""
    print("Setting up Multi-User System for Existing Schools")
    print("=" * 50)
    
    try:
        # Initialize database and user manager
        db = SchoolDatabase()
        user_manager = SchoolUserManager(db.db_path)
        
        # Get all schools
        schools = db.get_all_schools()
        
        if not schools:
            print("No schools found in database.")
            return False
        
        print(f"Found {len(schools)} schools")
        print()
        
        success_count = 0
        for school in schools:
            school_id = school['school_id']
            school_name = school['school_name']
            username = school['username']
            
            print(f"Processing: {school_name} (ID: {school_id})")
            
            # Check if users already exist for this school
            existing_users = user_manager.get_school_users(school_id)
            
            if existing_users:
                print(f"  ✓ Users already exist: {len(existing_users)} users")
                for user in existing_users:
                    print(f"    - {user['full_name']} ({user['username']}) - {user['role']}")
                print()
                continue
            
            # Create default users for this school
            print(f"  Creating default users...")
            if user_manager.create_default_users(school_id, school_name):
                print(f"  ✓ Successfully created 4 default users")
                success_count += 1
                
                # Show created users
                new_users = user_manager.get_school_users(school_id)
                for user in new_users:
                    print(f"    - {user['full_name']} ({user['username']})")
            else:
                print(f"  ✗ Failed to create default users")
            
            print()
        
        print("=" * 50)
        print(f"Multi-User Setup Complete!")
        print(f"Successfully set up users for {success_count}/{len(schools)} schools")
        
        if success_count > 0:
            print()
            print("Default User Credentials:")
            print("-" * 30)
            print("For each school, 4 users were created:")
            print("  • Form 1 Teacher: [SCHOOL_NAME]_form1 / Form1Teacher2024")
            print("  • Form 2 Teacher: [SCHOOL_NAME]_form2 / Form2Teacher2024") 
            print("  • Form 3 Teacher: [SCHOOL_NAME]_form3 / Form3Teacher2024")
            print("  • Form 4 Teacher: [SCHOOL_NAME]_form4 / Form4Teacher2024")
            print()
            print("Replace [SCHOOL_NAME] with the actual school name (lowercase, underscores for spaces)")
            print()
            print("Users can now login simultaneously without conflicts!")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_setup():
    """Verify that multi-user system is working"""
    print("\nVerifying Multi-User System Setup...")
    print("-" * 40)
    
    try:
        db = SchoolDatabase()
        user_manager = SchoolUserManager(db.db_path)
        
        schools = db.get_all_schools()
        
        for school in schools:
            school_id = school['school_id']
            school_name = school['school_name']
            
            users = user_manager.get_school_users(school_id)
            print(f"\n{school_name}:")
            print(f"  Total users: {len(users)}")
            
            for user in users:
                assigned_forms = user.get('assigned_forms', [])
                print(f"  - {user['full_name']}: Forms {assigned_forms}")
        
        print("\n✓ Multi-user system verification complete!")
        return True
        
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return False

if __name__ == "__main__":
    print("School Reporting System - Multi-User Setup")
    print("This script creates default users for existing schools")
    print()
    
    # Run setup
    success = setup_multi_user_for_existing_schools()
    
    if success:
        # Verify setup
        verify_setup()
        
        print("\n" + "=" * 50)
        print("NEXT STEPS:")
        print("1. Schools can now login with multiple user accounts")
        print("2. Each user is assigned to specific forms (1, 2, 3, 4)")
        print("3. Users can work simultaneously without conflicts")
        print("4. All users share the same school settings")
        print("5. System prevents data conflicts and tracks activity")
        print()
        print("Ready for multi-user concurrent data entry!")
    
    input("\nPress Enter to exit...")
