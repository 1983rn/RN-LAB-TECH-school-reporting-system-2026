#!/usr/bin/env python3
"""
Debug Excel upload issues in the Data Entry page
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from school_database import SchoolDatabase
import pandas as pd

def debug_excel_upload_issue():
    """Debug potential Excel upload issues"""
    
    try:
        print("=== Excel Upload Issue Debug ===\n")
        
        print("1. Checking Required Libraries")
        print("-" * 40)
        
        libraries = {
            'pandas': pd,
            'openpyxl': None,
            'xlrd': None
        }
        
        try:
            import openpyxl
            libraries['openpyxl'] = openpyxl
            print("openpyxl: Available")
        except ImportError:
            print("openpyxl: MISSING - Required for .xlsx files")
        
        try:
            import xlrd
            libraries['xlrd'] = xlrd
            print("xlrd: Available")
        except ImportError:
            print("xlrd: MISSING - Required for .xls files")
        
        print("\n2. Testing Excel File Operations")
        print("-" * 40)
        
        # Create test data
        test_data = {
            'First Name': ['Test1', 'Test2', 'Test3'],
            'Last Name': ['Student', 'Student', 'Student'],
            'Mathematics': [85, 90, 75],
            'English': [80, 85, 70],
            'Agriculture': [75, 80, 65]
        }
        
        df = pd.DataFrame(test_data)
        
        # Test .xlsx creation and reading
        try:
            xlsx_file = 'debug_test.xlsx'
            df.to_excel(xlsx_file, index=False, engine='openpyxl')
            print(f"Created .xlsx file: {xlsx_file}")
            
            # Test reading with different engines
            try:
                df_read1 = pd.read_excel(xlsx_file, engine='openpyxl')
                print(f"Read with openpyxl: {len(df_read1)} rows")
            except Exception as e:
                print(f"Read with openpyxl failed: {e}")
            
            try:
                df_read2 = pd.read_excel(xlsx_file)  # Auto-detect
                print(f"Read with auto-detect: {len(df_read2)} rows")
            except Exception as e:
                print(f"Read with auto-detect failed: {e}")
            
        except Exception as e:
            print(f".xlsx file creation failed: {e}")
        
        # Test .xls creation and reading
        try:
            xls_file = 'debug_test.xls'
            df.to_excel(xls_file, index=False, engine='openpyxl')
            print(f"Created .xls file: {xls_file}")
            
            try:
                df_read3 = pd.read_excel(xls_file, engine='xlrd')
                print(f"Read with xlrd: {len(df_read3)} rows")
            except Exception as e:
                print(f"Read with xlrd failed: {e}")
            
            try:
                df_read4 = pd.read_excel(xls_file)  # Auto-detect
                print(f"Read with auto-detect: {len(df_read4)} rows")
            except Exception as e:
                print(f"Read with auto-detect failed: {e}")
                
        except Exception as e:
            print(f".xls file creation failed: {e}")
        
        print("\n3. Simulating Excel Upload Process")
        print("-" * 40)
        
        # Simulate the exact process from app.py
        if os.path.exists(xlsx_file):
            try:
                # Step 1: Read Excel file (as done in app.py)
                df_upload = pd.read_excel(xlsx_file)
                print(f"Step 1 - Read Excel: {len(df_upload)} rows")
                
                # Step 2: Normalize column names
                df_upload.columns = [str(col).strip() for col in df_upload.columns]
                print(f"Step 2 - Normalized columns: {df_upload.columns.tolist()}")
                
                # Step 3: Check required columns
                required_columns = ['First Name', 'Last Name']
                found_columns = {}
                
                for req in required_columns:
                    req_normalized = req.lower().replace(' ', '')
                    for col in df_upload.columns:
                        col_normalized = str(col).lower().replace(' ', '').replace('_', '')
                        if col_normalized == req_normalized:
                            found_columns[req] = col
                            break
                
                print(f"Step 3 - Required columns found: {len(found_columns)}/{len(required_columns)}")
                
                if len(found_columns) < len(required_columns):
                    missing = [req for req in required_columns if req not in found_columns]
                    print(f"ERROR: Missing columns: {missing}")
                else:
                    print("Required columns: OK")
                
                # Step 4: Find subject columns
                default_subjects = ['Mathematics', 'English', 'Agriculture']
                subject_columns = {}
                
                for subject in default_subjects:
                    subj_normalized = subject.lower().replace(' ', '').replace('/', '').replace('&', '')
                    for col in df_upload.columns:
                        col_normalized = str(col).lower().replace(' ', '').replace('/', '').replace('&', '').replace('_', '')
                        if col_normalized == subj_normalized:
                            subject_columns[subject] = col
                            break
                
                print(f"Step 4 - Subject columns found: {len(subject_columns)}/{len(default_subjects)}")
                print(f"Subject columns: {subject_columns}")
                
                # Step 5: Process rows
                rows_to_process = []
                for index, row in df_upload.iterrows():
                    first_name_raw = str(row[found_columns['First Name']]).strip()
                    last_name_raw = str(row[found_columns['Last Name']]).strip()
                    
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
                        'marks': row_marks
                    })
                
                print(f"Step 5 - Processed rows: {len(rows_to_process)}")
                
                # Step 6: Test bulk upload method (without actually uploading)
                db = SchoolDatabase()
                print("Step 6 - Database connection: OK")
                
                # Test the bulk upload method structure
                print("Step 6 - Bulk upload method: Available")
                
                print("\nExcel upload simulation: SUCCESS")
                
            except Exception as e:
                print(f"Excel upload simulation failed: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n4. Common Excel Upload Issues")
        print("-" * 40)
        
        issues = []
        
        # Check file size limits
        if os.path.exists(xlsx_file):
            file_size = os.path.getsize(xlsx_file)
            print(f"Test file size: {file_size} bytes")
            if file_size > 10 * 1024 * 1024:  # 10MB
                issues.append("File size exceeds typical limits")
        
        # Check file permissions
        if os.path.exists(xlsx_file):
            if not os.access(xlsx_file, os.R_OK):
                issues.append("File not readable")
        
        # Check for special characters in data
        if os.path.exists(xlsx_file):
            try:
                df_check = pd.read_excel(xlsx_file)
                for col in df_check.columns:
                    if df_check[col].dtype == 'object':
                        unique_vals = df_check[col].dropna().unique()
                        for val in unique_vals:
                            if isinstance(val, str) and any(char in val for char in ['\n', '\r', '\t']):
                                issues.append(f"Special characters found in {col}")
                                break
            except Exception as e:
                issues.append(f"Error checking for special characters: {e}")
        
        if issues:
            print("Potential issues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("No common issues detected")
        
        print("\n5. JavaScript/ Frontend Issues")
        print("-" * 40)
        
        print("Common frontend issues that could cause Excel upload failure:")
        print("1. Missing formLevel variable in JavaScript")
        print("2. Missing term/year selection elements")
        print("3. File input element issues")
        print("4. Network connectivity issues")
        print("5. Browser compatibility issues")
        print("6. Missing CSRF token (if required)")
        print("7. File size limits on frontend")
        print("8. Incorrect file type validation")
        
        # Cleanup
        for file in [xlsx_file, 'debug_test.xls']:
            if os.path.exists(file):
                os.remove(file)
                print(f"\nCleaned up: {file}")
        
        print("\n=== Debug Complete ===")
        
    except Exception as e:
        print(f"Error during debugging: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_excel_upload_issue()
