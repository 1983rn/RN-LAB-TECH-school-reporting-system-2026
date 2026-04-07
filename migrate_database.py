#!/usr/bin/env python3
"""
Database Migration Script for Persistent Storage
Copies existing database to persistent storage location
"""

import os
import shutil
import sys

def migrate_database():
    """Copy existing database to persistent storage"""
    source_db = "school_reports.db"
    target_db = os.environ.get('DATABASE_PATH', 'school_reports.db')
    
    # Only migrate if we're using persistent storage and source exists
    if target_db != 'school_reports.db' and os.path.exists(source_db):
        # Ensure target directory exists
        os.makedirs(os.path.dirname(target_db), exist_ok=True)
        
        # Copy database if target doesn't exist
        if not os.path.exists(target_db):
            shutil.copy2(source_db, target_db)
            print(f"✅ Migrated database from {source_db} to {target_db}")
        else:
            print(f"ℹ️ Database already exists at {target_db}")
    else:
        print("ℹ️ No migration needed")

if __name__ == "__main__":
    migrate_database()