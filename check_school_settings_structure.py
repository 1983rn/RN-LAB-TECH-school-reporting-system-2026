#!/usr/bin/env python3

import sqlite3
import os

def check_school_settings_structure():
    """Check structure of school_settings table"""
    db_path = "data/school_reports.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== SCHOOL_SETTINGS TABLE STRUCTURE ===\n")
    
    cursor.execute("PRAGMA table_info(school_settings)")
    columns = cursor.fetchall()
    
    print("Columns in school_settings table:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Try to get some data
    cursor.execute("SELECT * FROM school_settings LIMIT 5")
    try:
        settings = cursor.fetchall()
        print(f"\nSample data ({len(settings)} rows):")
        for row in settings:
            print(f"  {row}")
    except Exception as e:
        print(f"Error getting data: {e}")
    
    conn.close()

if __name__ == "__main__":
    check_school_settings_structure()
