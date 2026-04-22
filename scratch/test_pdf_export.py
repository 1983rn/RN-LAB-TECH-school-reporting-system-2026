import sys
import traceback
from termly_report_generator import TermlyReportGenerator

sys.path.insert(0, 'd:/2025-2026/PRODUCTION/USA/RN-LAB-TECH-school-reporting-system-2026-1')

try:
    print("Initializing Generator...")
    gen = TermlyReportGenerator()
    print("Calling export_report_to_pdf_bytes...")
    pdf = gen.export_report_to_pdf_bytes(student_id=22, term='Term 1', academic_year='2025-2026', school_id=2)
    print("Result:", len(pdf) if pdf else 'None')
except Exception as e:
    print("Exception occurred:")
    traceback.print_exc()
