#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from school_database import SchoolDatabase

def test_settings_read():
    """Test that settings are read correctly after update"""
    db = SchoolDatabase()
    
    print("=== TESTING SETTINGS READ ===\n")
    
    # Test for School ID 3 (FALLS COMMUNITY DAY SECONDARY SCHOOL)
    print("Testing School ID 3:")
    settings = db.get_school_settings(3)
    
    print(f"selected_term: '{settings.get('selected_term', 'NOT_FOUND')}'")
    print(f"selected_academic_year: '{settings.get('selected_academic_year', 'NOT_FOUND')}'")
    
    # Test for School ID 2 (FALLS CDSS)
    print("\nTesting School ID 2:")
    settings = db.get_school_settings(2)
    
    print(f"selected_term: '{settings.get('selected_term', 'NOT_FOUND')}'")
    print(f"selected_academic_year: '{settings.get('selected_academic_year', 'NOT_FOUND')}'")
    
    print("\n" + "=" * 50)
    print("If the settings show 'Term 3' and '2025-2026', then the issue is resolved!")
    print("If they show 'To be announced' or empty, then there's still a caching issue.")

if __name__ == "__main__":
    test_settings_read()
