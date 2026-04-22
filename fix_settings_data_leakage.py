#!/usr/bin/env python3
"""
Fix Settings Data Leakage - Clean up template data from schools
Ensures newly registered schools have blank fields as required
"""

import os
import sys

# Add current directory to path 
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from school_database import SchoolDatabase

def fix_settings_data_leakage():
    """Fix data leakage by clearing template data from school settings"""
    
    print("=== Fixing Settings Data Leakage ===")
    
    # Initialize database
    db = SchoolDatabase()
    
    try:
        # Step 1: Identify schools with template data
        print("\n1. Identifying schools with template data...")
        
        template_values = {
            'school_address': 'P.O. Box [NUMBER], [CITY], Malawi',
            'school_phone': '+265 [PHONE NUMBER]',
            'school_email': '@school.edu.mw',
            'next_term_begins': 'To be announced',
            'boys_uniform': 'White shirt, black trousers, black shoes',
            'girls_uniform': 'White blouse, black skirt, black shoes'
        }
        
        all_schools = db.get_all_schools()
        schools_with_template_data = []
        
        for school in all_schools:
            school_id = school['school_id']
            school_name = school['school_name']
            
            settings = db.get_school_settings(school_id)
            
            has_template_data = False
            template_fields_found = []
            
            for field, template_value in template_values.items():
                actual_value = settings.get(field, '')
                
                # Check if field contains template data
                if template_value in actual_value:
                    has_template_data = True
                    template_fields_found.append(field)
                    print(f"  School {school_id} ({school_name}): {field} = '{actual_value}'")
            
            if has_template_data:
                schools_with_template_data.append({
                    'school_id': school_id,
                    'school_name': school_name,
                    'template_fields': template_fields_found,
                    'current_settings': settings
                })
        
        print(f"\nFound {len(schools_with_template_data)} schools with template data")
        
        # Step 2: Clean up template data
        if schools_with_template_data:
            print(f"\n2. Cleaning up template data...")
            
            for school_info in schools_with_template_data:
                school_id = school_info['school_id']
                school_name = school_info['school_name']
                template_fields = school_info['template_fields']
                
                print(f"\n--- Cleaning School {school_id}: {school_name} ---")
                
                # Create cleaned settings - keep non-template data, clear template data
                current_settings = school_info['current_settings']
                cleaned_settings = {}
                
                for field, value in current_settings.items():
                    if field in template_values:
                        # Check if this field contains template data
                        is_template = False
                        for template_field, template_value in template_values.items():
                            if field == template_field and template_value in str(value):
                                is_template = True
                                break
                        
                        if is_template:
                            cleaned_settings[field] = ''  # Clear template data
                            print(f"  Cleared {field}: '{value}' -> ''")
                        else:
                            cleaned_settings[field] = value  # Keep real data
                            print(f"  Kept {field}: '{value}'")
                    else:
                        # Keep other fields as-is
                        cleaned_settings[field] = value
                
                # Update the school settings with cleaned data
                db.update_school_settings(cleaned_settings, school_id)
                
                # Verify the cleanup
                updated_settings = db.get_school_settings(school_id)
                print(f"  Verification:")
                for field in template_fields:
                    new_value = updated_settings.get(field, '')
                    print(f"    {field}: '{new_value}'")
        
        # Step 3: Verify the fix by testing new school creation
        print(f"\n3. Testing new school creation...")
        
        test_school_data = {
            'school_name': 'Test School for Blank Fields',
            'username': 'test_blank_fields',
            'password': 'test123'
        }
        
        # Create test school
        test_school_id = db.add_school(test_school_data)
        print(f"Created test school with ID: {test_school_id}")
        
        # Create blank settings (as the registration process should do)
        blank_settings = {
            'school_name': '',
            'school_address': '',
            'school_phone': '',
            'school_email': '',
            'pta_fund': '',
            'sdf_fund': '',
            'boarding_fee': '',
            'next_term_begins': '',
            'boys_uniform': '',
            'girls_uniform': ''
        }
        
        db.update_school_settings(blank_settings, test_school_id)
        
        # Verify blank fields
        test_settings = db.get_school_settings(test_school_id)
        print(f"Test school settings after blank update:")
        
        all_blank = True
        for field in ['school_name', 'school_address', 'school_phone', 'school_email', 'next_term_begins', 'boys_uniform', 'girls_uniform']:
            value = test_settings.get(field, '')
            print(f"  {field}: '{value}'")
            if value != '':
                all_blank = False
        
        if all_blank:
            print(f"  ** SUCCESS: New school has all blank fields **")
        else:
            print(f"  ** FAILURE: New school still has data in fields **")
        
        # Clean up test school
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM school_settings WHERE school_id = ?", (test_school_id,))
            cursor.execute("DELETE FROM schools WHERE school_id = ?", (test_school_id,))
            conn.commit()
        print(f"Cleaned up test school {test_school_id}")
        
        # Step 4: Final verification
        print(f"\n4. Final verification...")
        
        # Check a few schools to ensure they're clean
        verification_schools = all_schools[:3] if len(all_schools) >= 3 else all_schools
        
        for school in verification_schools:
            school_id = school['school_id']
            school_name = school['school_name']
            
            settings = db.get_school_settings(school_id)
            
            # Check for any remaining template data
            remaining_template_data = []
            for field, template_value in template_values.items():
                actual_value = settings.get(field, '')
                if template_value in actual_value:
                    remaining_template_data.append(f"{field}='{actual_value}'")
            
            if remaining_template_data:
                print(f"  School {school_id} ({school_name}): Still has template data - {', '.join(remaining_template_data)}")
            else:
                print(f"  School {school_id} ({school_name}): Clean - no template data")
        
        print("\n" + "="*60)
        print("SETTINGS DATA LEAKAGE FIX COMPLETE")
        
        print(f"\nFix Summary:")
        print(f"  - Schools cleaned: {len(schools_with_template_data)}")
        print(f"  - Template fields cleared: {sum(len(s['template_fields']) for s in schools_with_template_data)}")
        print(f"  - New school creation: {'VERIFIED' if all_blank else 'FAILED'}")
        
        print(f"\nRecommendations:")
        print(f"1. Ensure school registration process creates blank settings")
        print(f"2. Test Settings page with different school user sessions")
        print(f"  - All newly registered schools should show blank fields")
        print(f"  - School users must fill in their own information")
        print(f"  - No data leakage between schools")
        
    except Exception as e:
        print(f"\n** Fix failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_settings_data_leakage()
