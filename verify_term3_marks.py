#!/usr/bin/env python3
"""
Verify Term 3 marks are present for Forms 1 and 3
"""

from school_database import SchoolDatabase

def verify_term3_marks():
    db = SchoolDatabase()
    
    print("=== VERIFICATION: Term 3 2024-2025 Marks ===\n")
    
    # Check Form 1 students
    form1_students = db.get_students_by_grade(1)
    print(f"Form 1 Students: {len(form1_students)} found")
    
    if form1_students:
        # Show marks for first 3 Form 1 students
        for i, student in enumerate(form1_students[:3]):
            student_id = student['student_id']
            marks = db.get_student_marks(student_id, 'Term 3', '2024-2025')
            print(f"\n{student['first_name']} {student['last_name']} (Form 1):")
            if marks:
                for subject, data in marks.items():
                    print(f"  {subject}: {data['mark']} ({data['grade']})")
            else:
                print("  No marks found")
    
    # Check Form 3 students  
    form3_students = db.get_students_by_grade(3)
    print(f"\nForm 3 Students: {len(form3_students)} found")
    
    if form3_students:
        # Show marks for first 3 Form 3 students
        for i, student in enumerate(form3_students[:3]):
            student_id = student['student_id']
            marks = db.get_student_marks(student_id, 'Term 3', '2024-2025')
            print(f"\n{student['first_name']} {student['last_name']} (Form 3):")
            if marks:
                for subject, data in marks.items():
                    print(f"  {subject}: {data['mark']} ({data['grade']})")
            else:
                print("  No marks found")
    
    # Summary count
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.grade_level, COUNT(*) as mark_count, COUNT(DISTINCT s.student_id) as student_count
                FROM student_marks sm
                JOIN students s ON sm.student_id = s.student_id
                WHERE sm.term = 'Term 3' AND sm.academic_year = '2024-2025'
                AND s.grade_level IN (1, 3)
                GROUP BY s.grade_level
                ORDER BY s.grade_level
            """)
            
            results = cursor.fetchall()
            print(f"\n=== SUMMARY ===")
            for form_level, mark_count, student_count in results:
                subjects_per_student = mark_count // student_count if student_count > 0 else 0
                print(f"Form {form_level}: {student_count} students, {mark_count} total marks ({subjects_per_student} subjects per student)")
                
    except Exception as e:
        print(f"Error getting summary: {e}")

if __name__ == "__main__":
    verify_term3_marks()