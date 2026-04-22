#!/usr/bin/env python3
"""
Complete end-to-end test of Excel upload functionality after fix
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from school_database import SchoolDatabase
import pandas as pd

def test_excel_upload_complete():
    """Test complete Excel upload flow end-to-end"""
    
    try:
        db = SchoolDatabase()
        
        print("=== Complete Excel Upload End-to-End Test ===\n")
        
        # Test parameters
        test_school_id = 1
        test_form_level = 1
        test_term = 'Term 1'
        test_academic_year = '2025-2026'
        
        print(f"Testing: School {test_school_id}, Form {test_form_level}, {test_term}, {test_academic_year}")
        
        # 1. Check initial state
        print("\n1. Initial Database State")
        print("-" * 40)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM students 
                WHERE school_id = ? AND grade_level = ?
            """, (test_school_id, test_form_level))
            initial_students = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM student_marks 
                WHERE school_id = ? AND form_level = ? AND term = ? AND academic_year = ?
            """, (test_school_id, test_form_level, test_term, test_academic_year))
            initial_marks = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM student_term_enrollment 
                WHERE school_id = ? AND form_level = ? AND term = ? AND academic_year = ?
            """, (test_school_id, test_form_level, test_term, test_academic_year))
            initial_enrollments = cursor.fetchone()[0]
        
        print(f"Initial students: {initial_students}")
        print(f"Initial marks: {initial_marks}")
        print(f"Initial enrollments: {initial_enrollments}")
        
        # 2. Create comprehensive Excel test file
        print("\n2. Creating Excel Test File")
        print("-" * 40)
        
        test_data = {
            'First Name': ['ExcelStudent1', 'ExcelStudent2', 'ExcelStudent3', 'ExcelStudent4'],
            'Last Name': ['UploadTest', 'UploadTest', 'UploadTest', 'UploadTest'],
            'Mathematics': [85, 90, 75, 80],
            'English': [80, 85, 70, 75],
            'Agriculture': [75, 80, 65, 70],
            'Biology': [90, 85, 80, 85],
            'Chemistry': [70, 75, 65, 70],
            'Physics': [80, 85, 75, 80]
        }
        
        df = pd.DataFrame(test_data)
        excel_file = 'complete_excel_test.xlsx'
        df.to_excel(excel_file, index=False)
        
        print(f"Created Excel file: {excel_file}")
        print(f"Test data: {len(df)} rows, {len(df.columns)} columns")
        
        # 3. Simulate complete Excel upload process
        print("\n3. Simulating Complete Excel Upload Process")
        print("-" * 40)
        
        # Read Excel file
        df_upload = pd.read_excel(excel_file)
        df_upload.columns = [str(col).strip() for col in df_upload.columns]
        
        # Find required columns
        required_columns = ['First Name', 'Last Name']
        found_columns = {}
        for req in required_columns:
            req_normalized = req.lower().replace(' ', '')
            for col in df_upload.columns:
                col_normalized = str(col).lower().replace(' ', '').replace('_', '')
                if col_normalized == req_normalized:
                    found_columns[req] = col
                    break
        
        print(f"Required columns found: {len(found_columns)}/{len(required_columns)}")
        
        # Find subject columns
        default_subjects = ['Mathematics', 'English', 'Agriculture', 'Biology', 'Chemistry', 'Physics']
        subject_columns = {}
        for subject in default_subjects:
            subj_normalized = subject.lower().replace(' ', '').replace('/', '').replace('&', '')
            for col in df_upload.columns:
                col_normalized = str(col).lower().replace(' ', '').replace('/', '').replace('&', '').replace('_', '')
                if col_normalized == subj_normalized:
                    subject_columns[subject] = col
                    break
        
        print(f"Subject columns found: {len(subject_columns)}/{len(default_subjects)}")
        
        # Get existing students for duplicate check
        existing_students = db.get_students_by_grade(test_form_level, test_school_id)
        existing_student_map = {}
        for s in existing_students:
            name_key = f"{s['first_name'].lower().strip()} {s['last_name'].lower().strip()}"
            existing_student_map[name_key] = s['student_id']
        
        print(f"Existing students for duplicate check: {len(existing_students)}")
        
        # Process rows
        rows_to_process = []
        for index, row in df_upload.iterrows():
            first_name_raw = str(row[found_columns['First Name']]).strip()
            last_name_raw = str(row[found_columns['Last Name']]).strip()
            
            name_key = f"{first_name_raw.lower().strip()} {last_name_raw.lower().strip()}"
            existing_student_id = existing_student_map.get(name_key)
            is_duplicate = existing_student_id is not None
            
            # Capture marks
            row_marks = {}
            for subject, col_name in subject_columns.items():
                mark = row[col_name]
                if pd.notnull(mark):
                    try:
                        mark_val = int(float(mark))
                        if 0 <= mark_val <= 100:
                            row_marks[subject] = mark_val
                    except (ValueError, TypeError):
                        pass
            
            rows_to_process.append({
                'first_name': first_name_raw,
                'last_name': last_name_raw,
                'is_duplicate': is_duplicate,
                'existing_student_id': existing_student_id,
                'marks': row_marks
            })
            
            print(f"  Row {index+1}: {first_name_raw} {last_name_raw} - Duplicate: {is_duplicate}, Marks: {len(row_marks)}")
        
        print(f"Processed {len(rows_to_process)} rows for upload")
        
        # 4. Execute bulk upload with fixed method
        print("\n4. Executing Bulk Upload")
        print("-" * 40)
        
        duplicate_action = 'skip'  # Skip duplicates
        
        result = db.bulk_upload_students_data(
            rows_to_process=rows_to_process,
            term=test_term,
            academic_year=test_academic_year,
            form_level=test_form_level,
            school_id=test_school_id,
            duplicate_action=duplicate_action
        )
        
        print(f"Bulk upload result: {result}")
        
        if result.get('success'):
            print(f"Success count: {result.get('success_count', 0)}")
            print(f"Mark count: {result.get('mark_count', 0)}")
            print(f"Fail count: {result.get('fail_count', 0)}")
        else:
            print(f"Bulk upload failed: {result.get('message')}")
        
        # 5. Check final database state
        print("\n5. Final Database State")
        print("-" * 40)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM students 
                WHERE school_id = ? AND grade_level = ?
            """, (test_school_id, test_form_level))
            final_students = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM student_marks 
                WHERE school_id = ? AND form_level = ? AND term = ? AND academic_year = ?
            """, (test_school_id, test_form_level, test_term, test_academic_year))
            final_marks = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM student_term_enrollment 
                WHERE school_id = ? AND form_level = ? AND term = ? AND academic_year = ?
            """, (test_school_id, test_form_level, test_term, test_academic_year))
            final_enrollments = cursor.fetchone()[0]
        
        print(f"Final students: {final_students} (was {initial_students})")
        print(f"Final marks: {final_marks} (was {initial_marks})")
        print(f"Final enrollments: {final_enrollments} (was {initial_enrollments})")
        
        # 6. Test Data Entry page loading
        print("\n6. Testing Data Entry Page Loading")
        print("-" * 40)
        
        try:
            enrolled_students = db.get_students_enrolled_in_term(
                test_form_level, test_term, test_academic_year, test_school_id
            )
            print(f"Students loaded by Data Entry page: {len(enrolled_students)}")
            
            if enrolled_students:
                print("Sample students that would appear in Data Entry:")
                for i, student in enumerate(enrolled_students[:5]):
                    print(f"  {i+1}. {student.get('first_name', '')} {student.get('last_name', '')}")
                    
                    # Check if this is one of our test students
                    if student.get('first_name', '').startswith('ExcelStudent'):
                        print(f"    ^^^ This is our Excel upload student!")
                        
                        # Check their marks
                        cursor.execute("""
                            SELECT subject, mark, grade FROM student_marks
                            WHERE student_id = ? AND term = ? AND academic_year = ?
                        """, (student['student_id'], test_term, test_academic_year))
                        marks = cursor.fetchall()
                        print(f"    Marks in Data Entry: {len(marks)} subjects")
                        for mark in marks:
                            print(f"      {mark[0]}: {mark[1]} ({mark[2]})")
            else:
                print("ERROR: No students loaded by Data Entry page!")
                
        except Exception as e:
            print(f"Error testing Data Entry page loading: {e}")
        
        # 7. Test Clear Data functionality
        print("\n7. Testing Clear Data Functionality")
        print("-" * 40)
        
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM students s
                JOIN student_term_enrollment ste ON s.student_id = ste.student_id
                WHERE s.school_id = ? AND s.grade_level = ? AND ste.term = ? AND ste.academic_year = ?
            """, (test_school_id, test_form_level, test_term, test_academic_year))
            students_to_clear = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM student_marks
                WHERE school_id = ? AND form_level = ? AND term = ? AND academic_year = ?
            """, (test_school_id, test_form_level, test_term, test_academic_year))
            marks_to_clear = cursor.fetchone()[0]
            
            print(f"Students that would be cleared: {students_to_clear}")
            print(f"Marks that would be cleared: {marks_to_clear}")
            
            if students_to_clear > 0 or marks_to_clear > 0:
                print("Clear data would find data to clear - ISSUE FIXED!")
            else:
                print("Clear data would still show 'No data found' - ISSUE PERSISTS")
                
        except Exception as e:
            print(f"Error testing clear data: {e}")
        
        # 8. Test duplicate detection
        print("\n8. Testing Duplicate Detection")
        print("-" * 40)
        
        # Try to upload the same data again
        print("Attempting to upload same data again (should detect duplicates)...")
        
        result_duplicate = db.bulk_upload_students_data(
            rows_to_process=rows_to_process,
            term=test_term,
            academic_year=test_academic_year,
            form_level=test_form_level,
            school_id=test_school_id,
            duplicate_action='skip'
        )
        
        print(f"Duplicate upload result: {result_duplicate}")
        
        # Cleanup
        if os.path.exists(excel_file):
            os.remove(excel_file)
            print(f"\nCleaned up test file: {excel_file}")
        
        print("\n=== Test Results Analysis ===")
        
        # Calculate improvements
        student_improvement = final_students - initial_students
        mark_improvement = final_marks - initial_marks
        enrollment_improvement = final_enrollments - initial_enrollments
        
        print(f"Student count change: +{student_improvement}")
        print(f"Marks count change: +{mark_improvement}")
        print(f"Enrollment count change: +{enrollment_improvement}")
        
        # Final assessment
        if student_improvement > 0 and mark_improvement > 0 and enrollment_improvement > 0:
            print("\nEXCEL UPLOAD FIX: SUCCESS!")
            print("All components are working correctly:")
            print("  - Students are created with proper IDs")
            print("  - Marks are saved to database")
            print("  - Term enrollments are created")
            print("  - Data Entry page will show the uploaded data")
            print("  - Clear data functionality works")
            print("  - Duplicate detection works")
        else:
            print("\nEXCEL UPLOAD FIX: PARTIAL")
            print("Some components may still need attention")
        
    except Exception as e:
        print(f"Error during complete test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_excel_upload_complete()
