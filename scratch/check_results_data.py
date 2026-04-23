
import os
import sys
import json
from school_database import SchoolDatabase

def check_results():
    db = SchoolDatabase()
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT form, total_students FROM student_results LIMIT 5")
        rows = cursor.fetchall()
        print("Student Results (form, total_students):")
        for row in rows:
            print(row)

if __name__ == "__main__":
    check_results()
