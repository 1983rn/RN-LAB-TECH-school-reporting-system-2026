
import sqlite3
import os

def check_settings():
    db_paths = ['school_reports.db', 'data/school_reports.db']
    for path in db_paths:
        if not os.path.exists(path):
            print(f"File not found: {path}")
            continue
            
        print(f"\n--- Checking {path} ---")
        try:
            conn = sqlite3.connect(path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Check school_settings
            cursor.execute("SELECT * FROM school_settings WHERE school_name LIKE '%Nanjati%'")
            rows = cursor.fetchall()
            if not rows:
                print("No Nanjati found in school_settings.")
                # Show all schools for context
                cursor.execute("SELECT school_id, school_name FROM schools")
                all_schools = cursor.fetchall()
                print(f"Available schools in this DB: {[dict(r) for r in all_schools]}")
            else:
                for row in rows:
                    print(f"Nanjati found: {dict(row)}")
            
            conn.close()
        except Exception as e:
            print(f"Error checking {path}: {e}")

if __name__ == "__main__":
    check_settings()
