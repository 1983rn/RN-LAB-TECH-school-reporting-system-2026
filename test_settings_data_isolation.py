#!/usr/bin/env python3
"""
Test script to verify Settings page data isolation between schools
Ensures newly registered schools have blank fields and no data leakage
"""

import os
import sys
import json

# Add current directory to path 
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from school_database import SchoolDatabase

def test_settings_data_isolation():
    """Test Settings page data isolation and blank fields for new schools"""
    
    print("=== Testing Settings Page Data Isolation ===")
    
    # Initialize database
    db = SchoolDatabase()
    
    try:
        # Step 1: Check existing schools and their settings
        print("\n1. Checking existing schools and their settings...")
        
        all_schools = db.get_all_schools()
        print(f"Total schools in database: {len(all_schools)}")
        
        for school in all_schools:
            school_id = school['school_id']
            school_name = school['school_name']
            
            print(f"\n--- School {school_id}: {school_name} ---")
            
            # Get settings for this school
            settings = db.get_school_settings(school_id)
            
            # Check if fields are blank for new schools or have data for existing schools
            critical_fields = ['school_name', 'school_address', 'school_phone', 'school_email', 
                             'next_term_begins', 'boys_uniform', 'girls_uniform', 'boarding_fee']
            
            blank_count = 0
            filled_count = 0
            
            for field in critical_fields:
                value = settings.get(field, '')
                if value == '' or value is None:
                    blank_count += 1
                    print(f"  {field}: [BLANK]")
                else:
                    filled_count += 1
                    print(f"  {field}: {value}")
            
            print(f"  Summary: {filled_count} filled, {blank_count} blank fields")
            
            # Check for potential data leakage - all critical fields should be blank for new schools
            if school_id > 2:  # Assume schools with ID > 2 are newer
                if filled_count > 0:
                    print(f"  ** WARNING: New school {school_id} has pre-filled data - potential data leakage! **")
                else:
                    print(f"  ** OK: New school {school_id} has all blank fields as expected **")
        
        # Step 2: Test creating a new school with blank settings
        print(f"\n2. Testing new school creation with blank settings...")
        
        # Create test school data
        test_school_data = {
            'school_name': 'Test School for Settings Isolation',
            'username': 'test_settings_isolation',
            'password': 'test123'
        }
        
        # Add the school
        new_school_id = db.add_school(test_school_data)
        print(f"Created test school with ID: {new_school_id}")
        
        # Check settings immediately after creation
        new_school_settings = db.get_school_settings(new_school_id)
        
        print(f"Settings for new school {new_school_id}:")
        critical_fields = ['school_name', 'school_address', 'school_phone', 'school_email', 
                          'next_term_begins', 'boys_uniform', 'girls_uniform', 'boarding_fee']
        
        all_blank = True
        for field in critical_fields:
            value = new_school_settings.get(field, '')
            if value == '' or value is None:
                print(f"  {field}: [BLANK] - OK")
            else:
                print(f"  {field}: {value} - ** DATA LEAKAGE DETECTED! **")
                all_blank = False
        
        if all_blank:
            print(f"  ** SUCCESS: All fields are blank for newly registered school **")
        else:
            print(f"  ** FAILURE: Data leakage detected in newly registered school **")
        
        # Step 3: Test data isolation between schools
        print(f"\n3. Testing data isolation between schools...")
        
        if len(all_schools) >= 2:
            # Get settings from two different schools
            school1 = all_schools[0]
            school2 = all_schools[1] if len(all_schools) > 1 else all_schools[0]
            
            settings1 = db.get_school_settings(school1['school_id'])
            settings2 = db.get_school_settings(school2['school_id'])
            
            print(f"Comparing settings between School {school1['school_id']} and School {school2['school_id']}")
            
            # Check if settings are different (they should be!)
            different_fields = []
            same_fields = []
            
            for field in critical_fields:
                value1 = settings1.get(field, '')
                value2 = settings2.get(field, '')
                
                if value1 != value2:
                    different_fields.append(field)
                    print(f"  {field}: Different (School1: '{value1}' vs School2: '{value2}') - OK")
                else:
                    same_fields.append(field)
                    if value1 != '':  # Only flag as issue if not blank
                        print(f"  {field}: Same non-empty value ('{value1}') - ** POTENTIAL DATA LEAKAGE **")
                    else:
                        print(f"  {field}: Same blank value - OK")
            
            if len(same_fields) == 0:
                print(f"  ** SUCCESS: All school settings are properly isolated **")
            else:
                non_blank_same = [f for f in same_fields if settings1.get(f, '') != '']
                if len(non_blank_same) > 0:
                    print(f"  ** FAILURE: Data leakage detected in fields: {non_blank_same} **")
                else:
                    print(f"  ** OK: Same fields are all blank (no data leakage) **")
        
        # Step 4: Test Settings page template rendering
        print(f"\n4. Testing Settings page template rendering...")
        
        # Simulate what the Settings page route does
        for school in all_schools[:3]:  # Test first 3 schools
            school_id = school['school_id']
            school_name = school['school_name']
            
            print(f"\n--- Template rendering for School {school_id}: {school_name} ---")
            
            # Get settings like the route does
            settings_obj = db.get_school_settings(school_id)
            
            # Simulate template rendering logic
            template_values = {}
            for field in ['school_name', 'school_address', 'school_phone', 'school_email']:
                template_value = settings_obj.get(field) if settings_obj and settings_obj.get(field) is not None and settings_obj.get(field) else ''
                template_values[field] = template_value
                print(f"  Template field '{field}': '{template_value}'")
            
            # Check if template would render blank fields correctly
            all_template_blank = all(value == '' for value in template_values.values())
            if school_id > 2 and all_template_blank:
                print(f"  ** OK: Template renders blank fields for new school **")
            elif school_id <= 2 and not all_template_blank:
                print(f"  ** OK: Template renders data for existing school **")
            elif school_id > 2 and not all_template_blank:
                print(f"  ** WARNING: Template shows data for new school - potential issue **")
        
        # Step 5: Clean up test data
        print(f"\n5. Cleaning up test data...")
        
        # Remove the test school we created
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM school_settings WHERE school_id = ?", (new_school_id,))
                cursor.execute("DELETE FROM schools WHERE school_id = ?", (new_school_id,))
                conn.commit()
            print(f"Removed test school {new_school_id}")
        except Exception as e:
            print(f"Error cleaning up test school: {e}")
        
        print("\n" + "="*60)
        print("SETTINGS DATA ISOLATION TEST COMPLETE")
        
        print(f"\nTest Results Summary:")
        print(f"  - Total schools tested: {len(all_schools)}")
        print(f"  - New school blank fields: {'VERIFIED' if all_blank else 'FAILED'}")
        print(f"  - Data isolation between schools: {'VERIFIED' if len(all_schools) < 2 or len(different_fields) > 0 else 'NEEDS REVIEW'}")
        # Check template rendering for each school
        template_rendering_ok = True
        for school in all_schools[:3]:
            school_id = school['school_id']
            settings = db.get_school_settings(school_id)
            all_blank = all(settings.get(field, '') == '' for field in critical_fields)
            
            if school_id > 2 and not all_blank:
                template_rendering_ok = False
                break
        
        print(f"  - Template rendering: {'VERIFIED' if template_rendering_ok else 'FAILED'}")
        
        print(f"\nRecommendations:")
        print(f"1. Ensure all newly registered schools have blank School Information fields")
        print(f"2. Verify school_id-based isolation in all database queries")
        print(f"3. Test Settings page with different school user sessions")
        print(f"4. Confirm no cross-school data contamination in templates")
        
    except Exception as e:
        print(f"\n** Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_settings_data_isolation()
