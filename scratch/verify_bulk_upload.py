
import os
import sys
import json

# Add project root to path
sys.path.append(os.path.abspath('.'))

try:
    from school_database import SchoolDatabase
    db = SchoolDatabase()
    
    # Mock data for bulk upload
    rows_to_process = [
        {
            'first_name': 'BulkTest1',
            'last_name': 'Student1',
            'is_duplicate': False,
            'existing_student_id': None,
            'marks': {'English': 85, 'Mathematics': 90}
        },
        {
            'first_name': 'BulkTest2',
            'last_name': 'Student2',
            'is_duplicate': False,
            'existing_student_id': None,
            'marks': {'English': 75, 'Mathematics': 80}
        }
    ]
    
    school_id = 1 # Assuming school 1 exists
    term = 'Term 1'
    academic_year = '2025-2026'
    form_level = 1
    duplicate_action = 'skip'
    
    print("Starting bulk upload test...")
    result = db.bulk_upload_students_data(
        rows_to_process=rows_to_process,
        term=term,
        academic_year=academic_year,
        form_level=form_level,
        school_id=school_id,
        duplicate_action=duplicate_action
    )
    
    print(f"Result: {json.dumps(result, indent=2)}")
    
    if result.get('success') and result.get('success_count') == 2:
        print("Bulk upload test PASSED")
    else:
        print("Bulk upload test FAILED")
        
except Exception as e:
    print(f"Error during verification: {e}")
    import traceback
    traceback.print_exc()
