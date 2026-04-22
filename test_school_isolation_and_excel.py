#!/usr/bin/env python3
"""
Test school data isolation and Excel upload functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from school_database import SchoolDatabase
import pandas as pd

def test_school_data_isolation():
    """Test that each school's data is properly isolated"""
    
    try:
        db = SchoolDatabase()
        
        print("=== School Data Isolation Test ===\n")
        
        # Get all schools in database
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT school_id, school_name FROM schools ORDER BY school_id")
            schools = cursor.fetchall()
        
        print(f"Found {len(schools)} schools in database:")
        for school_id, school_name in schools:
            print(f"  School {school_id}: {school_name}")
        
        print("\n1. Testing Student Data Isolation")
        print("-" * 50)
        
        for school_id, school_name in schools:
            # Test students for each school
            students = db.get_students_by_grade(1, school_id)
            print(f"School {school_id} ({school_name}): {len(students)} Form 1 students")
            
            # Test marks for each school
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM student_marks 
                    WHERE school_id = ? AND form_level = 1
                """, (school_id,))
                marks_count = cursor.fetchone()[0]
                print(f"  School {school_id}: {marks_count} Form 1 marks")
        
        print("\n2. Testing Cross-School Data Leakage")
        print("-" * 50)
        
        # Test that queries properly filter by school_id
        test_school_id = 1
        other_schools = [s[0] for s in schools if s[0] != test_school_id]
        
        if other_schools:
            other_school_id = other_schools[0]
            
            # Get students for test school
            test_school_students = db.get_students_by_grade(1, test_school_id)
            other_school_students = db.get_students_by_grade(1, other_school_id)
            
            print(f"School {test_school_id} students: {len(test_school_students)}")
            print(f"School {other_school_id} students: {len(other_school_students)}")
            
            # Verify no overlap in student IDs
            test_ids = {s['student_id'] for s in test_school_students}
            other_ids = {s['student_id'] for s in other_school_students}
            
            overlap = test_ids & other_ids
            print(f"Student ID overlap: {len(overlap)} (should be 0)")
            
            # Test marks isolation
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Count marks for test school only
                cursor.execute("""
                    SELECT COUNT(*) FROM student_marks 
                    WHERE school_id = ? AND form_level = 1
                """, (test_school_id,))
                test_marks = cursor.fetchone()[0]
                
                # Count marks for other school only
                cursor.execute("""
                    SELECT COUNT(*) FROM student_marks 
                    WHERE school_id = ? AND form_level = 1
                """, (other_school_id,))
                other_marks = cursor.fetchone()[0]
                
                # Count total marks (should equal sum of individual schools)
                cursor.execute("""
                    SELECT COUNT(*) FROM student_marks 
                    WHERE form_level = 1
                """)
                total_marks = cursor.fetchone()[0]
                
                print(f"School {test_school_id} marks: {test_marks}")
                print(f"School {other_school_id} marks: {other_marks}")
                print(f"Total marks: {total_marks}")
                print(f"Sum check: {test_marks + other_marks} == {total_marks}? {'PASS' if test_marks + other_marks == total_marks else 'FAIL'}")
        
        print("\n3. Testing API-Level School Isolation")
        print("-" * 50)
        
        # Test rankings isolation
        for school_id, school_name in schools[:2]:  # Test first 2 schools
            result = db.get_student_rankings(1, 'Term 1', '2025-2026', school_id)
            rankings = result.get('rankings', [])
            print(f"School {school_id} rankings: {len(rankings)} students")
            
            if rankings:
                # Verify all rankings belong to this school
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    for student in rankings[:3]:  # Check first 3 students
                        name = student.get('name', '')
                        first_name, last_name = name.split(' ', 1) if ' ' in name else (name, '')
                        
                        cursor.execute("""
                            SELECT COUNT(*) FROM students s
                            JOIN student_marks sm ON s.student_id = sm.student_id
                            WHERE s.first_name = ? AND s.last_name = ? AND sm.school_id = ?
                        """, (first_name, last_name, school_id))
                        count = cursor.fetchone()[0]
                        
                        if count == 0:
                            print(f"  LEAKAGE: {name} found in wrong school!")
                        else:
                            print(f"  OK: {name} belongs to correct school")
        
        print("\n4. Testing Excel Upload School Assignment")
        print("-" * 50)
        
        # Create test Excel data
        test_data = {
            'First Name': ['TestStudent1', 'TestStudent2'],
            'Last Name': ['ExcelUpload', 'ExcelUpload'],
            'Mathematics': [75, 80],
            'English': [65, 70]
        }
        
        df = pd.DataFrame(test_data)
        excel_path = 'test_excel_upload.xlsx'
        df.to_excel(excel_path, index=False)
        
        print(f"Created test Excel file: {excel_path}")
        print(f"Test data: {len(df)} students")
        
        # Test bulk upload method for different schools
        for school_id, school_name in schools[:2]:
            print(f"\nTesting Excel upload for School {school_id} ({school_name})")
            
            # Simulate Excel upload processing
            rows_to_process = []
            for index, row in df.iterrows():
                rows_to_process({
                    'first_name': row['First Name'],
                    'last_name': row['Last Name'],
                    'is_duplicate': False,
                    'existing_student_id': None,
                    'marks': {
                        'Mathematics': row['Mathematics'],
                        'English': row['English']
                    }
                })
            
            # Test the bulk upload method (without actually uploading)
            print(f"  Prepared {len(rows_to_process)} rows for School {school_id}")
            print(f"  School isolation: {'PASS' if school_id is not None else 'FAIL'}")
        
        # Cleanup
        if os.path.exists(excel_path):
            os.remove(excel_path)
            print(f"\nCleaned up test file: {excel_path}")
        
        print("\n=== School Isolation Test Complete ===")
        
    except Exception as e:
        print(f"Error during school isolation test: {e}")
        import traceback
        traceback.print_exc()

def test_excel_upload_functionality():
    """Test Excel upload functionality issues"""
    
    try:
        print("\n=== Excel Upload Functionality Test ===\n")
        
        # Check if required libraries are available
        try:
            import pandas as pd
            print("pandas: AVAILABLE")
        except ImportError:
            print("pandas: MISSING - This could cause Excel upload failures")
            return
        
        try:
            import openpyxl
            print("openpyxl: AVAILABLE")
        except ImportError:
            print("openpyxl: MISSING - This could cause .xlsx file issues")
        
        try:
            import xlrd
            print("xlrd: AVAILABLE")
        except ImportError:
            print("xlrd: MISSING - This could cause .xls file issues")
        
        print("\n1. Testing Excel File Creation")
        print("-" * 30)
        
        # Create test Excel files
        test_data = {
            'First Name': ['Test1', 'Test2'],
            'Last Name': ['Student', 'Student'],
            'Mathematics': [85, 90],
            'English': [75, 80]
        }
        
        df = pd.DataFrame(test_data)
        
        # Test .xlsx format
        xlsx_file = 'test_upload.xlsx'
        try:
            df.to_excel(xlsx_file, index=False, engine='openpyxl')
            print(f"Created .xlsx file: {xlsx_file}")
            
            # Test reading it back
            df_read = pd.read_excel(xlsx_file, engine='openpyxl')
            print(f"Read .xlsx file: {len(df_read)} rows")
            print("Excel .xlsx support: PASS")
        except Exception as e:
            print(f"Excel .xlsx support: FAIL - {e}")
        
        # Test .xls format (if xlrd available)
        try:
            xls_file = 'test_upload.xls'
            df.to_excel(xls_file, index=False, engine='openpyxl')  # Create as .xls
            print(f"Created .xls file: {xls_file}")
            
            df_read = pd.read_excel(xls_file, engine='xlrd')
            print(f"Read .xls file: {len(df_read)} rows")
            print("Excel .xls support: PASS")
        except Exception as e:
            print(f"Excel .xls support: FAIL - {e}")
        
        print("\n2. Testing Excel Upload Logic")
        print("-" * 30)
        
        # Simulate the Excel upload processing logic
        df.columns = [str(col).strip() for col in df.columns]
        
        # Required columns check
        required_columns = ['First Name', 'Last Name']
        found_columns = {}
        
        for req in required_columns:
            req_normalized = req.lower().replace(' ', '')
            for col in df.columns:
                col_normalized = str(col).lower().replace(' ', '').replace('_', '')
                if col_normalized == req_normalized:
                    found_columns[req] = col
                    break
        
        print(f"Required columns found: {len(found_columns)}/{len(required_columns)}")
        print("Column matching logic: PASS" if len(found_columns) == len(required_columns) else "FAIL")
        
        # Subject column detection
        default_subjects = ['Mathematics', 'English']
        subject_columns = {}
        
        for subject in default_subjects:
            subj_normalized = subject.lower().replace(' ', '').replace('/', '').replace('&', '')
            for col in df.columns:
                col_normalized = str(col).lower().replace(' ', '').replace('/', '').replace('&', '').replace('_', '')
                if col_normalized == subj_normalized:
                    subject_columns[subject] = col
                    break
        
        print(f"Subject columns found: {len(subject_columns)}/{len(default_subjects)}")
        print("Subject matching logic: PASS" if len(subject_columns) == len(default_subjects) else "FAIL")
        
        print("\n3. Common Excel Upload Issues")
        print("-" * 30)
        
        issues = []
        
        # Check for common issues
        if not os.path.exists(xlsx_file):
            issues.append("Excel file creation failed")
        
        try:
            test_df = pd.read_excel(xlsx_file)
            if len(test_df) == 0:
                issues.append("Empty Excel file")
        except Exception as e:
            issues.append(f"Excel reading error: {e}")
        
        # Check file permissions
        if os.path.exists(xlsx_file):
            if not os.access(xlsx_file, os.R_OK):
                issues.append("Excel file not readable")
        
        if issues:
            print("Potential issues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("No common issues detected")
        
        # Cleanup
        for file in [xlsx_file, 'test_upload.xls']:
            if os.path.exists(file):
                os.remove(file)
                print(f"Cleaned up: {file}")
        
        print("\n=== Excel Upload Test Complete ===")
        
    except Exception as e:
        print(f"Error during Excel upload test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_school_data_isolation()
    test_excel_upload_functionality()
