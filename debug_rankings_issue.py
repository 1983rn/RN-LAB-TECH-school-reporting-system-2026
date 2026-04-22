#!/usr/bin/env python3
"""
Debug why rankings return empty despite data existing in student_marks
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from school_database import SchoolDatabase

def debug_rankings_issue():
    """Debug the rankings issue step by step"""
    
    try:
        db = SchoolDatabase()
        
        print("=== Debugging Rankings Issue ===\n")
        
        # Step 1: Check what data actually exists
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            print("Step 1: Checking student_marks table structure and data")
            print("-" * 50)
            
            # Check if school_id column exists in student_marks
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'student_marks'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            
            print("student_marks table columns:")
            for col in columns:
                print(f"  {col[0]}: {col[1]}")
            
            # Check sample data with all columns
            cursor.execute("""
                SELECT * FROM student_marks 
                LIMIT 3
            """)
            sample_data = cursor.fetchall()
            
            print(f"\nSample data ({len(sample_data)} rows):")
            for i, row in enumerate(sample_data):
                print(f"  Row {i+1}: {row}")
            
            # Check distinct school_ids in student_marks
            cursor.execute("SELECT DISTINCT school_id FROM student_marks")
            school_ids = cursor.fetchall()
            print(f"\nSchool IDs in student_marks: {[sid[0] for sid in school_ids]}")
            
            # Check data for specific period
            cursor.execute("""
                SELECT COUNT(*) FROM student_marks 
                WHERE form_level = 1 AND term = 'Term 1' AND academic_year = '2025-2026'
            """)
            count_all_schools = cursor.fetchone()[0]
            print(f"\nTotal marks for Form 1, Term 1, 2025-2026 (all schools): {count_all_schools}")
            
            cursor.execute("""
                SELECT COUNT(*) FROM student_marks 
                WHERE form_level = 1 AND term = 'Term 1' AND academic_year = '2025-2026' AND school_id = 2
            """)
            count_school_2 = cursor.fetchone()[0]
            print(f"Total marks for Form 1, Term 1, 2025-2026 (school_id=2): {count_school_2}")
        
        print("\nStep 2: Checking students table and linking")
        print("-" * 50)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check students in Form 1
            cursor.execute("""
                SELECT COUNT(*) FROM students 
                WHERE grade_level = 1
            """)
            form1_students = cursor.fetchone()[0]
            print(f"Total Form 1 students: {form1_students}")
            
            # Check students with school_id
            cursor.execute("""
                SELECT COUNT(*) FROM students 
                WHERE grade_level = 1 AND school_id = 2
            """)
            form1_students_school2 = cursor.fetchone()[0]
            print(f"Form 1 students with school_id=2: {form1_students_school2}")
            
            # Check the JOIN query used in rankings
            cursor.execute("""
                SELECT DISTINCT s.student_id, s.first_name, s.last_name 
                FROM students s
                JOIN student_marks sm ON s.student_id = sm.student_id
                WHERE sm.form_level = 1 AND sm.term = 'Term 1' AND sm.academic_year = '2025-2026' AND sm.school_id = 2
                ORDER BY s.first_name, s.last_name
                LIMIT 5
            """)
            joined_students = cursor.fetchall()
            print(f"\nStudents found by JOIN query: {len(joined_students)}")
            for student in joined_students:
                print(f"  {student[0]}: {student[1]} {student[2]}")
        
        print("\nStep 3: Testing individual parts of the rankings query")
        print("-" * 50)
        
        # Test the exact query from get_student_rankings method
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Test the first part - getting distinct students
            cursor.execute("""
                SELECT DISTINCT s.student_id, s.first_name, s.last_name 
                FROM students s
                JOIN student_marks sm ON s.student_id = sm.student_id
                WHERE sm.form_level = 1 AND sm.term = 'Term 1' AND sm.academic_year = '2025-2026' AND sm.school_id = 2
                ORDER BY s.first_name, s.last_name
            """)
            all_students = cursor.fetchall()
            print(f"Students found by main query: {len(all_students)}")
            
            if all_students:
                # Test marks calculation for first student
                student_id, first_name, last_name = all_students[0]
                print(f"\nTesting marks calculation for: {first_name} {last_name} (ID: {student_id})")
                
                cursor.execute("""
                    SELECT AVG(sm.mark) as average,
                           SUM(sm.mark) as total_marks,
                           COUNT(CASE WHEN sm.mark >= 50 THEN 1 END) as subjects_passed,
                           COUNT(sm.mark) as total_subjects
                    FROM student_marks sm
                    WHERE sm.student_id = ? AND sm.term = 'Term 1' AND sm.academic_year = '2025-2026' AND sm.school_id = 2
                """, (student_id,))
                
                marks_data = cursor.fetchone()
                print(f"Marks data: {marks_data}")
                
                # Check if student has English marks
                cursor.execute("""
                    SELECT mark FROM student_marks 
                    WHERE student_id = ? AND subject = 'English' AND term = 'Term 1' AND academic_year = '2025-2026' AND school_id = 2
                """, (student_id,))
                
                english_result = cursor.fetchone()
                print(f"English mark: {english_result}")
        
        print("\nStep 4: Testing the complete rankings method")
        print("-" * 50)
        
        # Test with different school_id values
        for test_school_id in [None, 1, 2]:
            print(f"\nTesting with school_id = {test_school_id}")
            
            try:
                result = db.get_student_rankings(1, 'Term 1', '2025-2026', test_school_id)
                rankings = result.get('rankings', [])
                total_students = result.get('total_students', 0)
                students_with_marks = result.get('students_with_marks', 0)
                
                print(f"  Total enrolled students: {total_students}")
                print(f"  Students with marks: {students_with_marks}")
                print(f"  Students in rankings: {len(rankings)}")
                
                if rankings:
                    print(f"  First student: {rankings[0].get('name', 'Unknown')}")
                    
            except Exception as e:
                print(f"  Error: {e}")
        
        print("\n=== Debug Complete ===")
        
    except Exception as e:
        print(f"Error during debugging: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_rankings_issue()
