#!/usr/bin/env python3
"""
Debug script to find the source of template data in school settings
"""

import os
import sys

# Add current directory to path 
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from school_database import SchoolDatabase

def debug_settings_data_source():
    """Debug where template data is coming from in school settings"""
    
    print("=== Debugging Settings Data Source ===")
    
    # Initialize database
    db = SchoolDatabase()
    
    try:
        # Step 1: Check the raw database data for problematic schools
        print("\n1. Checking raw database data...")
        
        problematic_schools = [9, 10, 11, 12, 13]  # Schools with template data
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            for school_id in problematic_schools:
                print(f"\n--- School {school_id} Raw Data ---")
                
                # Check schools table
                cursor.execute("SELECT * FROM schools WHERE school_id = ?", (school_id,))
                school_row = cursor.fetchone()
                if school_row:
                    columns = [description[0] for description in cursor.description]
                    school_data = dict(zip(columns, school_row))
                    print(f"Schools table: {school_data}")
                
                # Check school_settings table
                cursor.execute("SELECT * FROM school_settings WHERE school_id = ?", (school_id,))
                settings_row = cursor.fetchone()
                if settings_row:
                    columns = [description[0] for description in cursor.description]
                    settings_data = dict(zip(columns, settings_row))
                    print(f"Settings table: {settings_data}")
                    
                    # Check for any non-empty fields
                    for key, value in settings_data.items():
                        if value and key not in ['setting_id', 'school_id', 'updated_date']:
                            print(f"  {key}: '{value}'")
                else:
                    print("No settings found in school_settings table")
        
        # Step 2: Check if there's any trigger or default value in the database
        print(f"\n2. Checking database schema for defaults...")
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check school_settings table schema
            cursor.execute("PRAGMA table_info(school_settings)")
            columns = cursor.fetchall()
            print(f"school_settings table schema:")
            for col in columns:
                print(f"  {col}")
            
            # Check for any triggers
            cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger' AND tbl_name='school_settings'")
            triggers = cursor.fetchall()
            if triggers:
                print(f"\nTriggers on school_settings:")
                for trigger in triggers:
                    print(f"  {trigger}")
            else:
                print(f"\nNo triggers found on school_settings table")
        
        # Step 3: Check if there's any code that might be inserting template data
        print(f"\n3. Checking for template data insertion...")
        
        # Look for the specific template values in the codebase
        template_values = [
            "P.O. Box [NUMBER], [CITY], Malawi",
            "+265 [PHONE NUMBER]",
            "To be announced",
            "White shirt, black trousers, black shoes",
            "White blouse, black skirt, black shoes"
        ]
        
        for template_value in template_values:
            print(f"\nSearching for: '{template_value}'")
            
            # Search in app.py
            try:
                with open('app.py', 'r', encoding='utf-8') as f:
                    content = f.read()
                    if template_value in content:
                        print(f"  Found in app.py!")
                        # Find line numbers
                        lines = content.split('\n')
                        for i, line in enumerate(lines, 1):
                            if template_value in line:
                                print(f"    Line {i}: {line.strip()}")
            except:
                pass
            
            # Search in school_database.py
            try:
                with open('school_database.py', 'r', encoding='utf-8') as f:
                    content = f.read()
                    if template_value in content:
                        print(f"  Found in school_database.py!")
                        # Find line numbers
                        lines = content.split('\n')
                        for i, line in enumerate(lines, 1):
                            if template_value in line:
                                print(f"    Line {i}: {line.strip()}")
            except:
                pass
        
        # Step 4: Check if there's any initialization script or migration
        print(f"\n4. Checking for initialization scripts...")
        
        import glob
        init_files = glob.glob("*.sql") + glob.glob("init*") + glob.glob("migrate*") + glob.glob("setup*")
        if init_files:
            print(f"Found initialization files: {init_files}")
            for file in init_files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for template_value in template_values:
                            if template_value in content:
                                print(f"  Found template data in {file}")
                except:
                    pass
        else:
            print("No initialization files found")
        
        # Step 5: Check recent database operations
        print(f"\n5. Checking if there's any recent bulk update...")
        
        # Let's manually create a new school and trace what happens
        print(f"\nCreating a test school to trace the process...")
        
        test_school_data = {
            'school_name': 'Debug Test School',
            'username': 'debug_test_school',
            'password': 'test123'
        }
        
        # Add school
        new_school_id = db.add_school(test_school_data)
        print(f"Created test school with ID: {new_school_id}")
        
        # Check settings immediately
        settings_before = db.get_school_settings(new_school_id)
        print(f"Settings immediately after creation:")
        for field in ['school_name', 'school_address', 'school_phone', 'school_email']:
            value = settings_before.get(field, '')
            print(f"  {field}: '{value}'")
        
        # Now call update_school_settings with blank data (like the registration does)
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
        
        db.update_school_settings(blank_settings, new_school_id)
        
        # Check settings after update
        settings_after = db.get_school_settings(new_school_id)
        print(f"Settings after blank update:")
        for field in ['school_name', 'school_address', 'school_phone', 'school_email']:
            value = settings_after.get(field, '')
            print(f"  {field}: '{value}'")
        
        # Clean up
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM school_settings WHERE school_id = ?", (new_school_id,))
            cursor.execute("DELETE FROM schools WHERE school_id = ?", (new_school_id,))
            conn.commit()
        print(f"Cleaned up test school {new_school_id}")
        
        print("\n" + "="*60)
        print("DEBUGGING COMPLETE")
        
    except Exception as e:
        print(f"\n** Debug failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_settings_data_source()
