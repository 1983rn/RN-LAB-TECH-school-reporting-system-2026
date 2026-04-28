
import sys
import os
import time
import pandas as pd
import io

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from school_database import SchoolDatabase

def benchmark_bulk_upload():
    db = SchoolDatabase()
    
    # Create 50 dummy students
    students = []
    subjects = ['Mathematics', 'English', 'Agriculture', 'Biology', 'Chemistry', 'Chichewa', 'Geography', 'History', 'Physics', 'Social Studies']
    
    for i in range(50):
        student = {
            'First Name': f'BenchFirst{i}',
            'Last Name': f'BenchLast{i}',
        }
        for sub in subjects:
            student[sub] = 70 + (i % 30)
        students.append(student)
    
    df = pd.DataFrame(students)
    
    # Prepare rows_to_process like app.py does
    rows_to_process = []
    for _, row in df.iterrows():
        marks = {}
        for sub in subjects:
            marks[sub] = row[sub]
            
        rows_to_process.append({
            'first_name': row['First Name'],
            'last_name': row['Last Name'],
            'is_duplicate': False,
            'existing_student_id': None,
            'marks': marks
        })
    
    print(f"Starting bulk upload of {len(rows_to_process)} students with {len(subjects)} marks each...")
    start_time = time.time()
    
    result = db.bulk_upload_students_data(
        rows_to_process=rows_to_process,
        term='Term 1',
        academic_year='2025-2026',
        form_level=1,
        school_id=1,
        duplicate_action='skip'
    )
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"Result: {result['success']}, count: {result.get('success_count')}")
    print(f"Time taken: {duration:.2f} seconds")
    
    if duration > 10:
        print("WARNING: This might timeout on Render for larger files!")

if __name__ == "__main__":
    benchmark_bulk_upload()
