#!/usr/bin/env python3

import sqlite3
import os

def fix_school_settings():
    """Fix school settings to use correct term"""
    db_path = "data/school_reports.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== FIXING SCHOOL SETTINGS ===\n")
    
    # Update School ID 3 (FALLS COMMUNITY DAY SECONDARY SCHOOL) to use Term 3
    cursor.execute("""
        UPDATE school_settings 
        SET selected_term = 'Term 3'
        WHERE school_id = 3
    """)
    
    # Update School ID 2 (FALLS CDSS) to use Term 3  
    cursor.execute("""
        UPDATE school_settings 
        SET selected_term = 'Term 3'
        WHERE school_id = 2
    """)
    
    # Update academic year to 2025-2026 for both schools
    cursor.execute("""
        UPDATE school_settings 
        SET selected_academic_year = '2025-2026'
        WHERE school_id IN (2, 3)
    """)
    
    updated_count = cursor.rowcount
    print(f"Updated {updated_count} school settings")
    
    # Verify the update
    cursor.execute("""
        SELECT school_id, school_name, selected_term, selected_academic_year 
        FROM school_settings 
        WHERE school_id IN (2, 3)
    """)
    
    schools = cursor.fetchall()
    print("\nUpdated school settings:")
    print("School ID\tSchool Name\t\tTerm\t\tYear")
    print("-" * 60)
    for school in schools:
        school_id, school_name, selected_term, selected_academic_year = school
        print(f"{school_id}\t{school_name}\t{selected_term}\t{selected_academic_year}")
    
    conn.commit()
    conn.close()
    
    print(f"\nSchool settings updated successfully!")
    print("Now the data Entry interface should show correct positions")

if __name__ == "__main__":
    fix_school_settings()
