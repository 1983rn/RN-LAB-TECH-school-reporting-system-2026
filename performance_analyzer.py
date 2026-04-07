#!/usr/bin/env python3
"""
Performance Analyzer Module
Generates reports for best performing students by class, subject, and department
Departments: Sciences, Humanities, Languages
Created: 2025-08-06
"""

from school_database import SchoolDatabase
from datetime import datetime
import json
from typing import List, Dict, Optional

class PerformanceAnalyzer:
    """Class for analyzing and generating performance reports"""
    
    def __init__(self, school_name="[SCHOOL NAME]"):
        self.db = SchoolDatabase()
        self.school_name = school_name
        
        # Department classifications
        self.departments = {
            'Sciences': {
                'subjects': ['Agriculture', 'Biology', 'Chemistry', 'Physics', 'Mathematics', 'Computer Studies'],
                'description': 'Science and Mathematics Department'
            },
            'Humanities': {
                'subjects': ['Bible Knowledge', 'Geography', 'History', 'Life Skills/SOS'],
                'description': 'Humanities and Social Studies Department'
            },
            'Languages': {
                'subjects': ['English', 'Chichewa'],
                'description': 'Languages Department'
            }
        }
        
        self.all_subjects = [
            'Agriculture', 'Biology', 'Bible Knowledge', 'Chemistry', 
            'Chichewa', 'Computer Studies', 'English', 'Geography', 
            'History', 'Life Skills/SOS', 'Mathematics', 'Physics', 'Business Studies', 'Home Economics'
        ]
    
    def get_top_performers(self, category: str, form_level: int, term: str, academic_year: str = '2024-2025') -> List[Dict]:
        """Get top performers by category"""
        return self.db.get_top_performers(category, form_level, term, academic_year)
    
    def get_best_performing_students_by_class(self, form_level: int, term: str, academic_year: str = '2024-2025', top_n: int = 10) -> Dict:
        """Generate best performing students report for a specific class"""
        try:
            rankings = self.db.get_student_rankings(form_level, term, academic_year)
            if not rankings:
                return None
                
            top_students = rankings[:top_n]
            
            return {
                'report_type': f'Best Performing Students - Form {form_level}',
                'form_level': form_level,
                'term': term,
                'academic_year': academic_year,
                'top_students': top_students,
                'generated_date': datetime.now().isoformat()
            }
                
        except Exception as e:
            print(f"Error generating class performance report: {e}")
            return None
    
    def get_best_performing_students_by_subject(self, subject_name: str, term: str, academic_year: str = '2024-2025', top_n: int = 10) -> Dict:
        """Generate best performing students report for a specific subject across all forms"""
        try:
            with self.db.get_connection() as conn:
                query = """
                    SELECT 
                        s.student_id,
                        s.student_number,
                        s.first_name,
                        s.last_name,
                        s.grade_level,
                        sm.mark as percentage,
                        sm.grade as letter_grade
                    FROM students s
                    JOIN student_marks sm ON s.student_id = sm.student_id
                    WHERE sm.subject = ?
                    AND sm.term = ?
                    AND sm.academic_year = ?
                    AND s.status = 'Active'
                    ORDER BY sm.mark DESC
                    LIMIT ?
                """
                
                import pandas as pd
                df = pd.read_sql_query(query, conn, params=(subject_name, term, academic_year, top_n))
                
                return {
                    'report_type': f'Best Performing Students - {subject_name}',
                    'subject_name': subject_name,
                    'term': term,
                    'academic_year': academic_year,
                    'top_students': df.to_dict('records'),
                    'generated_date': datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"Error generating subject performance report: {e}")
            return None
    
    def get_best_performing_students_by_department(self, department_name: str, term: str, academic_year: str = '2024-2025', top_n: int = 10) -> Dict:
        """Generate best performing students report for a specific department"""
        try:
            if department_name not in self.departments:
                raise ValueError(f"Department '{department_name}' not found. Available departments: {list(self.departments.keys())}")
            
            department_subjects = self.departments[department_name]['subjects']
            subjects_placeholder = ','.join(['?' for _ in department_subjects])
            
            with self.db.get_connection() as conn:
                query = f"""
                    SELECT 
                        s.student_id,
                        s.student_number,
                        s.first_name,
                        s.last_name,
                        s.grade_level,
                        AVG(sm.mark) as department_average,
                        COUNT(sm.mark_id) as subjects_taken_in_dept,
                        SUM(CASE WHEN sm.mark >= 50 THEN 1 ELSE 0 END) as subjects_passed_in_dept,
                        MIN(sm.mark) as lowest_mark_in_dept,
                        MAX(sm.mark) as highest_mark_in_dept
                    FROM students s
                    JOIN student_marks sm ON s.student_id = sm.student_id
                    WHERE sm.subject IN ({subjects_placeholder})
                    AND sm.term = ?
                    AND sm.academic_year = ?
                    AND s.status = 'Active'
                    GROUP BY s.student_id
                    HAVING subjects_taken_in_dept >= 2
                    ORDER BY department_average DESC, subjects_passed_in_dept DESC
                    LIMIT ?
                """
                
                import pandas as pd
                params = department_subjects + [term, academic_year, top_n]
                df = pd.read_sql_query(query, conn, params=params)
                
                return {
                    'report_type': f'Best Performing Students - {department_name} Department',
                    'department_name': department_name,
                    'department_subjects': department_subjects,
                    'term': term,
                    'academic_year': academic_year,
                    'top_students': df.to_dict('records'),
                    'generated_date': datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"Error generating department performance report: {e}")
            return None
    
    def generate_comprehensive_performance_report(self, term: str, academic_year: str = '2024-2025') -> Dict:
        """Generate a comprehensive performance report covering all categories"""
        try:
            comprehensive_report = {
                'report_type': 'Comprehensive Performance Analysis',
                'term': term,
                'academic_year': academic_year,
                'generated_date': datetime.now().isoformat(),
                'school_name': self.school_name,
                'performance_data': {}
            }
            
            # Best performers by class (Forms 1-4)
            comprehensive_report['performance_data']['by_class'] = {}
            for form_level in [1, 2, 3, 4]:
                class_report = self.get_best_performing_students_by_class(form_level, term, academic_year, 5)
                if class_report:
                    comprehensive_report['performance_data']['by_class'][f'Form_{form_level}'] = class_report
            
            # Best performers by subject
            comprehensive_report['performance_data']['by_subject'] = {}
            for subject in self.all_subjects:
                subject_report = self.get_best_performing_students_by_subject(subject, term, academic_year, 5)
                if subject_report:
                    comprehensive_report['performance_data']['by_subject'][subject] = subject_report
            
            # Best performers by department
            comprehensive_report['performance_data']['by_department'] = {}
            for department in self.departments.keys():
                dept_report = self.get_best_performing_students_by_department(department, term, academic_year, 5)
                if dept_report:
                    comprehensive_report['performance_data']['by_department'][department] = dept_report
            
            return comprehensive_report
            
        except Exception as e:
            print(f"Error generating comprehensive performance report: {e}")
            return None
    
    def format_class_performance_report(self, report_data: Dict) -> str:
        """Format class performance report for display/printing"""
        if not report_data or not report_data.get('top_students'):
            return "No performance data available"
        
        report = f"""
{'='*90}
                            REPUBLIC OF MALAWI
                         MINISTRY OF EDUCATION
                      
                    [🇲🇼 MALAWI GOVERNMENT EMBLEM 🇲🇼]
                         UNITY - WORK - PROGRESS
                        
{'='*90}

                  BEST PERFORMING STUDENTS REPORT
                           {report_data['report_type']}

{'='*90}
SCHOOL: {self.school_name}
ACADEMIC YEAR: {report_data['academic_year']}
TERM: {report_data['term']}
REPORT GENERATED: {datetime.now().strftime('%d/%m/%Y at %H:%M')}

{'='*90}
TOP PERFORMING STUDENTS - FORM {report_data['form_level']}
{'='*90}

{'Rank':<6} {'Student No':<12} {'Full Name':<25} {'Average':<8} {'Subjects':<8} {'Passed':<7} {'Range':<12}
{'-'*90}
"""
        
        for i, student in enumerate(report_data['top_students'], 1):
            name = f"{student['first_name']} {student['last_name']}"
            range_marks = f"{student['lowest_mark']:.0f}-{student['highest_mark']:.0f}%"
            
            # Fix: For Forms 1/2, if PASS and grade is F, show D
            grade = student.get('letter_grade', 'F')
            if student.get('grade_level') in [1, 2] and student.get('overall_status') == 'PASS' and grade == 'F':
                grade = 'D'
            report += f"{i:<6} {student['student_number']:<12} {name[:24]:<25} "
            report += f"{student['overall_average']:.1f}%{'':<2} {student['subjects_taken']:<8} "
            report += f"{student['subjects_passed']:<7} {range_marks:<12} {grade:<6}\n"
        
        # Add footer with official receipt info
        receipt_number = datetime.now().strftime('%Y%m%d%H%M%S')
        receipt_datetime = datetime.now().strftime('%d/%m/%Y at %H:%M:%S')
        
        report += f"""

{'='*90}
PERFORMANCE ANALYSIS:
{'='*90}

Excellence Recognition: These students have demonstrated outstanding academic 
performance in Form {report_data['form_level']} during {report_data['term']} {report_data['academic_year']}.

Ranking Criteria:
1. Overall Average Percentage (Primary)
2. Number of Subjects Passed (Secondary)
3. Consistency across subjects

{'='*90}
                        END OF PERFORMANCE REPORT
{'='*90}

{'-'*90}
Official Performance Report No: {receipt_number} ({receipt_datetime})
Created by: RN_LAB_TECH
{'-'*90}

"""
        return report
    
    def format_subject_performance_report(self, report_data: Dict) -> str:
        """Format subject performance report for display/printing"""
        if not report_data or not report_data.get('top_students'):
            return "No performance data available"
        
        report = f"""
{'='*90}
                            REPUBLIC OF MALAWI
                         MINISTRY OF EDUCATION
                      
                    [🇲🇼 MALAWI GOVERNMENT EMBLEM 🇲🇼]
                         UNITY - WORK - PROGRESS
                        
{'='*90}

                  BEST PERFORMING STUDENTS REPORT
                           {report_data['report_type']}

{'='*90}
SCHOOL: {self.school_name}
SUBJECT: {report_data['subject_name']}
ACADEMIC YEAR: {report_data['academic_year']}
TERM: {report_data['term']}
REPORT GENERATED: {datetime.now().strftime('%d/%m/%Y at %H:%M')}

{'='*90}
TOP PERFORMERS IN {report_data['subject_name'].upper()}
{'='*90}

{'Rank':<6} {'Student No':<12} {'Full Name':<25} {'Form':<6} {'Mark':<8} {'Grade':<6} {'Teacher':<20}
{'-'*90}
"""
        
        for i, student in enumerate(report_data['top_students'], 1):
            name = f"{student['first_name']} {student['last_name']}"
            
            report += f"{i:<6} {student['student_number']:<12} {name[:24]:<25} "
            report += f"{student['grade_level']:<6} {student['percentage']:.1f}%{'':<2} "
            report += f"{student['letter_grade']:<6} {student['teacher_name'][:19]:<20}\n"
        
        # Add footer with official receipt info
        receipt_number = datetime.now().strftime('%Y%m%d%H%M%S')
        receipt_datetime = datetime.now().strftime('%d/%m/%Y at %H:%M:%S')
        
        report += f"""

{'='*90}
SUBJECT PERFORMANCE ANALYSIS:
{'='*90}

Subject Excellence: These students achieved the highest marks in 
{report_data['subject_name']} during {report_data['term']} {report_data['academic_year']}.

Recognition: Outstanding achievement in {report_data['subject_name']} 
demonstrates dedication and mastery of the subject content.

{'='*90}
                        END OF SUBJECT REPORT
{'='*90}

{'-'*90}
Official Performance Report No: {receipt_number} ({receipt_datetime})
Created by: RN_LAB_TECH
{'-'*90}

"""
        return report
    
    def format_department_performance_report(self, report_data: Dict) -> str:
        """Format department performance report for display/printing"""
        if not report_data or not report_data.get('top_students'):
            return "No performance data available"
        
        subjects_list = ', '.join(report_data['department_subjects'])
        
        report = f"""
{'='*90}
                            REPUBLIC OF MALAWI
                         MINISTRY OF EDUCATION
                      
                    [🇲🇼 MALAWI GOVERNMENT EMBLEM 🇲🇼]
                         UNITY - WORK - PROGRESS
                        
{'='*90}

                  BEST PERFORMING STUDENTS REPORT
                           {report_data['report_type']}

{'='*90}
SCHOOL: {self.school_name}
DEPARTMENT: {report_data['department_name']}
SUBJECTS INCLUDED: {subjects_list}
ACADEMIC YEAR: {report_data['academic_year']}
TERM: {report_data['term']}
REPORT GENERATED: {datetime.now().strftime('%d/%m/%Y at %H:%M')}

{'='*90}
TOP PERFORMERS - {report_data['department_name'].upper()} DEPARTMENT
{'='*90}

{'Rank':<6} {'Student No':<12} {'Full Name':<25} {'Form':<6} {'Avg':<8} {'Subjects':<8} {'Passed':<7}
{'-'*90}
"""
        
        for i, student in enumerate(report_data['top_students'], 1):
            name = f"{student['first_name']} {student['last_name']}"
            
            report += f"{i:<6} {student['student_number']:<12} {name[:24]:<25} "
            report += f"{student['grade_level']:<6} {student['department_average']:.1f}%{'':<2} "
            report += f"{student['subjects_taken_in_dept']:<8} {student['subjects_passed_in_dept']:<7}\n"
        
        # Add footer with official receipt info
        receipt_number = datetime.now().strftime('%Y%m%d%H%M%S')
        receipt_datetime = datetime.now().strftime('%d/%m/%Y at %H:%M:%S')
        
        report += f"""

{'='*90}
DEPARTMENT PERFORMANCE ANALYSIS:
{'='*90}

Department Excellence: These students demonstrated exceptional performance 
across multiple subjects in the {report_data['department_name']} Department.

Subjects Evaluated: {subjects_list}

Recognition Criteria:
- Average performance across department subjects
- Minimum of 2 subjects taken in the department
- Consistency in department subject performance

{'='*90}
                     END OF DEPARTMENT REPORT
{'='*90}

{'-'*90}
Official Performance Report No: {receipt_number} ({receipt_datetime})
Created by: RN_LAB_TECH
{'-'*90}

"""
        return report
    
    def export_performance_report(self, report_type: str, **kwargs) -> str:
        """Export performance report to file"""
        try:
            if report_type == 'class':
                report_data = self.get_best_performing_students_by_class(**kwargs)
                formatted_report = self.format_class_performance_report(report_data)
                filename = f"Best_Performers_Form_{kwargs['form_level']}_{kwargs['term']}_{kwargs.get('academic_year', '2024-2025').replace('-', '_')}.txt"
            
            elif report_type == 'subject':
                report_data = self.get_best_performing_students_by_subject(**kwargs)
                formatted_report = self.format_subject_performance_report(report_data)
                subject_clean = kwargs['subject_name'].replace('/', '_').replace(' ', '_')
                filename = f"Best_Performers_{subject_clean}_{kwargs['term']}_{kwargs.get('academic_year', '2024-2025').replace('-', '_')}.txt"
            
            elif report_type == 'department':
                report_data = self.get_best_performing_students_by_department(**kwargs)
                formatted_report = self.format_department_performance_report(report_data)
                filename = f"Best_Performers_{kwargs['department_name']}_Dept_{kwargs['term']}_{kwargs.get('academic_year', '2024-2025').replace('-', '_')}.txt"
            
            elif report_type == 'top_performers':
                # New PDF export for top performers
                formatted_report = self.format_top_performers_pdf(**kwargs)
                category = kwargs['category'].replace(' ', '_')
                filename = f"Top_Performers_{category}_Form_{kwargs['form_level']}_{kwargs['term']}_{kwargs.get('academic_year', '2024-2025').replace('-', '_')}.pdf"
                return self.generate_pdf_report(formatted_report, filename)
            
            elif report_type == 'rankings':
                # New PDF export for rankings
                formatted_report = self.format_rankings_pdf(**kwargs)
                filename = f"Rankings_Form_{kwargs['form_level']}_{kwargs['term']}_{kwargs.get('academic_year', '2024-2025').replace('-', '_')}.pdf"
                return self.generate_pdf_report(formatted_report, filename)
            
            else:
                raise ValueError(f"Unknown report type: {report_type}")
            
            if formatted_report and "No performance data available" not in formatted_report:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(formatted_report)
                print("Performance report exported to: " + filename)
                return filename
            else:
                print("No data to export")
                return None
                
        except Exception as e:
            print("Error exporting performance report: " + str(e))
            return None
    
    def export_rankings_to_excel(self, form_level: int, term: str, academic_year: str) -> str:
        """Export rankings to Excel file"""
        try:
            rankings = self.db.get_student_rankings(form_level, term, academic_year)
            
            if not rankings:
                return None
            
            import pandas as pd
            df = pd.DataFrame(rankings)
            
            filename = f"Form_{form_level}_Rankings_{term}_{academic_year.replace('-', '_')}.xlsx"
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Rankings', index=False)
                
                # Add summary sheet
                summary_data = {
                    'Total Students': [len(rankings)],
                    'Students Passed': [len([r for r in rankings if r['status'] == 'PASS'])],
                    'Students Failed': [len([r for r in rankings if r['status'] == 'FAIL'])],
                    'Average Mark': [sum(r['average'] for r in rankings) / len(rankings)]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            return filename
            
        except Exception as e:
            print(f"Error exporting rankings to Excel: {e}")
            return None
    
    def format_top_performers_pdf(self, **kwargs) -> str:
        """Format top performers data for PDF generation"""
        category = kwargs.get('category', 'overall')
        form_level = kwargs.get('form_level', 1)
        term = kwargs.get('term', 'Term 1')
        academic_year = kwargs.get('academic_year', '2024-2025')
        performers = kwargs.get('performers', [])
        
        category_titles = {
            'overall': 'Best Overall Students',
            'sciences': 'Best in Sciences Department',
            'humanities': 'Best in Humanities Department',
            'languages': 'Best in Languages Department'
        }
        
        title = category_titles.get(category, f'Best in {category.title()}')
        
        report = f"""
{'='*90}
                            REPUBLIC OF MALAWI
                         MINISTRY OF EDUCATION
                      
                         UNITY - WORK - PROGRESS
                        
{'='*90}

                      TOP PERFORMERS REPORT
                           {title}

{'='*90}
SCHOOL: {school_name}
FORM LEVEL: {form_level}
ACADEMIC YEAR: {academic_year}
TERM: {term}
REPORT GENERATED: {datetime.now().strftime('%d/%m/%Y %H:%M')}

{'='*90}
TOP PERFORMERS - {title.upper()}
{'='*90}

{'Rank':<6} {'Student Name':<25} {'Average':<10} {'Grade/Points':<12} {'Excellence Area':<20}
{'-'*90}
"""
        
        for i, performer in enumerate(performers, 1):
            name = performer['name'][:24]
            average = f"{performer['average']:.1f}%"
            
            # Display grade or aggregate points based on form level
            if form_level >= 3 and performer.get('aggregate_points'):
                grade_display = f"{performer['aggregate_points']} pts"
            else:
                grade_display = performer.get('grade', 'N/A')
            
            excellence_area = performer.get('excellence_area', category.title())[:19]
            
            report += f"{i:<6} {name:<25} {average:<10} {grade_display:<12} {excellence_area:<20}\n"
        
        # Add footer with official receipt info
        receipt_number = datetime.now().strftime('%Y%m%d%H%M%S')
        receipt_datetime = datetime.now().strftime('%d/%m/%Y at %H:%M:%S')
        
        report += f"""

{'='*90}
PERFORMANCE ANALYSIS:
{'='*90}

Excellence Recognition: These students have demonstrated outstanding academic 
performance in {title} during {term} {academic_year}.

Category Details:
"""
        
        if category == 'sciences':
            report += "- Agriculture, Biology, Chemistry, Computer Studies, Mathematics, Physics\n"
        elif category == 'humanities':
            report += "- Bible Knowledge, Geography, History, Life Skills/SOS\n"
        elif category == 'languages':
            report += "- English, Chichewa\n"
        else:
            report += "- Overall performance across all subjects\n"
        
        report += f"""
Ranking Criteria:
1. Academic Performance (Primary)
2. Subject Category Excellence
3. Consistency across subjects

{'='*90}
                        END OF TOP PERFORMERS REPORT
{'='*90}

{'-'*90}
Official Performance Report No: {receipt_number} ({receipt_datetime})
Created by: RN_LAB_TECH
{'-'*90}

"""
        return report
    
    def format_rankings_pdf(self, **kwargs) -> str:
        """Format rankings data for PDF generation"""
        form_level = kwargs.get('form_level', 1)
        term = kwargs.get('term', 'Term 1')
        academic_year = kwargs.get('academic_year', '2024-2025')
        rankings = kwargs.get('rankings', [])
        
        # Get school name from settings
        school_settings = self.db.get_school_settings()
        school_name = school_settings.get('school_name', 'SECONDARY SCHOOL')
        
        report = f"""
{'='*90}
                            REPUBLIC OF MALAWI
                         MINISTRY OF EDUCATION
                      
                         UNITY - WORK - PROGRESS
                        
{'='*90}

                      STUDENT RANKINGS REPORT
                           Form {form_level}

{'='*90}
SCHOOL: {school_name}
FORM LEVEL: {form_level}
ACADEMIC YEAR: {academic_year}
TERM: {term}
REPORT GENERATED: {datetime.now().strftime('%d/%m/%Y %H:%M')}

{'='*90}
FORM {form_level} STUDENT RANKINGS
{'='*90}

{'Position':<8} {'Student Name':<30} {'Average Mark':<12} {'Aggregate Points':<16} {'Subjects Passed':<15} {'Status':<8}
{'-'*90}
"""
        
        for i, student in enumerate(rankings, 1):
            name = student['name'][:29]
            average = f"{student['average']:.1f}%"
            
            # Display aggregate points for all form levels
            if student.get('aggregate_points'):
                aggregate_points = str(student['aggregate_points'])
            else:
                aggregate_points = 'N/A'
            
            subjects_passed = student.get('subjects_passed', 0)
            status = student.get('status', 'N/A')
            
            report += f"{i:<8} {name:<30} {average:<12} {aggregate_points:<16} {subjects_passed:<15} {status:<8}\n"
        
        # Add summary statistics
        total_students = len(rankings)
        passed_students = len([r for r in rankings if r.get('status') == 'PASS'])
        failed_students = total_students - passed_students
        
        if total_students > 0:
            average_mark = sum(r['average'] for r in rankings) / total_students
        else:
            average_mark = 0
        
        # Add footer with official receipt info
        receipt_number = datetime.now().strftime('%Y%m%d%H%M%S')
        receipt_datetime = datetime.now().strftime('%d/%m/%Y at %H:%M:%S')
        
        report += f"""

{'='*90}
RANKING SUMMARY:
{'='*90}

Total Students: {total_students}
Students Passed: {passed_students}
Students Failed: {failed_students}
Class Average: {average_mark:.1f}%

Pass Rate: {(passed_students/total_students*100):.1f}% if total_students > 0 else 0%

Ranking Criteria:
1. Overall Average Percentage (Primary)
2. Number of Subjects Passed (Secondary)
3. Individual Subject Performance

{'='*90}
                        END OF RANKINGS REPORT
{'='*90}

{'-'*90}
Official Rankings Report No: {receipt_number} ({receipt_datetime})
Created by: RN_LAB_TECH
{'-'*90}

"""
        return report
    
    def generate_pdf_report(self, content: str, filename: str) -> str:
        """Generate professional PDF from formatted content"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch, cm
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
            from reportlab.lib.colors import HexColor, black, white, blue, green, red
            from reportlab.lib import colors
            
            # Create PDF document with margins
            doc = SimpleDocTemplate(
                filename, 
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # Custom color scheme
            primary_color = HexColor('#1f4e79')  # Dark blue
            secondary_color = HexColor('#2e75b6')  # Medium blue
            accent_color = HexColor('#70ad47')  # Green
            light_gray = HexColor('#f2f2f2')
            
            # Custom styles
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                spaceAfter=20,
                spaceBefore=10,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold',
                textColor=primary_color
            )
            
            header_style = ParagraphStyle(
                'CustomHeader',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=15,
                spaceBefore=15,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold',
                textColor=secondary_color
            )
            
            subheader_style = ParagraphStyle(
                'CustomSubHeader',
                parent=styles['Heading3'],
                fontSize=14,
                spaceAfter=10,
                spaceBefore=10,
                alignment=TA_LEFT,
                fontName='Helvetica-Bold',
                textColor=primary_color
            )
            
            info_style = ParagraphStyle(
                'InfoStyle',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=8,
                alignment=TA_LEFT,
                fontName='Helvetica',
                textColor=black
            )
            
            # Build PDF content
            story = []
            
            # Parse content to extract structured data
            lines = content.split('\n')
            i = 0
            
            while i < len(lines):
                line = lines[i].strip()
                
                # Skip empty lines
                if not line:
                    i += 1
                    continue
                
                # Header section (REPUBLIC OF MALAWI)
                if 'REPUBLIC OF MALAWI' in line:
                    story.append(Paragraph('REPUBLIC OF MALAWI', title_style))
                    story.append(Paragraph('MINISTRY OF EDUCATION', header_style))
                    story.append(Spacer(1, 10))
                    story.append(Paragraph('UNITY - WORK - PROGRESS', header_style))
                    story.append(Spacer(1, 20))
                    i += 1
                    continue
                
                # Report title
                elif 'TOP PERFORMERS REPORT' in line or 'STUDENT RANKINGS REPORT' in line:
                    story.append(Paragraph(line, title_style))
                    i += 1
                    # Get subtitle if exists
                    if i < len(lines) and lines[i].strip() and not lines[i].strip().startswith('='):
                        story.append(Paragraph(lines[i].strip(), header_style))
                        i += 1
                    story.append(Spacer(1, 20))
                    continue
                
                # School info section
                elif line.startswith('SCHOOL:'):
                    info_data = []
                    while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith('='):
                        if ':' in lines[i]:
                            info_data.append(lines[i].strip())
                        i += 1
                    
                    # Create info table with better column widths
                    if info_data:
                        info_table_data = []
                        for info_line in info_data:
                            if ':' in info_line:
                                key, value = info_line.split(':', 1)
                                info_table_data.append([key.strip() + ':', value.strip()])
                        
                        info_table = Table(info_table_data, colWidths=[3.5*cm, 11.5*cm])
                        info_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (0, -1), light_gray),
                            ('TEXTCOLOR', (0, 0), (0, -1), primary_color),
                            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 0), (-1, -1), 10),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [white, light_gray])
                        ]))
                        story.append(info_table)
                        story.append(Spacer(1, 20))
                    continue
                
                # Data table section
                elif ('Rank' in line and 'Student Name' in line) or ('Position' in line and 'Student Name' in line):
                    # This is a table header - create proper table structure
                    table_data = []
                    
                    # Define headers based on table type
                    if 'Position' in line:
                        # Rankings table
                        headers = ['Position', 'Student Name', 'Average Mark', 'Aggregate Points', 'Subjects Passed', 'Status']
                    else:
                        # Top performers table
                        headers = ['Rank', 'Student Name', 'Average', 'Grade/Points', 'Excellence Area']
                    
                    table_data.append(headers)
                    
                    i += 1
                    # Skip separator line
                    if i < len(lines) and lines[i].strip().startswith('-'):
                        i += 1
                    
                    # Collect table rows
                    while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith('='):
                        row_line = lines[i].strip()
                        if row_line and not row_line.startswith('-'):
                            # Parse row data based on fixed-width columns
                            if 'Position' in headers[0]:
                                # Rankings format: Position(8) Name(30) Average(12) Aggregate(16) Subjects(15) Status(8)
                                position = row_line[:8].strip()
                                name = row_line[8:38].strip()
                                average = row_line[38:50].strip()
                                aggregate = row_line[50:66].strip()
                                subjects = row_line[66:81].strip()
                                status = row_line[81:].strip()
                                row = [position, name, average, aggregate, subjects, status]
                            else:
                                # Top performers format: Rank(6) Name(25) Average(10) Grade(12) Excellence(20)
                                rank = row_line[:6].strip()
                                name = row_line[6:31].strip()
                                average = row_line[31:41].strip()
                                grade = row_line[41:53].strip()
                                excellence = row_line[53:].strip()
                                row = [rank, name, average, grade, excellence]
                            
                            table_data.append(row)
                        i += 1
                    
                    # Create professional table
                    if len(table_data) > 1:
                        # Calculate column widths based on table type
                        if 'Position' in headers[0]:
                            # Rankings table widths
                            col_widths = [2*cm, 5*cm, 2.5*cm, 3*cm, 2.5*cm, 2*cm]
                        else:
                            # Top performers table widths
                            col_widths = [1.5*cm, 5*cm, 2.5*cm, 2.5*cm, 4.5*cm]
                        
                        data_table = Table(table_data, colWidths=col_widths)
                        data_table.setStyle(TableStyle([
                            # Header styling
                            ('BACKGROUND', (0, 0), (-1, 0), primary_color),
                            ('TEXTCOLOR', (0, 0), (-1, 0), white),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 11),
                            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                            
                            # Data rows styling
                            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 1), (-1, -1), 9),
                            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Position/Rank column
                            ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Name column
                            ('ALIGN', (2, 1), (-1, -1), 'CENTER'), # Other columns
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            
                            # Borders and backgrounds
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, light_gray]),
                            
                            # Special formatting for top performers
                            ('BACKGROUND', (0, 1), (-1, 3), HexColor('#fff2cc')),  # Top 3 highlighted
                        ]))
                        
                        story.append(data_table)
                        story.append(Spacer(1, 20))
                    continue
                
                # Summary sections
                elif 'PERFORMANCE ANALYSIS:' in line or 'RANKING SUMMARY:' in line:
                    story.append(Paragraph(line, subheader_style))
                    i += 1
                    
                    # Collect summary content
                    summary_content = []
                    while i < len(lines) and not lines[i].strip().startswith('='):
                        if lines[i].strip():
                            summary_content.append(lines[i].strip())
                        i += 1
                    
                    # Format summary as paragraphs
                    for content_line in summary_content:
                        if content_line:
                            story.append(Paragraph(content_line, info_style))
                    story.append(Spacer(1, 15))
                    continue
                
                # Footer section
                elif 'Official' in line and 'Report No:' in line:
                    # Add some space before footer
                    story.append(Spacer(1, 30))
                    
                    footer_style = ParagraphStyle(
                        'FooterStyle',
                        parent=styles['Normal'],
                        fontSize=9,
                        alignment=TA_CENTER,
                        fontName='Helvetica-Oblique',
                        textColor=colors.grey
                    )
                    
                    story.append(Paragraph(line, footer_style))
                    i += 1
                    if i < len(lines) and 'Created by:' in lines[i]:
                        story.append(Paragraph(lines[i].strip(), footer_style))
                        i += 1
                    continue
                
                else:
                    # Skip separator lines and other content
                    i += 1
            
            # Build PDF
            doc.build(story)
            
            print("Professional PDF report generated: " + filename)
            return filename
            
        except ImportError:
            print("ReportLab not installed. Installing...")
            import subprocess
            subprocess.check_call(['pip', 'install', 'reportlab'])
            return self.generate_pdf_report(content, filename)
        except Exception as e:
            print("Error generating PDF: " + str(e))
            # Fallback to text file
            text_filename = filename.replace('.pdf', '.txt')
            with open(text_filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return text_filename


def main():
    """Demo function showing performance analysis capabilities"""
    print("PERFORMANCE ANALYZER MODULE")
    print("=" * 60)
    print("GENERATES BEST PERFORMING STUDENTS REPORTS:")
    print("   • By Class (Forms 1-4)")
    print("   • By Subject (All 12 subjects)")
    print("   • By Department (Sciences, Humanities, Languages)")
    print("=" * 60)
    
    analyzer = PerformanceAnalyzer("DEMO SECONDARY SCHOOL")
    
    print("\nDEPARTMENT CLASSIFICATIONS:")
    for dept, info in analyzer.departments.items():
        print(f"\n{dept} Department:")
        for subject in info['subjects']:
            print(f"  • {subject}")
    
    print("\n" + "=" * 60)
    print("USAGE EXAMPLES:")
    print("=" * 60)
    
    print("\n1. Best performers by class:")
    print("   analyzer.get_best_performing_students_by_class(form_level=1, term='Term 1')")
    
    print("\n2. Best performers by subject:")
    print("   analyzer.get_best_performing_students_by_subject('Mathematics', term='Term 1')")
    
    print("\n3. Best performers by department:")
    print("   analyzer.get_best_performing_students_by_department('Sciences', term='Term 1')")
    
    print("\n4. Export performance report:")
    print("   analyzer.export_performance_report('class', form_level=1, term='Term 1')")
    
    print("\n5. Comprehensive analysis:")
    print("   analyzer.generate_comprehensive_performance_report(term='Term 1')")
    
    print("\nPerformance analysis system ready!")


if __name__ == "__main__":
    main()
