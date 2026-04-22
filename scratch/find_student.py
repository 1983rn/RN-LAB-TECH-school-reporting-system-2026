import sqlite3

def find_nanjati_student():
    try:
        conn = sqlite3.connect('school_reports.db')
        cursor = conn.cursor()
        cursor.execute("SELECT student_id, first_name, last_name FROM students WHERE school_id = 2 LIMIT 1;")
        row = cursor.fetchone()
        if row:
            print(f"ID: {row[0]}, Name: {row[1]} {row[2]}")
        else:
            print("No students found for Nanjati.")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_nanjati_student()
