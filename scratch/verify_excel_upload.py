import os
import sys

# Add project root to path
sys.path.insert(0, r'd:\2025-2026\PRODUCTION\USA\RN-LAB-TECH-school-reporting-system-2026-1')

import pandas as pd
from school_database import SchoolDatabase

def test_excel_upload_logic():
    excel_path = r'd:\2025-2026\PRODUCTION\USA\RN-LAB-TECH-school-reporting-system-2026-1\scratch\students_test.xlsx'
    
    if not os.path.exists(excel_path):
        print(f"Error: {excel_path} not found")
        return

    print(f"Reading {excel_path}...")
    df = pd.read_excel(excel_path)
    print("Columns found:", df.columns.tolist())
    
    # Logic from app.py
    df.columns = [str(col).strip() for col in df.columns]
    required_columns = ['First Name', 'Last Name']
    found_columns = {}
    for req in required_columns:
        for col in df.columns:
            if col.lower() == req.lower():
                found_columns[req] = col
                break
    
    if len(found_columns) < len(required_columns):
        print("Error: Missing columns")
        return
        
    db = SchoolDatabase()
    school_id = 1 # Sample school ID
    form_level = 1
    
    print("Processing students...")
    for index, row in df.iterrows():
        first_name = str(row[found_columns['First Name']]).strip()
        last_name = str(row[found_columns['Last Name']]).strip()
        
        if not first_name or not last_name or first_name.lower() == 'nan' or last_name.lower() == 'nan':
            print(f"Skipping empty/nan row {index}")
            continue
            
        print(f"Adding: {first_name} {last_name}")
        
        student_data = {
            'first_name': first_name,
            'last_name': last_name,
            'grade_level': form_level
        }
        
        # Call add_student
        try:
            student_id = db.add_student(student_data, school_id)
            print(f"Successfully added with ID: {student_id}")
        except Exception as e:
            print(f"Error adding student: {e}")

    # Verify alphabetical sorting (retrieve from DB)
    print("\nVerifying sorting in DB...")
    students = db.get_students_by_grade(form_level, school_id)
    print("Students in DB (should be alphabetical):")
    for s in students:
        print(f"- {s['first_name']} {s['last_name']}")

    print("\nLogic verification complete.")

if __name__ == "__main__":
    test_excel_upload_logic()
