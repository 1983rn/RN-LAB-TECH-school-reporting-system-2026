import sqlite3

def find_nanjati():
    try:
        conn = sqlite3.connect('school_reports.db')
        cursor = conn.cursor()
        cursor.execute("SELECT school_id, school_name FROM schools WHERE school_name LIKE '%Nanjati%';")
        rows = cursor.fetchall()
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_nanjati()
