#!/usr/bin/env python3
"""
Termly Report Card Generator
Generates official school report cards showing only end-of-term exam marks
with teacher names for Forms 1-4 subjects and pass/fail determination
Pass Criteria: Must pass at least 6 subjects including English
Created: 2025-08-06
"""

import os
import io
import tempfile
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Union, Tuple

from school_database import SchoolDatabase

# Ensure reports directory exists
REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TermlyReportGenerator:
    """Class for generating professional termly report cards with pass/fail determination"""
    
    def __init__(self, school_name="[SCHOOL NAME]", school_address="[SCHOOL ADDRESS]", school_phone="[PHONE]", school_email="[EMAIL]", pta_fee="[PTA FEE AMOUNT]", sdf_fee="[SDF FEE AMOUNT]", boarding_fee="[BOARDING FEE AMOUNT]", boys_uniform="[BOYS UNIFORM REQUIREMENTS]", girls_uniform="[GIRLS UNIFORM REQUIREMENTS]", emblem_path=None):
        self.db = SchoolDatabase()
        self.standard_subjects = [
            'Agriculture', 'Biology', 'Bible Knowledge', 'Chemistry', 
            'Chichewa', 'Computer Studies', 'English', 'Geography', 
            'History', 'Life Skills/SOS', 'Mathematics', 'Physics', 'Business Studies', 'Home Economics'
        ]
        # School information - editable fields
        self.school_name = school_name
        self.school_address = school_address
        self.school_phone = school_phone
        self.school_email = school_email
        # Fee information - editable fields
        self.pta_fee = pta_fee
        self.sdf_fee = sdf_fee
        self.boarding_fee = boarding_fee
        # Uniform requirements - editable fields
        self.boys_uniform = boys_uniform
        self.girls_uniform = girls_uniform
        # Malawi Government emblem image path
        self.emblem_path = emblem_path
    
    def generate_termly_report_card(self, student_id: int, term: str, academic_year: str = '2024-2025'):
        """Generate a complete termly report card with pass/fail status"""
        try:
            report_data = self.db.generate_termly_report_card(student_id, term, academic_year)
            return self.format_report_card(report_data)
        except Exception as e:
            print(f"Error generating report card: {e}")
            return None
    
    def generate_progress_report(self, student_id: int, term: str, academic_year: str = '2024-2025', school_id: int = None):
        """Generate progress report using student marks from database"""
        try:
            # Get student info
            student = self.db.get_student_by_id(student_id)
            if not student:
                return None
            
            # Use student's school_id if not provided
            if not school_id:
                school_id = student.get('school_id')
            
            # Get student marks
            marks = self.db.get_student_marks(student_id, term, academic_year, school_id)
            if not marks:
                return None
            
            # Get position and points
            position_data = self.db.get_student_position_and_points(student_id, term, academic_year, student['grade_level'], school_id)
            
            return self.format_progress_report(student, marks, position_data, term, academic_year, school_id)
            
        except Exception as e:
            print(f"Error generating progress report: {e}")
            return None
    
    def format_report_card(self, report_data: dict) -> str:
        """Format simple report card matching original format"""
        if not report_data:
            return "No report data available"
        
        student = report_data['student_info']
        grades = report_data['subject_grades']
        stats = report_data['overall_statistics']
        
        # Get school settings for header and footer
        settings = self.db.get_school_settings(student.get('school_id'))
        school_name = settings.get('school_name', self.school_name)
        school_address = settings.get('school_address', 'P.O. Box [NUMBER], [CITY], Malawi')
        
        # Format address lines
        address_lines = school_address.split(', ')
        formatted_address = '\n'.join([f"                            {line.strip()}" for line in address_lines])
        
        # Simple header
        report = f"""
================================================================================
                            {school_name}
{formatted_address}

                         PROGRESS REPORT
================================================================================

Serial No:        {student['student_number']}
Student Name:     {student['first_name']} {student['last_name']}
Term:             {report_data['term'].replace('Term', '').strip()}
Form:             {student['grade_level']}
Year:             {report_data['academic_year']}

Subject                Marks Grade Comment      Signature
==============================================================================
"""
        
        # Subject grades in simple format
        for subject_name in self.standard_subjects:
            subject_found = False
            for grade in grades:
                if grade['subject_name'] == subject_name:
                    comment = self.db.get_teacher_comment(grade['letter_grade']) if hasattr(self.db, 'get_teacher_comment') else 'Good'
                    report += f"{subject_name:<20} {grade['percentage']:>3.0f} {grade['letter_grade']:>5} {comment:<12} ____________\n"
                    subject_found = True
                    break
            
            if not subject_found:
                report += f"{subject_name:<20} {'--':>3} {'--':>5} {'Not taken':<12} ____________\n"
        
        # Simple grading system
        if student['grade_level'] <= 2:
            report += f"\nGRADING: A(80-100) B(70-79) C(60-69) D(50-59) F(0-49)\n"
        else:
            report += f"\nMSCE GRADING: 1(75-100) 2(70-74) 3(65-69) 4(60-64) 5(55-59) 6(50-54) 7(45-49) 8(40-44) 9(0-39)\n"
        
        # Simple comments
        if stats['overall_status'] == 'PASS':
            form_teacher_comment = f"Good performance! Passed {stats['passed_subjects']} subjects."
            head_teacher_comment = "Well done. Keep up the good work."
        else:
            form_teacher_comment = f"Needs improvement. Focus on weak subjects."
            head_teacher_comment = "Extra effort required. Seek help from teachers."
        
        # Get school settings for footer information
        settings = self.db.get_school_settings(student.get('school_id'))
        
        report += f"""
FORM TEACHERS' COMMENT: {form_teacher_comment}
HEAD TEACHERS' COMMENT: {head_teacher_comment}

FORM TEACHER SIGN: ________________________
HEAD TEACHER SIGN: ________________________

==============================================================================
NEXT TERM BEGINS ON: {settings.get('next_term_begins', 'To be announced')}
FEES - BOARDING FEE: {settings.get('boarding_fee', 'MK 150,000')}
UNIFORM - GIRLS: {settings.get('girls_uniform', 'White blouse, black skirt, black shoes')}
UNIFORM - BOYS: {settings.get('boys_uniform', 'White shirt, black trousers, black shoes')}
==============================================================================

                        Generated by: RN_LAB_TECH
                     Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}
"""
        
        return report
    
    def generate_pass_fail_summary(self, form_level: int, term: str, academic_year: str = '2024-2025', school_id: int = None):
        """Generate a summary of pass/fail statistics for a class"""
        try:
            students = self.db.get_students_by_grade(form_level, school_id)
            summary_data = {
                'total_students': len(students),
                'passed_students': 0,
                'failed_students': 0,
                'failed_english_only': 0,
                'failed_insufficient_subjects': 0,
                'failed_both': 0,
                'student_details': []
            }
            
            print(f"Analyzing pass/fail status for Form {form_level} - {term}...")
            
            for student in students:
                try:
                    report_data = self.db.generate_termly_report_card(
                        student['student_id'], term, academic_year
                    )
                    
                    if report_data:
                        stats = report_data['overall_statistics']
                        student_detail = {
                            'name': f"{student['first_name']} {student['last_name']}",
                            'student_number': student['student_number'],
                            'status': stats['overall_status'],
                            'passed_subjects': stats['passed_subjects'],
                            'english_passed': stats['english_passed'],
                            'english_percentage': stats['english_percentage'],
                            'overall_average': stats['overall_average']
                        }
                        
                        summary_data['student_details'].append(student_detail)
                        
                        if stats['overall_status'] == 'PASS':
                            summary_data['passed_students'] += 1
                        else:
                            summary_data['failed_students'] += 1
                            
                            # Categorize failure reasons
                            if stats['passed_subjects'] >= 6 and not stats['english_passed']:
                                summary_data['failed_english_only'] += 1
                            elif stats['passed_subjects'] < 6 and stats['english_passed']:
                                summary_data['failed_insufficient_subjects'] += 1
                            else:
                                summary_data['failed_both'] += 1
                
                except Exception as e:
                    print(f"Error processing {student['first_name']} {student['last_name']}: {e}")
            
            return self.format_class_summary(summary_data, form_level, term, academic_year)
            
        except Exception as e:
            print(f"Error generating class summary: {e}")
            return None
    
    def format_class_summary(self, summary_data: dict, form_level: int, term: str, academic_year: str) -> str:
        """Format the class pass/fail summary"""
        
        pass_rate = (summary_data['passed_students'] / summary_data['total_students'] * 100) if summary_data['total_students'] > 0 else 0
        
        report = f"""
{'='*80}
                    CLASS PASS/FAIL SUMMARY REPORT
{'='*80}

Class: Form {form_level}
Term: {term}
Academic Year: {academic_year}
Date Generated: {datetime.now().strftime('%d/%m/%Y %H:%M')}

{'='*80}
OVERALL STATISTICS:
{'='*80}

Total Students: {summary_data['total_students']}
Students Passed: {summary_data['passed_students']} ({pass_rate:.1f}%)
Students Failed: {summary_data['failed_students']} ({100-pass_rate:.1f}%)

{'='*80}
FAILURE ANALYSIS:
{'='*80}

Failed due to English only: {summary_data['failed_english_only']} students
(Passed 6+ subjects but failed English)

Failed due to insufficient subjects: {summary_data['failed_insufficient_subjects']} students
(Passed English but failed to pass 6 subjects)

Failed both criteria: {summary_data['failed_both']} students
(Failed English AND passed less than 6 subjects)

{'='*80}
INDIVIDUAL STUDENT RESULTS:
{'='*80}

{'Name':<25} {'Std.No':<10} {'Status':<6} {'Subjects':<8} {'English':<8} {'Average':<8}
{'-'*80}
"""
        
        # Sort students by status (pass first) then by name
        sorted_students = sorted(summary_data['student_details'], 
                               key=lambda x: (x['status'] == 'FAIL', x['name']))
        
        for student in sorted_students:
            english_status = f"{student['english_percentage']:.0f}%"
            report += f"{student['name'][:24]:<25} {student['student_number']:<10} {student['status']:<6} {student['passed_subjects']:<8} {english_status:<8} {student['overall_average']:.1f}%\n"
        
        # Recommendations
        report += f"""

{'='*80}
RECOMMENDATIONS:
{'='*80}

For Students Who Failed English:
- Organize remedial English classes
- Focus on basic English communication skills
- Consider individual tutoring for English
- English is mandatory - no promotion without pass

For Students With Insufficient Subjects:
- Identify weakest subjects for targeted support
- Group remedial classes for common weak subjects
- Extra practice sessions before next examinations
- Peer tutoring programs

For High Performing Students:
- Advanced enrichment programs
- Peer mentoring opportunities
- Leadership roles in study groups

{'='*80}
"""
        
        return report
    
    def format_progress_report(self, student, marks, position_data, term, academic_year, school_id=None):
        """Format authentic Malawi school report card matching sample format"""
        form_level = student['grade_level']
        
        # Calculate statistics
        total_marks = sum(data['mark'] for data in marks.values()) if marks else 0
        subject_count = len(marks)
        average = total_marks / subject_count if subject_count > 0 else 0
        
        # Pass/fail determination
        passed_subjects = sum(1 for data in marks.values() if data['mark'] >= 50) if marks else 0
        english_mark = marks.get('English', {}).get('mark', 0)
        overall_status = 'PASS' if passed_subjects >= 6 and english_mark >= 50 else 'FAIL'
        
        # Get school settings
        settings = self.db.get_school_settings(school_id)
        school_name = settings.get('school_name', 'DEMO SECONDARY SCHOOL')
        
        # Authentic Malawi report card format
        report = f"""
================================================================================
                            {school_name}
                          PRIVATE BAG 211
                             KAWALE
                            LILONGWE
                             MALAWI

                         PROGRESS REPORT
================================================================================

Serial No:        {student.get('student_number', 'N/A')}
Student Name:     {student['first_name']} {student['last_name']}
Term:             {term.replace('Term', '').strip()}
Form:             {form_level}
Year:             {academic_year}
Position:         {position_data.get('position', 'N/A')}/{position_data.get('total_students', 'N/A')}

Subject                Marks Grade Pos  Comment      Signature
==============================================================================
"""
        
        # Add subjects with positions
        for subject in self.standard_subjects:
            if subject in marks:
                mark = marks[subject]['mark']
                grade = marks[subject]['grade']
                pos = self.db.get_subject_position(student['student_id'], subject, term, academic_year, form_level) if hasattr(self.db, 'get_subject_position') else 'N/A'
                comment = self.db.get_teacher_comment(grade) if hasattr(self.db, 'get_teacher_comment') else ('Good' if mark >= 50 else 'Fair')
                report += f"{subject:<20} {mark:>3} {grade:>5} {pos:>3}  {comment:<12} ____________\n"
            else:
                report += f"{subject:<20} {'--':>3} {'--':>5} {'--':>3}  {'Not taken':<12} ____________\n"
        
        # Add aggregate for Forms 3&4
        if form_level >= 3:
            # Calculate aggregate points
            if marks:
                best_marks = sorted([data['mark'] for data in marks.values()], reverse=True)[:6]
                grade_points = []
                for mark in best_marks:
                    grade = self.db.calculate_grade(mark, form_level) if hasattr(self.db, 'calculate_grade') else ('1' if mark >= 75 else '9')
                    grade_points.append(int(grade) if grade.isdigit() else 9)
                aggregate = sum(grade_points)
            else:
                aggregate = 54
            report += f"\n================================================================================\nAggregate Points (Best Six): {aggregate}    Remark: {overall_status}\n"
        
        # Grading system
        if form_level <= 2:
            report += f"\nGRADING: A(80-100) B(70-79) C(60-69) D(50-59) F(0-49)\n"
        else:
            report += f"\nMSCE GRADING: 1(75-100) 2(70-74) 3(65-69) 4(60-64) 5(55-59) 6(50-54) 7(45-49) 8(40-44) 9(0-39)\n"
        
        # Teacher comments
        if overall_status == 'PASS':
            form_teacher_comment = f"Good performance! Passed {passed_subjects} subjects with {average:.1f}% average."
            head_teacher_comment = "Well done. Keep up the excellent work."
        else:
            form_teacher_comment = f"Needs improvement. Focus on weak areas. Average: {average:.1f}%"
            head_teacher_comment = "Extra effort required. Seek help from teachers."
        
        report += f"""
FORM TEACHERS' COMMENT: {form_teacher_comment}
HEAD TEACHERS' COMMENT: {head_teacher_comment}

FORM TEACHER SIGN: ________________________
HEAD TEACHER SIGN: ________________________

==============================================================================
NEXT TERM BEGINS ON: {settings.get('next_term_begins', 'To be announced')}
FEES - BOARDING FEE: {settings.get('boarding_fee', 'MK 150,000')}
UNIFORM - GIRLS: {settings.get('girls_uniform', 'White blouse, black skirt, black shoes')}
UNIFORM - BOYS: {settings.get('boys_uniform', 'White shirt, black trousers, black shoes')}
==============================================================================

                        Generated by: RN_LAB_TECH
                     Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}
"""
        
        return report
    
    def generate_termly_report_pdf(self, student_info, subject_grades, overall_statistics, term, academic_year, output_path=None):
        """Generate PDF from termly report data
        
        Args:
            student_info: Dictionary containing student information
            subject_grades: List of subject grades
            overall_statistics: Dictionary of overall statistics
            term: Term number (1-3)
            academic_year: Academic year (e.g., '2024-2025')
            output_path: Optional custom output path. If None, uses the reports directory.
            
        Returns:
            str: Path to the generated PDF file
        """
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
            from reportlab.lib import colors
            from reportlab.lib.units import inch, cm
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
            import base64
            import io
            from datetime import datetime
            
            # Generate a safe filename
            student_name = f"{student_info.get('first_name', '')}_{student_info.get('last_name', '')}".replace(' ', '_')
            safe_filename = f"{student_name}_Term_{term}_Progress_Report_{academic_year.replace('/', '_')}.pdf"
            
            # Use provided output path or default to reports directory
            if not output_path:
                output_path = os.path.join(REPORTS_DIR, safe_filename)
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Create PDF in memory
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.8*inch, bottomMargin=0.8*inch)
            
            styles = getSampleStyleSheet()
            story = []
            
            # School header
            school_style = ParagraphStyle('School', parent=styles['Heading1'], fontSize=16, alignment=TA_CENTER)
            story.append(Paragraph(f"<b>{self.school_name}</b>", school_style))
            story.append(Paragraph(f"<b>{self.school_address}</b>", ParagraphStyle('Address', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER)))
            story.append(Spacer(1, 12))
            
            # Report title
            story.append(Paragraph(f"<b>PROGRESS REPORT</b>", ParagraphStyle('Title', parent=styles['Heading1'], fontSize=14, alignment=TA_CENTER)))
            story.append(Spacer(1, 12))
            
            # Student info
            student_data = [
                ['Serial No:', student_info['student_number']],
                ['Student Name:', f"{student_info['first_name']} {student_info['last_name']}"],
                ['Term:', term],
                ['Form:', str(student_info['grade_level'])],
                ['Year:', academic_year]
            ]
            
            student_table = Table(student_data, colWidths=[1.5*inch, 4*inch])
            student_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT')
            ]))
            story.append(student_table)
            story.append(Spacer(1, 12))
            
            # Grades table
            table_data = [['Subject', 'Marks', 'Grade', 'Comment']]
            for grade in subject_grades:
                comment = 'Good' if grade['percentage'] >= 50 else 'Needs improvement'
                table_data.append([grade['subject_name'], str(grade['percentage']), grade['letter_grade'], comment])
            
            grades_table = Table(table_data, colWidths=[2*inch, 1*inch, 1*inch, 2*inch])
            grades_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(grades_table)
            story.append(Spacer(1, 12))
            
            # Overall statistics
            story.append(Paragraph(f"<b>Overall Average: {overall_statistics['overall_average']}%</b>", styles['Normal']))
            story.append(Paragraph(f"<b>Overall Grade: {overall_statistics['overall_grade']}</b>", styles['Normal']))
            story.append(Paragraph(f"<b>Status: {overall_statistics['overall_status']}</b>", styles['Normal']))
            
            doc.build(story)
            buffer.seek(0)
            return buffer
            
        except ImportError:
            # Fallback if reportlab is not available
            return io.BytesIO(b'PDF generation requires reportlab library')
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return io.BytesIO(b'Error generating PDF')
    
    def export_report_to_pdf_bytes(self, student_id: int, term: str, academic_year: str = '2024-2025', school_id: int = None):
        """Export professional progress report as PDF and return as bytes"""
        try:
            print(f"DEBUG: Starting PDF generation for student {student_id}")
            pdf_filename = self.export_progress_report(student_id, term, academic_year, school_id)
            print(f"DEBUG: PDF filename generated: {pdf_filename}")
            
            if pdf_filename and os.path.exists(pdf_filename):
                print(f"DEBUG: PDF file exists, reading {pdf_filename}")
                with open(pdf_filename, 'rb') as f:
                    pdf_bytes = f.read()
                print(f"DEBUG: Read {len(pdf_bytes)} bytes from PDF")
                os.remove(pdf_filename)  # Clean up temporary file
                return pdf_bytes
            else:
                print(f"DEBUG: PDF file not found or not generated: {pdf_filename}")
                return b''
        except Exception as e:
            print(f"Error generating PDF bytes: {e}")
            import traceback
            traceback.print_exc()
            return b''
    
    def export_progress_report(self, student_id: int, term: str, academic_year: str = '2024-2025', school_id: int = None):
        """Export progress report to PDF file"""
        student = self.db.get_student_by_id(student_id)
        if not student:
            return None
        
        # Use student's school_id if not provided
        if not school_id:
            school_id = student.get('school_id')
            
        student_name = f"{student['first_name']}_{student['last_name']}"
        filename = f"{student_name}_{term}_Progress_Report_{academic_year.replace('-', '_')}.pdf"
        
        report = self.generate_progress_report(student_id, term, academic_year, school_id)
        print(f"DEBUG: Generated report text: {len(report) if report else 0} characters")
        
        if report:
            try:
                from reportlab.lib.pagesizes import A4
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageTemplate, Frame
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import inch
                from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
                from reportlab.lib import colors
                from reportlab.platypus.doctemplate import BaseDocTemplate
                
                # Create custom document with colorful border
                class BorderedDocTemplate(BaseDocTemplate):
                    def __init__(self, filename, **kwargs):
                        BaseDocTemplate.__init__(self, filename, **kwargs)
                        
                    def draw_border(self, canvas, doc):
                        # Draw colorful border
                        canvas.saveState()
                        
                        # Outer border - Blue
                        canvas.setStrokeColor(colors.blue)
                        canvas.setLineWidth(4)
                        canvas.rect(20, 20, A4[0]-40, A4[1]-40)
                        
                        # Middle border - Green
                        canvas.setStrokeColor(colors.green)
                        canvas.setLineWidth(2)
                        canvas.rect(30, 30, A4[0]-60, A4[1]-60)
                        
                        # Inner border - Red
                        canvas.setStrokeColor(colors.red)
                        canvas.setLineWidth(1)
                        canvas.rect(40, 40, A4[0]-80, A4[1]-80)
                        
                        canvas.restoreState()
                
                doc = BorderedDocTemplate(filename, pagesize=A4, topMargin=0.8*inch, bottomMargin=0.8*inch, leftMargin=0.8*inch, rightMargin=0.8*inch)
                
                # Create frame and page template with border
                frame = Frame(0.8*inch, 0.8*inch, A4[0]-1.6*inch, A4[1]-1.6*inch, leftPadding=0, bottomPadding=0, rightPadding=0, topPadding=0)
                template = PageTemplate(id='bordered', frames=frame, onPage=doc.draw_border)
                doc.addPageTemplates([template])
                styles = getSampleStyleSheet()
                story = []
                
                # Get school settings and student info for PDF processing
                settings = self.db.get_school_settings(school_id)
                school_name = settings.get('school_name', 'DEMO SECONDARY SCHOOL')
                student_info = self.db.get_student_by_id(student_id)
                form_level = student_info['grade_level'] if student_info else 1
                
                # Add logo if exists - smaller for A4 fit
                logo_path = "Malawi Government logo.png"
                if os.path.exists(logo_path):
                    try:
                        logo = Image(logo_path, width=0.8*inch, height=0.8*inch)
                        story.append(logo)
                        story.append(Spacer(1, 6))
                    except:
                        pass
                
                # Create styles with black text and background colors only
                school_name_style = ParagraphStyle('SchoolName', parent=styles['Heading1'], fontSize=16, alignment=TA_CENTER, fontName='Helvetica-Bold', textColor=colors.black)
                address_style = ParagraphStyle('Address', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER, fontName='Helvetica-Bold', textColor=colors.black)
                progress_style = ParagraphStyle('Progress', parent=styles['Heading1'], fontSize=14, alignment=TA_CENTER, fontName='Helvetica-Bold', textColor=colors.black)
                normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=9, fontName='Helvetica', textColor=colors.black)
                section_style = ParagraphStyle('Section', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold', textColor=colors.black)
                
                # Add school header with reduced spacing for Forms 3-4
                spacing = 2 if form_level >= 3 else 4
                story.append(Paragraph(f"<b>{school_name}</b>", school_name_style))
                story.append(Spacer(1, spacing))
                
                # Add school address from settings
                school_address = settings.get('school_address', 'P.O. Box [NUMBER], [CITY], Malawi')
                address_lines = school_address.split(', ')
                for line in address_lines:
                    story.append(Paragraph(f"<b>{line.strip()}</b>", address_style))
                story.append(Spacer(1, spacing))
                
                # Add progress report title
                story.append(Paragraph(f"<b>PROGRESS REPORT</b>", progress_style))
                story.append(Spacer(1, spacing))
                

                
                # Build table data directly from marks data
                marks = self.db.get_student_marks(student_id, term, academic_year, school_id)
                subject_teachers = self.db.get_subject_teachers(form_level, school_id)
                
                # Create table with actual data
                table_data = [['Subject', 'Marks', 'Grade', 'Position', 'Teachers Comment', 'Signature']]
                
                for subject in self.standard_subjects:
                    if subject in marks:
                        mark = marks[subject]['mark']
                        grade = marks[subject]['grade']
                        position = self.db.get_subject_position(student_id, subject, term, academic_year, form_level)
                        comment = self.db.get_teacher_comment(grade)
                        teacher = subject_teachers.get(subject, f"{subject} Teacher F{form_level}")
                        table_data.append([subject, str(mark), grade, str(position), comment, teacher[:15]])
                    else:
                        table_data.append([subject, '--', '--', '--', 'Not taken', '--'])
                
                # Create professional table
                table = Table(table_data, colWidths=[2*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1.5*inch, 1.2*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('TOPPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
                ]))
                
                # Add student information with uniform spacing using table
                student_data = [
                    ['Serial No:', student_info['student_number']],
                    ['Student Name:', f"{student_info['first_name']} {student_info['last_name']}"],
                    ['Term:', term.replace('Term', '').strip()],
                    ['Form:', str(form_level)],
                    ['Year:', academic_year]
                ]
                
                student_table = Table(student_data, colWidths=[1.5*inch, 4*inch])
                student_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP')
                ]))
                story.append(student_table)
                
                # Get position data for PDF
                position_data = self.db.get_student_position_and_points(student_id, term, academic_year, form_level, school_id)
                marks_pdf = self.db.get_student_marks(student_id, term, academic_year, school_id)
                subject_count = len(marks_pdf)
                
                # Check for insufficient subjects
                if subject_count <= 5:
                    overall_status_pdf = 'FAIL'
                    if form_level <= 2:
                        avg_grade = 'F'
                        position_info = f"{position_data['position']}/{position_data['total_students']}                    Average Grade: {avg_grade}    Remark: {overall_status_pdf}"
                    else:
                        # CRITICAL RULE: Forms 3&4 students with 1-5 subjects MUST get 54 aggregate points
                        position_data['aggregate_points'] = 54
                        position_info = f"{position_data['position']}/{position_data['total_students']}                    Aggregate Points: {position_data['aggregate_points']}    Remark: {overall_status_pdf}"
                else:
                    if form_level <= 2:
                        # Calculate average grade for junior forms
                        if form_level in [1, 2]:
                            passed_subjects = sum(1 for data in marks_pdf.values() if data['mark'] >= 50)
                        else:
                            passed_subjects = sum(1 for data in marks_pdf.values() if data['mark'] >= 40)
                        english_mark = marks_pdf.get('English', {}).get('mark', 0)
                        english_passed = self.db.is_english_passed(english_mark, form_level)
                        overall_status = self.db.determine_pass_fail_status(passed_subjects, english_passed)
                        
                        # CRITICAL RULE: Forms 1&2 failed students MUST get F grade
                        if overall_status == 'FAIL':
                            avg_grade = 'F'
                        else:
                            grades = [marks_pdf[subject]['grade'] for subject in marks_pdf if subject in marks_pdf]
                            if grades:
                                grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
                                for grade in grades:
                                    if grade in grade_counts:
                                        grade_counts[grade] += 1
                                
                                max_count = max(grade_counts.values())
                                most_common_grades = [grade for grade, count in grade_counts.items() if count == max_count]
                                
                                if len(most_common_grades) == 1:
                                    avg_grade = most_common_grades[0]
                                else:
                                    total_marks = sum(marks_pdf[subject]['mark'] for subject in marks_pdf if subject in marks_pdf)
                                    average_mark = total_marks / len(marks_pdf)
                                    avg_grade = self.db.calculate_grade(int(average_mark), form_level)
                                
                                # Ensure passing students don't get F grade
                                if avg_grade == 'F':
                                    passing_grades = [g for g in grades if g in ['A', 'B', 'C', 'D']]
                                    if passing_grades:
                                        pass_grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
                                        for grade in passing_grades:
                                            pass_grade_counts[grade] += 1
                                        
                                        max_pass_count = max(pass_grade_counts.values())
                                        most_common_pass_grades = [grade for grade, count in pass_grade_counts.items() if count == max_pass_count]
                                        
                                        if len(most_common_pass_grades) == 1:
                                            avg_grade = most_common_pass_grades[0]
                                        else:
                                            total_marks = sum(marks_pdf[subject]['mark'] for subject in marks_pdf if subject in marks_pdf)
                                            average_mark = total_marks / len(marks_pdf)
                                            avg_grade = self.db.calculate_grade(int(average_mark), form_level)
                            else:
                                avg_grade = 'D'  # Fallback for passed student
                        
                        overall_status_pdf = overall_status
                        position_info = f"{position_data['position']}/{position_data['total_students']}                    Average Grade: {avg_grade}    Remark: {overall_status_pdf}"
                    else:
                        # Get pass/fail status for PDF
                        if form_level in [1, 2]:
                            passed_subjects_pdf = sum(1 for data in marks_pdf.values() if data['mark'] >= 50)
                        else:
                            passed_subjects_pdf = sum(1 for data in marks_pdf.values() if data['mark'] >= 40)
                        english_mark_pdf = marks_pdf.get('English', {}).get('mark', 0)
                        english_passed_pdf = self.db.is_english_passed(english_mark_pdf, form_level)
                        overall_status_pdf = self.db.determine_pass_fail_status(passed_subjects_pdf, english_passed_pdf)
                        
                        position_info = f"{position_data['position']}/{position_data['total_students']}                    Aggregate Points: {position_data['aggregate_points']}    Remark: {overall_status_pdf}"
                
                # Add position as separate table row
                position_table = Table([['Position:', position_info]], colWidths=[1.5*inch, 4*inch])
                position_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                    ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP')
                ]))
                story.append(position_table)
                
                story.append(Spacer(1, 3 if form_level >= 3 else 6))
                
                # Add the table
                story.append(table)
                
                # Add aggregate points for senior forms (left-aligned below table)
                if form_level >= 3:
                    story.append(Spacer(1, 2))
                    story.append(Paragraph(f"<b>**Aggregate Points (Best Six): {position_data['aggregate_points']}    Remark: {overall_status_pdf}**</b>", ParagraphStyle('AggregatePoints', parent=styles['Normal'], fontSize=10, alignment=TA_LEFT, fontName='Helvetica-Bold', textColor=colors.black)))
                
                story.append(Spacer(1, 3 if form_level >= 3 else 6))
                
                # Define style and spacing for footer based on form level
                if form_level <= 2:
                    footer_style = ParagraphStyle('FooterStyle', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold', textColor=colors.black, leading=10)
                    grading_style = footer_style
                    spacer_size = 3
                    teacher_comment_spacer = 2
                else:
                    # Compact footer for Forms 3 and 4
                    footer_style = ParagraphStyle('FooterStyleSqueezed', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold', textColor=colors.black, leading=10)
                    grading_style = ParagraphStyle('GradingSqueezed', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold', textColor=colors.black, leading=10)
                    spacer_size = 2
                    teacher_comment_spacer = 2

                # Add grading system
                if form_level <= 2:
                    story.append(Paragraph(f"<b><u>GRADING:</u> A(80-100) B(70-79) C(60-69) D(50-59) F(0-49)</b>", grading_style))
                else:
                    story.append(Paragraph(f"<b><u>MSCE GRADING:</u> 1(75-100) 2(70-74) 3(65-69) 4(60-64) 5(55-59) 6(50-54) 7(45-49) 8(40-44) 9(0-39)</b>", grading_style))
                story.append(Spacer(1, spacer_size))
                
                # Add teacher comments
                marks = self.db.get_student_marks(student_id, term, academic_year, school_id)
                subject_count = len(marks)
                
                if subject_count <= 5:
                    # Insufficient subjects
                    overall_status = 'FAIL'
                    form_teacher_comment = f"FAILED - Insufficient subjects written ({subject_count}/6 minimum required)."
                    head_teacher_comment = "FAILED - Must write at least 6 subjects to be eligible for pass."
                else:
                    if form_level in [1, 2]:
                        passed_subjects = sum(1 for data in marks.values() if data['mark'] >= 50)
                    else:
                        passed_subjects = sum(1 for data in marks.values() if data['mark'] >= 40)
                    english_mark = marks.get('English', {}).get('mark', 0)
                    english_passed = self.db.is_english_passed(english_mark, form_level)
                    overall_status = self.db.determine_pass_fail_status(passed_subjects, english_passed)
                    average = sum(data['mark'] for data in marks.values()) / len(marks) if marks else 0
                    
                    if overall_status == 'PASS':
                        form_teacher_comment = f"PASSED - Good performance! Passed {passed_subjects} subjects with {average:.1f}% average."
                        head_teacher_comment = "PASSED - Well done. Keep up the good work."
                    else:
                        form_teacher_comment = f"FAILED - Needs improvement. Focus on weak subjects, especially English."
                        head_teacher_comment = "FAILED - Extra effort required. Seek help from teachers."
                
                story.append(Paragraph(f"<b><u>FORM TEACHERS' COMMENT:</u> {form_teacher_comment}</b>", footer_style))
                story.append(Paragraph(f"<b><u>HEAD TEACHERS' COMMENT:</u> {head_teacher_comment}</b>", footer_style))
                story.append(Spacer(1, teacher_comment_spacer))
                story.append(Paragraph(f"<b><u>FORM TEACHER SIGN:</u> ________________________</b>", footer_style))
                story.append(Paragraph(f"<b><u>HEAD TEACHER SIGN:</u> ________________________</b>", footer_style))
                story.append(Spacer(1, spacer_size))
                
                # Add fees and uniform information from school settings
                settings = self.db.get_school_settings(school_id)
                
                story.append(Paragraph(f"<b><u>NEXT TERM BEGINS ON:</u> {settings.get('next_term_begins', 'To be announced')}</b>", footer_style))
                story.append(Paragraph(f"<b><u>FEES</u> - <u>BOARDING FEE:</u> {settings.get('boarding_fee', 'MK 150,000')}</b>", footer_style))
                story.append(Paragraph(f"<b><u>UNIFORM - GIRLS:</u> {settings.get('girls_uniform', 'White blouse, black skirt, black shoes')}</b>", footer_style))
                story.append(Paragraph(f"<b><u>UNIFORM - BOYS:</u> {settings.get('boys_uniform', 'White shirt, black trousers, black shoes')}</b>", footer_style))
                story.append(Spacer(1, spacer_size))
                
                # Add footer with centered text
                # Compact final footer for all forms
                story.append(Paragraph(f"<b>Generated by: RN_LAB_TECH</b>", ParagraphStyle('Footer', parent=styles['Normal'], fontSize=7, alignment=TA_CENTER, fontName='Helvetica-Bold', textColor=colors.black)))
                story.append(Paragraph(f"<b>Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}</b>", ParagraphStyle('Footer', parent=styles['Normal'], fontSize=7, alignment=TA_CENTER, fontName='Helvetica-Bold', textColor=colors.black)))
                
                doc.build(story)
                return filename
            except Exception as e:
                print(f"Error creating PDF: {e}")
                # Fallback to text file
                filename = filename.replace('.pdf', '.txt')
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report)
                return filename
        return None
    
    def export_report_to_file(self, student_id: int, term: str, academic_year: str = '2024-2025', 
                             filename: str = None):
        """Export report card to text file"""
        if not filename:
            student = self.db.get_student_by_id(student_id)
            student_name = f"{student['first_name']}_{student['last_name']}" if student else f"student_{student_id}"
            filename = f"{student_name}_{term}_report_{academic_year.replace('-', '_')}.txt"
        
        report_card = self.generate_termly_report_card(student_id, term, academic_year)
        
        if report_card:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report_card)
                print(f"✅ Report card exported to: {filename}")
                return filename
            except Exception as e:
                print(f"❌ Error exporting report: {e}")
                return None
        else:
            print("❌ No report data to export")
            return None
    
    def export_class_summary_to_file(self, form_level: int, term: str, academic_year: str = '2024-2025', school_id: int = None):
        """Export class pass/fail summary to file"""
        filename = f"Form_{form_level}_{term}_PassFail_Summary_{academic_year.replace('-', '_')}.txt"
        
        summary = self.generate_pass_fail_summary(form_level, term, academic_year, school_id)
        
        if summary:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(summary)
                print(f"✅ Class summary exported to: {filename}")
                return filename
            except Exception as e:
                print(f"❌ Error exporting summary: {e}")
                return None
        else:
            print("❌ No summary data to export")
            return None


def main():
    """Demo function showing the enhanced termly report generator"""
    print("📊 ENHANCED TERMLY REPORT CARD GENERATOR")
    print("=" * 60)
    print("🎯 PASS CRITERIA:")
    print("   • Must pass at least 6 subjects")
    print("   • English is MANDATORY (must pass)")
    print("   • Pass mark: 50%")
    print("=" * 60)
    
    generator = TermlyReportGenerator()
    
    print("\n📚 Standard Subjects on Report Card:")
    for i, subject in enumerate(generator.standard_subjects, 1):
        marker = " *MANDATORY*" if subject == "English" else ""
        print(f"  {i:2d}. {subject}{marker}")
    
    print("\n" + "=" * 60)
    print("💡 USAGE EXAMPLES:")
    print("=" * 60)
    
    print("\n1. Generate individual report with pass/fail:")
    print("   generator.generate_termly_report_card(student_id=1, term='Term 1')")
    
    print("\n2. Generate class pass/fail summary:")
    print("   generator.generate_pass_fail_summary(form_level=1, term='Term 1')")
    
    print("\n3. Export individual report:")
    print("   generator.export_report_to_file(student_id=1, term='Term 1')")
    
    print("\n4. Export class summary:")
    print("   generator.export_class_summary_to_file(form_level=1, term='Term 1')")
    
    print("\n📋 NEW FEATURES:")
    print("  • Pass/Fail determination based on school criteria")
    print("  • English mandatory requirement enforcement")
    print("  • Detailed performance analysis")
    print("  • Class-wide pass/fail statistics")
    print("  • Failure reason categorization")
    print("  • Remedial action recommendations")


if __name__ == "__main__":
    main()
