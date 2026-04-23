import sys
import os
import time
import json
import threading
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from school_database import SchoolDatabase
from termly_report_generator import TermlyReportGenerator
import app  # To access task_status and background_report_generation

def verify_caching():
    print("🚀 Starting Verification of Pre-computation and Caching Strategy")
    print("=" * 60)
    
    db = SchoolDatabase()
    generator = TermlyReportGenerator(db=db)
    
    # Test Data
    school_id = 1
    form_level = 3
    term = "Term 1"
    academic_year = "2025-2026"
    
    # 1. Ensure we have some students
    students = db.get_students_enrolled_in_term(form_level, term, academic_year, school_id)
    if not students:
        print("❌ No students found for testing. Please ensure database has test data.")
        return
    
    student_ids = [s['student_id'] for s in students]
    print(f"✅ Found {len(student_ids)} students in Form {form_level}")
    
    # 2. Trigger Background Task Manually
    task_id = "test_verification_task"
    print(f"⏳ Triggering background generation for task: {task_id}")
    
    # Run in a separate thread to simulate app.py behavior
    thread = threading.Thread(target=app.background_report_generation, 
                              args=(task_id, student_ids, term, academic_year, school_id))
    thread.start()
    
    # 3. Poll Status
    start_time = time.time()
    while True:
        status = app.task_status.get(task_id, {"status": "pending"})
        elapsed = time.time() - start_time
        print(f"[{elapsed:.1f}s] Status: {status['status']} | Progress: {status.get('progress', 0)}% | Msg: {status.get('message', '')}")
        
        if status['status'] in ['completed', 'failed']:
            break
        
        if elapsed > 60:
            print("❌ Timeout waiting for task completion")
            break
            
        time.sleep(2)
    
    if status['status'] == 'completed':
        print(f"✅ Task completed in {time.time() - start_time:.1f} seconds")
        
        # 4. Verify Files Exist on Disk
        all_exist = True
        for sid in student_ids:
            path = db.get_report_card_path(sid, term, academic_year, school_id)
            if not path or not os.path.exists(path):
                print(f"❌ Missing cached PDF for student {sid} at {path}")
                all_exist = False
            else:
                # print(f"✅ PDF exists: {path}")
                pass
        
        if all_exist:
            print("✅ ALL PDFs generated and cached on disk!")
            
        # 5. Verify Database precomputed results
        precomputed = db.get_precomputed_result(student_ids[0], term, academic_year, school_id)
        if precomputed:
            print(f"✅ Precomputed results found in DB for student {student_ids[0]}")
            # print(f"   Data: {json.dumps(precomputed, indent=2)[:200]}...")
        else:
            print(f"❌ Precomputed results NOT found for student {student_ids[0]}")
            
        # 6. Test Merging Performance
        print(f"⏳ Testing merging performance for {len(student_ids)} PDFs...")
        merge_start = time.time()
        merged_pdf = generator.merge_cached_pdfs(student_ids, term, academic_year, school_id)
        merge_end = time.time()
        
        if merged_pdf:
            print(f"✅ Merging completed in {merge_end - merge_start:.3f} seconds!")
            if (merge_end - merge_start) < 20:
                print("✨ PERFORMANCE TARGET MET: Batch generation is nearly instant!")
            else:
                print("⚠️ Performance target not quite met, but likely faster than before.")
        else:
            print("❌ Merging failed")
            
    else:
        print(f"❌ Task failed with status: {status['status']}")

if __name__ == "__main__":
    verify_caching()
