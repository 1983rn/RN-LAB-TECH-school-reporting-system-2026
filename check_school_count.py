#!/usr/bin/env python3
"""
Check how many schools are registered in the application
"""

import sqlite3
import os

def check_school_count():
    try:
        # Connect to the database
        db_path = "school_reports.db"
        if not os.path.exists(db_path):
            print(f"Database file {db_path} not found!")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if schools table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schools';")
        schools_table = cursor.fetchone()
        
        if schools_table:
            print("Schools table found!")
            
            # Check table structure first
            cursor.execute("PRAGMA table_info(schools);")
            columns = cursor.fetchall()
            print(f"Schools table columns: {[col[1] for col in columns]}")
            
            # Get all schools
            cursor.execute("SELECT * FROM schools ORDER BY school_id;")
            schools = cursor.fetchall()
            
            print(f"\nTotal schools registered: {len(schools)}")
            print("\nSchool Details:")
            print("-" * 80)
            
            for school in schools:
                print(f"ID: {school[0]}")
                print(f"Name: {school[1]}")
                print(f"Username: {school[2]}")
                print(f"Status: {school[4]}")
                print(f"Created: {school[6]}")
                print(f"Subscription: {school[7]}")
                print(f"Days Remaining: {school[11]}")
                print("-" * 40)
                
        else:
            print("No 'schools' table found in the database!")
            
            # Show all tables to help understand the structure
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"\nAvailable tables: {[table[0] for table in tables]}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking school count: {e}")

if __name__ == "__main__":
    check_school_count()
