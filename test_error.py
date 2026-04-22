import os
import sys

# Set path to allow importing from current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from termly_report_generator import TermlyReportGenerator
import traceback

print("Initializing Generator...")
gen = TermlyReportGenerator()

try:
    print("Exporting PDF for student 22...")
    buf = gen.export_progress_report(student_id=22, term='Term 1', academic_year='2025-2026', school_id=2)
    if buf:
        print("Success! Buffer size:", len(buf.getvalue()) if hasattr(buf, 'getvalue') else 'unknown')
    else:
        print("Returned None!")
except Exception as e:
    print("Caught Exception in script:")
    traceback.print_exc()
