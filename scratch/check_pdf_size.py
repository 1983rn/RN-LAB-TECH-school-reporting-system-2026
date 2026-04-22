import fitz
import io
import sys
import os

from termly_report_generator import TermlyReportGenerator

def test_sizes():
    class DummyDB:
        def get_student_by_id(self, student_id):
            return {
                'student_id': 1,
                'first_name': 'Test',
                'last_name': 'Student',
                'grade_level': 1,
                'student_number': '001',
                'school_id': 1
            }
        
        def get_school_settings(self, school_id):
            return {
                'school_name': 'Demo School',
                'school_address': 'P.O. Box 1',
                'junior_grading_rules': [
                    {'grade': 'A', 'min': 80, 'max': 100},
                    {'grade': 'B', 'min': 70, 'max': 79},
                    {'grade': 'C', 'min': 60, 'max': 69},
                    {'grade': 'D', 'min': 50, 'max': 59},
                    {'grade': 'F', 'min': 0, 'max': 49}
                ]
            }

        def get_student_position_and_points(self, *args, **kwargs):
            return {'position': 1, 'total_students': 100, 'aggregate_points': 10}

        def get_subject_position(self, *args, **kwargs):
            return 1
            
        def calculate_grade(self, mark, form_level, school_id=None):
            return 'A'
            
        def get_student_marks(self, *args, **kwargs):
            # Create marks for 14 subjects to max out space
            return {
                'Agriculture': {'mark': 80, 'grade': 'A'},
                'Biology': {'mark': 80, 'grade': 'A'},
                'Bible Knowledge': {'mark': 80, 'grade': 'A'},
                'Chemistry': {'mark': 80, 'grade': 'A'},
                'Chichewa': {'mark': 80, 'grade': 'A'},
                'Computer Studies': {'mark': 80, 'grade': 'A'},
                'English': {'mark': 80, 'grade': 'A'},
                'Geography': {'mark': 80, 'grade': 'A'},
                'History': {'mark': 80, 'grade': 'A'},
                'Life Skills/SOS': {'mark': 80, 'grade': 'A'},
                'Mathematics': {'mark': 80, 'grade': 'A'},
                'Physics': {'mark': 80, 'grade': 'A'},
                'Business Studies': {'mark': 80, 'grade': 'A'},
                'Home Economics': {'mark': 80, 'grade': 'A'}
            }
            
        def get_subject_teachers(self, form_level, school_id):
            return {}

    gen = TermlyReportGenerator()
    gen.db = DummyDB()
    
    buf = gen.export_progress_report(1, 'Term 1', '2025')
    if buf:
        buf.seek(0)
        doc = fitz.open(stream=buf.read(), filetype="pdf")
        print(f"Pages: {len(doc)}")
        
        # Save to file to see actual page dimension usage if needed
        with open('scratch/test_out.pdf', 'wb') as f:
            f.write(buf.getvalue())
    else:
        print("Failed to generate PDF")

if __name__ == "__main__":
    test_sizes()
