import sqlite3

def check_schema():
    conn = sqlite3.connect('school_reports.db')
    cursor = conn.cursor()
    
    print("--- Table SQL ---")
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='student_marks'")
    row = cursor.fetchone()
    if row:
        print(row[0])
    else:
        print("Table 'student_marks' not found.")
    
    print("\n--- Indices ---")
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name='student_marks'")
    for row in cursor.fetchall():
        print(row[0])
        
    conn.close()

if __name__ == "__main__":
    check_schema()
