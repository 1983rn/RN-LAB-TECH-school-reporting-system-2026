import os
import sys

# Add project root to path
sys.path.insert(0, r'd:\2025-2026\PRODUCTION\USA\RN-LAB-TECH-school-reporting-system-2026-1')

import pandas as pd
from school_database import SchoolDatabase

def test_duplicate_logic():
    excel_path = r'd:\2025-2026\PRODUCTION\USA\RN-LAB-TECH-school-reporting-system-2026-1\scratch\students_test.xlsx'
    
    # Create the file again just in case
    df = pd.DataFrame({'First Name': ['John', 'Jane', 'Alice'], 'Last Name': ['Doe', 'Smith', 'Brown']})
    df.to_excel(excel_path, index=False)
    
    db = SchoolDatabase()
    school_id = 1
    form_level = 1
    
    # Pre-populate some students to create duplicates
    print("Pre-populating students...")
    db.add_student({'first_name': 'John', 'last_name': 'Doe', 'grade_level': form_level}, school_id)
    
    # Get existing names
    existing_students = db.get_students_by_grade(form_level, school_id)
    existing_names = set(f"{s['first_name'].lower().strip()} {s['last_name'].lower().strip()}" for s in existing_students)
    print("Existing names in DB:", existing_names)
    
    # 1. Test "Skip Duplicates" logic
    print("\nTesting 'skip' action...")
    duplicate_action = 'skip'
    rows_to_process = [
        {'first_name': 'John', 'last_name': 'Doe', 'is_duplicate': ('john doe' in existing_names)},
        {'first_name': 'New', 'last_name': 'Student', 'is_duplicate': False}
    ]
    
    added_count = 0
    for row in rows_to_process:
        if row['is_duplicate'] and duplicate_action == 'skip':
            print(f"Skipping duplicate: {row['first_name']} {row['last_name']}")
            continue
        print(f"Adding: {row['first_name']} {row['last_name']}")
        added_count += 1
    
    print(f"Added {added_count} students with 'skip' action (Expected: 1)")
    
    # 2. Test "Maintain" logic
    print("\nTesting 'maintain' action...")
    duplicate_action = 'maintain'
    added_count = 0
    for row in rows_to_process:
        if row['is_duplicate'] and duplicate_action == 'skip':
            print(f"Skipping duplicate: {row['first_name']} {row['last_name']}")
            continue
        print(f"Adding: {row['first_name']} {row['last_name']}")
        added_count += 1
        
    print(f"Added {added_count} students with 'maintain' action (Expected: 2)")

    print("\nVerification complete.")

if __name__ == "__main__":
    test_duplicate_logic()
