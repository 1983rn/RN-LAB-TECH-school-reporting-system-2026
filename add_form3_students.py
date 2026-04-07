#!/usr/bin/env python3
"""
Add Form 3 students to the database
"""

import sqlite3

def add_form3_students():
    try:
        conn = sqlite3.connect('school_reports.db')
        cursor = conn.cursor()
        
        # Sample Form 3 students
        form3_students = [
            ('Alice', 'Banda', '2008-03-15'),
            ('Brian', 'Chikwanha', '2008-07-22'),
            ('Catherine', 'Mwale', '2008-01-10'),
            ('David', 'Phiri', '2008-09-05'),
            ('Elizabeth', 'Tembo', '2008-11-18'),
            ('Francis', 'Kamoto', '2008-04-30'),
            ('Grace', 'Nyirenda', '2008-08-12'),
            ('Henry', 'Zulu', '2008-02-28'),
            ('Ivy', 'Chirwa', '2008-06-14'),
            ('James', 'Mvula', '2008-12-03')
        ]
        
        # Get next student number
        cursor.execute("SELECT MAX(CAST(student_number AS INTEGER)) FROM students")
        max_num = cursor.fetchone()[0]
        next_num = (max_num + 1) if max_num else 1
        
        print("Adding Form 3 students...")
        for i, (first_name, last_name, dob) in enumerate(form3_students):
            student_number = f"{next_num + i:04d}"
            cursor.execute("""
                INSERT INTO students (
                    student_number, first_name, last_name, date_of_birth,
                    grade_level, status
                ) VALUES (?, ?, ?, ?, 3, 'Active')
            """, (student_number, first_name, last_name, dob))
            print(f"   Added: {first_name} {last_name} (#{student_number})")
        
        conn.commit()
        print(f"\n✅ Successfully added {len(form3_students)} Form 3 students!")
        
        # Verify the addition
        cursor.execute("SELECT COUNT(*) FROM students WHERE grade_level = 3")
        count = cursor.fetchone()[0]
        print(f"Total Form 3 students now: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    add_form3_students()
