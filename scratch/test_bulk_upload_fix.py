
import os
import sys
from datetime import datetime

# Add project root to sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from school_database import SchoolDatabase

def test_bulk_upload():
    print("Starting bulk upload test...")
    db = SchoolDatabase()
    
    # Sample data
    school_id = 1 # Assuming school 1 exists
    form_level = 1
    term = "Term 1"
    academic_year = "2024-2025"
    duplicate_action = "skip"
    
    rows_to_process = [
        {
            'first_name': 'TestStudent',
            'last_name': 'One',
            'is_duplicate': False,
            'existing_student_id': None,
            'marks': {
                'Mathematics': 85,
                'English': 72,
                'Chichewa': 65
            }
        },
        {
            'first_name': 'TestStudent',
            'last_name': 'Two',
            'is_duplicate': False,
            'existing_student_id': None,
            'marks': {
                'Mathematics': 45,
                'English': 38,
                'Chichewa': 50
            }
        }
    ]
    
    try:
        result = db.bulk_upload_students_data(
            rows_to_process=rows_to_process,
            term=term,
            academic_year=academic_year,
            form_level=form_level,
            school_id=school_id,
            duplicate_action=duplicate_action
        )
        
        print(f"Result: {result}")
        
        if result['success']:
            print("Bulk upload successful!")
            print(f"Success Count: {result['success_count']}")
            print(f"Mark Count: {result['mark_count']}")
            print(f"Fail Count: {result['fail_count']}")
            if result['errors']:
                print(f"Errors: {result['errors']}")
                
            # Verify in DB
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check students
                cursor.execute("SELECT student_id, first_name, last_name FROM students WHERE first_name LIKE 'TestStudent%'")
                students = cursor.fetchall()
                print(f"\nFound {len(students)} students in DB:")
                for s in students:
                    print(f"  ID: {s[0]}, Name: {s[1]} {s[2]}")
                    
                    # Check marks
                    cursor.execute("SELECT subject, mark, grade FROM student_marks WHERE student_id = ?", (s[0],))
                    marks = cursor.fetchall()
                    print(f"    Marks: {marks}")
        else:
            print(f"Bulk upload failed: {result.get('message')}")
            
    except Exception as e:
        print(f"Exception during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bulk_upload()
