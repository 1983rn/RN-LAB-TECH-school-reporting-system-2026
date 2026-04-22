#!/usr/bin/env python3
"""
Detailed debug of the bulk upload method to find why marks aren't saved
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from school_database import SchoolDatabase
import pandas as pd

def debug_bulk_upload_detailed():
    """Debug the bulk upload method in detail"""
    
    try:
        db = SchoolDatabase()
        
        print("=== Detailed Bulk Upload Debug ===\n")
        
        # Test parameters
        test_school_id = 1
        test_form_level = 1
        test_term = 'Term 1'
        test_academic_year = '2025-2026'
        
        # Create test data with proper structure
        rows_to_process = [
            {
                'first_name': 'DebugTest1',
                'last_name': 'UploadTest',
                'is_duplicate': False,
                'existing_student_id': None,
                'marks': {
                    'Mathematics': 85,
                    'English': 80,
                    'Agriculture': 75
                }
            },
            {
                'first_name': 'DebugTest2',
                'last_name': 'UploadTest',
                'is_duplicate': False,
                'existing_student_id': None,
                'marks': {
                    'Mathematics': 90,
                    'English': 85,
                    'Agriculture': 80
                }
            }
        ]
        
        print("Test data structure:")
        for i, row in enumerate(rows_to_process):
            print(f"  Row {i+1}: {row['first_name']} {row['last_name']}")
            print(f"    Duplicate: {row['is_duplicate']}")
            print(f"    Marks: {len(row.get('marks', {}))} subjects")
            for subject, mark in row.get('marks', {}).items():
                print(f"      {subject}: {mark}")
        
        print(f"\nParameters: School {test_school_id}, Form {test_form_level}, {test_term}, {test_academic_year}")
        
        # Test the bulk upload method step by step
        print("\n=== Manual Bulk Upload Simulation ===")
        
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                for i, row_data in enumerate(rows_to_process):
                    print(f"\n--- Processing Student {i+1}: {row_data['first_name']} {row_data['last_name']} ---")
                    
                    try:
                        # Use savepoint for each student
                        cursor.execute("SAVEPOINT student_upload")
                        student_id = None
                        
                        if row_data['is_duplicate']:
                            print("  Skipping duplicate student logic for now")
                        else:
                            # Create new student
                            print("  Creating new student...")
                            cursor.execute("""
                                INSERT INTO students (first_name, last_name, grade_level, school_id, status)
                                VALUES (?, ?, ?, ?, 'Active')
                                RETURNING student_id
                            """, (row_data['first_name'], row_data['last_name'], test_form_level, test_school_id))
                            
                            student_id = cursor.fetchone()[0]
                            print(f"  Created student with ID: {student_id}")
                            
                            if student_id:
                                # Enroll student in term
                                print("  Enrolling student in term...")
                                cursor.execute("""
                                    INSERT INTO student_term_enrollment (student_id, term, academic_year, form_level, school_id)
                                    VALUES (?, ?, ?, ?, ?)
                                    ON CONFLICT (student_id, term, academic_year, school_id) DO NOTHING
                                """, (student_id, test_term, test_academic_year, test_form_level, test_school_id))
                                
                                # Check if enrollment was created
                                cursor.execute("""
                                    SELECT COUNT(*) FROM student_term_enrollment
                                    WHERE student_id = ? AND term = ? AND academic_year = ?
                                """, (student_id, test_term, test_academic_year))
                                enrollment_count = cursor.fetchone()[0]
                                print(f"  Enrollment created: {enrollment_count > 0}")
                                
                                # Save marks
                                marks = row_data.get('marks', {})
                                print(f"  Processing {len(marks)} marks...")
                                
                                for subject, mark in marks.items():
                                    print(f"    Saving {subject}: {mark}")
                                    
                                    # Calculate grade
                                    grade = db.calculate_grade(mark, test_form_level, test_school_id)
                                    print(f"      Grade: {grade}")
                                    
                                    cursor.execute("""
                                        INSERT INTO student_marks (student_id, subject, mark, grade, term, academic_year, form_level, school_id)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                        ON CONFLICT (student_id, subject, term, academic_year, school_id) 
                                        DO UPDATE SET mark = EXCLUDED.mark, grade = EXCLUDED.grade
                                    """, (student_id, subject, mark, grade, test_term, test_academic_year, test_form_level, test_school_id))
                                    
                                    # Check if mark was saved
                                    cursor.execute("""
                                        SELECT COUNT(*) FROM student_marks
                                        WHERE student_id = ? AND subject = ? AND term = ? AND academic_year = ?
                                    """, (student_id, subject, test_term, test_academic_year))
                                    mark_count = cursor.fetchone()[0]
                                    print(f"      Mark saved: {mark_count > 0}")
                        
                        cursor.execute("RELEASE SAVEPOINT student_upload")
                        print("  Student processing completed successfully")
                        
                    except Exception as e:
                        try:
                            cursor.execute("ROLLBACK TO SAVEPOINT student_upload")
                            print(f"  Rolled back due to error: {e}")
                        except:
                            pass
                        print(f"  ERROR: {e}")
                        import traceback
                        traceback.print_exc()
                
                # Commit all changes
                conn.commit()
                print("\n=== All changes committed ===")
                
        except Exception as e:
            print(f"Error in manual simulation: {e}")
            import traceback
            traceback.print_exc()
        
        # Check final database state
        print("\n=== Final Database State ===")
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check our test students
            cursor.execute("""
                SELECT student_id, first_name, last_name
                FROM students
                WHERE first_name LIKE 'DebugTest%'
            """)
            test_students = cursor.fetchall()
            print(f"Test students created: {len(test_students)}")
            
            for student in test_students:
                student_id, first_name, last_name = student
                print(f"  {student_id}: {first_name} {last_name}")
                
                # Check enrollment
                cursor.execute("""
                    SELECT COUNT(*) FROM student_term_enrollment
                    WHERE student_id = ? AND term = ? AND academic_year = ?
                """, (student_id, test_term, test_academic_year))
                enrollment_count = cursor.fetchone()[0]
                print(f"    Enrolled: {'Yes' if enrollment_count > 0 else 'No'}")
                
                # Check marks
                cursor.execute("""
                    SELECT subject, mark, grade FROM student_marks
                    WHERE student_id = ? AND term = ? AND academic_year = ?
                """, (student_id, test_term, test_academic_year))
                marks = cursor.fetchall()
                print(f"    Marks: {len(marks)} subjects")
                for mark in marks:
                    print(f"      {mark[0]}: {mark[1]} ({mark[2]})")
        
        # Test the actual bulk upload method
        print("\n=== Testing Actual Bulk Upload Method ===")
        
        # Create fresh test data
        fresh_rows = [
            {
                'first_name': 'BulkTest1',
                'last_name': 'MethodTest',
                'is_duplicate': False,
                'existing_student_id': None,
                'marks': {
                    'Mathematics': 95,
                    'English': 90,
                    'Agriculture': 85
                }
            }
        ]
        
        print("Calling bulk_upload_students_data method...")
        result = db.bulk_upload_students_data(
            rows_to_process=fresh_rows,
            term=test_term,
            academic_year=test_academic_year,
            form_level=test_form_level,
            school_id=test_school_id,
            duplicate_action='skip'
        )
        
        print(f"Result: {result}")
        
        # Check if this student was created properly
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT student_id, first_name, last_name
                FROM students
                WHERE first_name = 'BulkTest1'
            """)
            bulk_student = cursor.fetchone()
            
            if bulk_student:
                student_id, first_name, last_name = bulk_student
                print(f"Bulk method created student: {student_id}: {first_name} {last_name}")
                
                # Check enrollment
                cursor.execute("""
                    SELECT COUNT(*) FROM student_term_enrollment
                    WHERE student_id = ? AND term = ? AND academic_year = ?
                """, (student_id, test_term, test_academic_year))
                enrollment_count = cursor.fetchone()[0]
                print(f"Bulk method enrollment: {'Yes' if enrollment_count > 0 else 'No'}")
                
                # Check marks
                cursor.execute("""
                    SELECT COUNT(*) FROM student_marks
                    WHERE student_id = ? AND term = ? AND academic_year = ?
                """, (student_id, test_term, test_academic_year))
                marks_count = cursor.fetchone()[0]
                print(f"Bulk method marks: {marks_count} subjects")
        
        print("\n=== Debug Complete ===")
        
    except Exception as e:
        print(f"Error during detailed debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_bulk_upload_detailed()
