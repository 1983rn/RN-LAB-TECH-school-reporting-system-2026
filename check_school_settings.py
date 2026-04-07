#!/usr/bin/env python3

import sqlite3
import os

def check_school_settings():
    """Check what's in the school_settings table"""
    db_path = "data/school_reports.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== SCHOOL_SETTINGS TABLE ===\n")
    
    cursor.execute("SELECT name, value FROM school_settings")
    settings = cursor.fetchall()
    
    print("Setting\tValue")
    print("-" * 50)
    for name, value in settings:
        print(f"{name}\t{value}")
    
    conn.close()

if __name__ == "__main__":
    check_school_settings()
