import os
import sys
from PIL import Image as PILImage
from reportlab.lib.units import inch

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from school_database import SchoolDatabase
from termly_report_generator import TermlyReportGenerator

def verify_signatures():
    db = SchoolDatabase()
    generator = TermlyReportGenerator()
    
    # 1. Create a dummy signature image
    sig_dir = os.path.join(os.getcwd(), 'static', 'uploads', 'signatures', 'test')
    os.makedirs(sig_dir, exist_ok=True)
    sig_path = os.path.join(sig_dir, 'test_sig.png')
    
    # Create a 200x50 black rectangle as a "signature"
    img = PILImage.new('RGBA', (200, 50), color=(0, 0, 255, 255))
    img.save(sig_path)
    print(f"Created dummy signature at: {sig_path}")
    
    # 2. Update a school's settings (School ID 2 is common in this DB)
    school_id = 2
    try:
        db.update_school_settings({
            'form_1_teacher_signature': sig_path,
            'head_teacher_signature': sig_path
        }, school_id)
        print("Updated school settings with mock signature path.")
    except Exception as e:
        print(f"Error updating settings: {e}")
        return

    # 3. Try to generate a report for a student in this school
    student_id = None
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT student_id, term, academic_year FROM student_marks WHERE school_id = 2 LIMIT 1")
        res = cursor.fetchone()
        if res:
            student_id, term, ay = res
            print(f"Testing with student {student_id}, {term}, {ay}")
            
            # Generate PDF
            try:
                # Direct check on image loading
                from reportlab.platypus import Image as RLImage
                test_img = RLImage(sig_path)
                print(f"ReportLab can load image: {sig_path}")
                
                # Use a buffer to capture possible prints in generator
                import io
                from contextlib import redirect_stdout, redirect_stderr
                
                out = io.StringIO()
                err = io.StringIO()
                
                with redirect_stdout(out), redirect_stderr(err):
                    pdf_output = generator.export_progress_report(student_id, term, ay, school_id=school_id)
                
                print("STDOUT from generator:", out.getvalue())
                print("STDERR from generator:", err.getvalue())
                
                if pdf_output:
                    output_path = os.path.join(os.path.dirname(os.getcwd()), 'test_signature_report.pdf')
                    with open(output_path, 'wb') as f:
                        f.write(pdf_output.getvalue())
                    print(f"SUCCESS: PDF generated with signature at {output_path}")
                else:
                    print("FAILED: PDF generation returned None.")
            except Exception as e:
                import traceback
                print(f"FAILED: PDF generation error: {e}")
                traceback.print_exc()
        else:
            print("No marks found for school_id 2 to test.")

if __name__ == "__main__":
    verify_signatures()
