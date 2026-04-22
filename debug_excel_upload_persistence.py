#!/usr/bin/env python3
"""
Debug Excel upload persistence issue - data uploaded but not visible
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from school_database import SchoolDatabase
import pandas as pd

def debug_excel_upload_persistence():
    """Debug why Excel upload appears successful but data doesn't show"""
    
    try:
        db = SchoolDatabase()
        
        print("=== Excel Upload Persistence Debug ===\n")
        
        # Test parameters
        test_school_id = 1  # Use school with existing data
        test_form_level = 1
        test_term = 'Term 1'
        test_academic_year = '2025-2026'
        
        print(f"Testing with: School {test_school_id}, Form {test_form_level}, {test_term}, {test_academic_year}")
        
        # 1. Check current state before upload
        print("\n1. Current Database State Before Upload")
        print("-" * 50)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check students
            cursor.execute("""
                SELECT COUNT(*) FROM students 
                WHERE school_id = ? AND grade_level = ?
            """, (test_school_id, test_form_level))
            students_before = cursor.fetchone()[0]
            print(f"Students in database: {students_before}")
            
            # Check student marks
            cursor.execute("""
                SELECT COUNT(*) FROM student_marks 
                WHERE school_id = ? AND form_level = ? AND term = ? AND academic_year = ?
            """, (test_school_id, test_form_level, test_term, test_academic_year))
            marks_before = cursor.fetchone()[0]
            print(f"Marks in database: {marks_before}")
            
            # Check term enrollment
            cursor.execute("""
                SELECT COUNT(*) FROM student_term_enrollment 
                WHERE school_id = ? AND form_level = ? AND term = ? AND academic_year = ?
            """, (test_school_id, test_form_level, test_term, test_academic_year))
            enrollment_before = cursor.fetchone()[0]
            print(f"Term enrollments in database: {enrollment_before}")
        
        # 2. Check what the Data Entry page would show
        print("\n2. Data Entry Page Loading Logic")
        print("-" * 50)
        
        # This simulates what the Data Entry page loads
        try:
            enrolled_students = db.get_students_enrolled_in_term(
                test_form_level, test_term, test_academic_year, test_school_id
            )
            print(f"Students enrolled in term: {len(enrolled_students)}")
            
            if enrolled_students:
                print("Sample enrolled students:")
                for i, student in enumerate(enrolled_students[:3]):
                    print(f"  {i+1}. {student.get('first_name', '')} {student.get('last_name', '')}")
            else:
                print("No enrolled students found")
                
        except Exception as e:
            print(f"Error loading enrolled students: {e}")
        
        # 3. Test Excel upload process
        print("\n3. Simulating Excel Upload Process")
        print("-" * 50)
        
        # Create test Excel data
        test_data = {
            'First Name': ['ExcelTest1', 'ExcelTest2', 'ExcelTest3'],
            'Last Name': ['UploadTest', 'UploadTest', 'UploadTest'],
            'Mathematics': [85, 90, 75],
            'English': [80, 85, 70],
            'Agriculture': [75, 80, 65]
        }
        
        df = pd.DataFrame(test_data)
        excel_file = 'debug_upload_test.xlsx'
        df.to_excel(excel_file, index=False)
        
        print(f"Created test Excel file: {excel_file}")
        
        # Simulate the exact upload process
        try:
            # Read Excel
            df_upload = pd.read_excel(excel_file)
            df_upload.columns = [str(col).strip() for col in df_upload.columns]
            print(f"Read Excel: {len(df_upload)} rows")
            
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
            
            print(f"Required columns found: {len(found_columns)}")
            
            # Find subject columns
            default_subjects = ['Mathematics', 'English', 'Agriculture']
            subject_columns = {}
            for subject in default_subjects:
                subj_normalized = subject.lower().replace(' ', '').replace('/', '').replace('&', '')
                for col in df_upload.columns:
                    col_normalized = str(col).lower().replace(' ', '').replace('/', '').replace('&', '').replace('_', '')
                    if col_normalized == subj_normalized:
                        subject_columns[subject] = col
                        break
            
            print(f"Subject columns found: {len(subject_columns)}")
            
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
            
            # Test the bulk upload method
            print("\n4. Testing Bulk Upload Method")
            print("-" * 50)
            
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
            
        except Exception as e:
            print(f"Error during upload simulation: {e}")
            import traceback
            traceback.print_exc()
        
        # 5. Check database state after upload
        print("\n5. Database State After Upload")
        print("-" * 50)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check students
            cursor.execute("""
                SELECT COUNT(*) FROM students 
                WHERE school_id = ? AND grade_level = ?
            """, (test_school_id, test_form_level))
            students_after = cursor.fetchone()[0]
            print(f"Students in database: {students_after} (was {students_before})")
            
            # Check student marks
            cursor.execute("""
                SELECT COUNT(*) FROM student_marks 
                WHERE school_id = ? AND form_level = ? AND term = ? AND academic_year = ?
            """, (test_school_id, test_form_level, test_term, test_academic_year))
            marks_after = cursor.fetchone()[0]
            print(f"Marks in database: {marks_after} (was {marks_before})")
            
            # Check term enrollment
            cursor.execute("""
                SELECT COUNT(*) FROM student_term_enrollment 
                WHERE school_id = ? AND form_level = ? AND term = ? AND academic_year = ?
            """, (test_school_id, test_form_level, test_term, test_academic_year))
            enrollment_after = cursor.fetchone()[0]
            print(f"Term enrollments in database: {enrollment_after} (was {enrollment_before})")
            
            # Check for our specific test students
            cursor.execute("""
                SELECT s.student_id, s.first_name, s.last_name
                FROM students s
                WHERE s.school_id = ? AND s.grade_level = ? 
                AND s.first_name LIKE 'ExcelTest%'
            """, (test_school_id, test_form_level))
            test_students = cursor.fetchall()
            
            print(f"Test students created: {len(test_students)}")
            for student in test_students:
                student_id, first_name, last_name = student
                print(f"  {student_id}: {first_name} {last_name}")
                
                # Check their marks
                cursor.execute("""
                    SELECT subject, mark FROM student_marks
                    WHERE student_id = ? AND term = ? AND academic_year = ?
                """, (student_id, test_term, test_academic_year))
                marks = cursor.fetchall()
                print(f"    Marks: {len(marks)} subjects")
                for mark in marks:
                    print(f"      {mark[0]}: {mark[1]}")
                
                # Check their enrollment
                cursor.execute("""
                    SELECT COUNT(*) FROM student_term_enrollment
                    WHERE student_id = ? AND term = ? AND academic_year = ?
                """, (student_id, test_term, test_academic_year))
                enrolled = cursor.fetchone()[0]
                print(f"    Enrolled in term: {'Yes' if enrolled > 0 else 'No'}")
        
        # 6. Test Data Entry page loading again
        print("\n6. Data Entry Page Loading After Upload")
        print("-" * 50)
        
        try:
            enrolled_students_after = db.get_students_enrolled_in_term(
                test_form_level, test_term, test_academic_year, test_school_id
            )
            print(f"Students enrolled in term: {len(enrolled_students_after)} (was {len(enrolled_students) if 'enrolled_students' in locals() else 0})")
            
            if enrolled_students_after:
                print("Sample enrolled students after upload:")
                for i, student in enumerate(enrolled_students_after[:5]):
                    print(f"  {i+1}. {student.get('first_name', '')} {student.get('last_name', '')}")
                    
                    # Check if this is one of our test students
                    if student.get('first_name', '').startswith('ExcelTest'):
                        print(f"    ^^^ This is our test student!")
            else:
                print("No enrolled students found after upload")
                
        except Exception as e:
            print(f"Error loading enrolled students after upload: {e}")
        
        # 7. Clear data test
        print("\n7. Testing Clear Data Functionality")
        print("-" * 50)
        
        try:
            # Test the clear data logic
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
            
            if students_to_clear == 0 and marks_to_clear == 0:
                print("Clear data would show 'No data found' - this explains the user's issue!")
            else:
                print("Clear data should find data to clear")
                
        except Exception as e:
            print(f"Error testing clear data: {e}")
        
        # Cleanup
        if os.path.exists(excel_file):
            os.remove(excel_file)
            print(f"\nCleaned up test file: {excel_file}")
        
        print("\n=== Debug Analysis Complete ===")
        
        # Analysis
        print("\nANALYSIS:")
        if students_after > students_before:
            print("1. Students were created successfully")
        else:
            print("1. ERROR: Students were NOT created")
            
        if marks_after > marks_before:
            print("2. Marks were saved successfully")
        else:
            print("2. ERROR: Marks were NOT saved")
            
        if enrollment_after > enrollment_before:
            print("3. Term enrollments were created successfully")
        else:
            print("3. ERROR: Term enrollments were NOT created")
            
        if len(enrolled_students_after) > len(enrolled_students) if 'enrolled_students' in locals() else False:
            print("4. Data Entry page should show new students")
        else:
            print("4. ERROR: Data Entry page will NOT show new students")
        
    except Exception as e:
        print(f"Error during debugging: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_excel_upload_persistence()
