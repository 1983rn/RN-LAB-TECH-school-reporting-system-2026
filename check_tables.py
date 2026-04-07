#!/usr/bin/env python3

import sqlite3
import os

def check_tables():
    """Check what tables exist in database"""
    db_path = "data/school_reports.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== DATABASE TABLES ===\n")
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("Tables in database:")
    for table in tables:
        print(f"  - {table[0]}")
    
    conn.close()

if __name__ == "__main__":
    check_tables()
