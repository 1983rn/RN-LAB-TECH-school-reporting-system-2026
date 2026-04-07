#!/usr/bin/env python3
"""
Test positioning for NANJATI students in Term 1 2025-2026
Verify both overall position and subject positions are working
"""

from school_database import SchoolDatabase

def test_positioning():
    """Test positioning for NANJATI students"""
    
    db = SchoolDatabase()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Find NANJATI school
            cursor.execute("""
                SELECT school_id, school_name FROM schools 
                WHERE school_name LIKE '%NANJATI%'
            """)
            school_info = cursor.fetchone()
            
            if not school_info:
                print("NANJATI school not found")
                return
            
            school_id, school_name = school_info
            print(f"Testing positioning for: {school_name} (ID: {school_id})")
            
            # Get Form 1 students with marks in Term 1 2025-2026
            cursor.execute("""
                SELECT DISTINCT s.student_id, s.first_name, s.last_name, s.grade_level
                FROM students s
                JOIN student_marks sm ON s.student_id = sm.student_id
                WHERE s.school_id = ? AND s.grade_level = 1 
                AND sm.term = 'Term 1' AND sm.academic_year = '2025-2026'
                ORDER BY s.first_name, s.last_name
                LIMIT 5
            """, (school_id,))
            
            students = cursor.fetchall()
            print(f"\nFound {len(students)} Form 1 students with marks")
            
            for student_id, first_name, last_name, grade_level in students:
                print(f"\n=== {first_name} {last_name} ===")
                
                # Test overall position
                position_data = db.get_student_position_and_points(
                    student_id, 'Term 1', '2025-2026', grade_level, school_id
                )
                print(f"Overall Position: {position_data['position']}/{position_data['total_students']}")
                
                # Test subject positions
                subjects = ['English', 'Mathematics', 'Biology', 'Chemistry']
                for subject in subjects:
                    subject_pos = db.get_subject_position(
                        student_id, subject, 'Term 1', '2025-2026', grade_level, school_id
                    )
                    print(f"{subject} Position: {subject_pos}")
            
            # Test Form 2 students with Bible Knowledge only
            print(f"\n{'='*50}")
            print("FORM 2 STUDENTS (Bible Knowledge only)")
            print(f"{'='*50}")
            
            cursor.execute("""
                SELECT DISTINCT s.student_id, s.first_name, s.last_name, s.grade_level
                FROM students s
                JOIN student_marks sm ON s.student_id = sm.student_id
                WHERE s.school_id = ? AND s.grade_level = 2 
                AND sm.term = 'Term 1' AND sm.academic_year = '2025-2026'
                AND sm.subject = 'Bible Knowledge'
                ORDER BY s.first_name, s.last_name
                LIMIT 3
            """, (school_id,))
            
            form2_students = cursor.fetchall()
            print(f"Found {len(form2_students)} Form 2 students with Bible Knowledge marks")
            
            for student_id, first_name, last_name, grade_level in form2_students:
                print(f"\n=== {first_name} {last_name} ===")
                
                # Test Bible Knowledge position
                bible_pos = db.get_subject_position(
                    student_id, 'Bible Knowledge', 'Term 1', '2025-2026', grade_level, school_id
                )
                print(f"Bible Knowledge Position: {bible_pos}")
                
                # Check marks
                cursor.execute("""
                    SELECT subject, mark, grade FROM student_marks
                    WHERE student_id = ? AND term = 'Term 1' AND academic_year = '2025-2026'
                """, (student_id,))
                marks = cursor.fetchall()
                print(f"Subjects taken: {len(marks)}")
                for subject, mark, grade in marks:
                    print(f"  - {subject}: {mark} ({grade})")
            
    except Exception as e:
        print(f"Error testing positioning: {e}")
        raise

if __name__ == "__main__":
    test_positioning()