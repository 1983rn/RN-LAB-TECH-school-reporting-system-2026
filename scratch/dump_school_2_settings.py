
import sqlite3
import os

def dump_settings():
    path = 'data/school_reports.db'
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return
        
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM school_settings WHERE school_id = 2 ORDER BY setting_id DESC")
    rows = cursor.fetchall()
    print(f"Found {len(rows)} settings for school_id=2")
    for row in rows:
        d = dict(row)
        print(f"ID: {d['setting_id']}, Name: {d['school_name']}, Address: {repr(d['school_address'])}")
    
    conn.close()

if __name__ == "__main__":
    dump_settings()
