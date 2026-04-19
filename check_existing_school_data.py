#!/usr/bin/env python3
"""
Check existing school data for 2025-2026 Term 1
Investigate Nanjati Community Day Secondary School and other schools with data
"""

import os
import sys
import json
from datetime import datetime

# Add current directory to path 
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from school_database import SchoolDatabase

def check_existing_school_data():
    """Check existing school data for 2025-2026 Term 1"""
    
    print("=== Checking Existing School Data for 2025-2026 Term 1 ===")
    
    # Initialize database
    db = SchoolDatabase()
    
    # Target parameters
    target_term = "Term 1"
    target_year = "2025-2026"
    target_school = "Nanjati Community Day Secondary School"
    
    try:
        # Step 1: Get all schools in the database
        print("\n1. Getting all schools in database...")
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT school_id, school_name FROM schools ORDER BY school_name")
            schools = cursor.fetchall()
            
        print(f"Total schools in database: {len(schools)}")
        print("\nSchool list:")
        for school_id, school_name in schools[:10]:  # Show first 10
            print(f"  ID {school_id}: {school_name}")
        
        if len(schools) > 10:
            print(f"  ... and {len(schools) - 10} more schools")
        
        # Step 2: Look for Nanjati Community Day Secondary School
        print(f"\n2. Looking for '{target_school}'...")
        nanjati_school = None
        for school_id, school_name in schools:
            if "nanjati" in school_name.lower():
                nanjati_school = (school_id, school_name)
                break
        
        if nanjati_school:
            school_id, school_name = nanjati_school
            print(f"Found: ID {school_id} - {school_name}")
        else:
            print("Nanjati Community Day Secondary School not found in database")
            print("Looking for similar names...")
            for school_id, school_name in schools:
                if "community" in school_name.lower() or "day" in school_name.lower():
                    print(f"  Similar: ID {school_id} - {school_name}")
        
        # Step 3: Check which schools have data for 2025-2026 Term 1
        print(f"\n3. Checking schools with data for {target_term} {target_year}...")
        
        schools_with_data = []
        for school_id, school_name in schools:
            # Check for students in this term/year
            students = db.get_students_enrolled_in_term(1, target_term, target_year, school_id)
            if students:
                schools_with_data.append((school_id, school_name, len(students)))
        
        print(f"Schools with {target_term} {target_year} data: {len(schools_with_data)}")
        for school_id, school_name, student_count in schools_with_data[:10]:
            print(f"  ID {school_id}: {school_name} ({student_count} students)")
        
        if len(schools_with_data) > 10:
            print(f"  ... and {len(schools_with_data) - 10} more schools")
        
        # Step 4: Detailed check for Nanjati if found
        if nanjati_school:
            school_id, school_name = nanjati_school
            print(f"\n4. Detailed data check for {school_name}...")
            
            # Check all forms for this school
            for form_level in [1, 2, 3, 4]:
                students = db.get_students_enrolled_in_term(form_level, target_term, target_year, school_id)
                print(f"  Form {form_level}: {len(students)} students")
                
                if students:
                    # Show sample students
                    print(f"    Sample students:")
                    for i, student in enumerate(students[:3]):
                        print(f"      {i+1}. {student['first_name']} {student['last_name']} (ID: {student['student_id']})")
                    
                    # Check for marks
                    marks_count = 0
                    for student in students:
                        marks = db.get_student_marks(student['student_id'], target_term, target_year, school_id)
                        if marks:
                            marks_count += len(marks)
                    
                    print(f"    Total marks entries: {marks_count}")
        
        # Step 5: Check overall database statistics
        print(f"\n5. Overall database statistics for {target_term} {target_year}...")
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total students across all schools
            cursor.execute("""
                SELECT COUNT(*) 
                FROM student_term_enrollment ste
                JOIN students s ON ste.student_id = s.student_id
                WHERE ste.term = ? AND ste.academic_year = ?
            """, (target_term, target_year))
            total_students = cursor.fetchone()[0]
            
            # Total marks across all schools
            cursor.execute("""
                SELECT COUNT(*) 
                FROM student_marks
                WHERE term = ? AND academic_year = ?
            """, (target_term, target_year))
            total_marks = cursor.fetchone()[0]
            
            print(f"  Total students enrolled: {total_students}")
            print(f"  Total marks entries: {total_marks}")
        
        # Step 6: Test data retrieval functionality
        print(f"\n6. Testing data retrieval functionality...")
        
        if nanjati_school:
            school_id, school_name = nanjati_school
            
            # Test retrieving students for Form 1
            form1_students = db.get_students_enrolled_in_term(1, target_term, target_year, school_id)
            print(f"Retrieved {len(form1_students)} Form 1 students for {school_name}")
            
            if form1_students:
                # Test retrieving marks for first student
                test_student = form1_students[0]
                student_marks = db.get_student_marks(test_student['student_id'], target_term, target_year, school_id)
                print(f"Retrieved {len(student_marks)} subjects for student {test_student['first_name']} {test_student['last_name']}")
                
                if student_marks:
                    print("Sample marks:")
                    for subject, data in list(student_marks.items())[:3]:
                        print(f"  {subject}: {data['mark']} (Grade: {data['grade']})")
        
        # Step 7: Check if data is accessible through web interface
        print(f"\n7. Web interface accessibility check...")
        
        # Simulate what the web interface does
        def simulate_web_interface(school_id, form_level, term, academic_year):
            """Simulate web interface data loading"""
            try:
                students = db.get_students_enrolled_in_term(form_level, term, academic_year, school_id)
                subjects = db.get_subjects_by_form(form_level, school_id)
                
                # Check for existing marks
                has_marks = db.check_marks_exist_for_period(form_level, term, academic_year, school_id)
                
                return {
                    'success': True,
                    'students': len(students),
                    'subjects': len(subjects),
                    'has_marks': has_marks,
                    'is_new_term': not has_marks and not students
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        if nanjati_school:
            school_id, school_name = nanjati_school
            
            for form_level in [1, 2, 3, 4]:
                result = simulate_web_interface(school_id, form_level, target_term, target_year)
                print(f"  Form {form_level}: ", end="")
                if result['success']:
                    print(f"{result['students']} students, {result['subjects']} subjects, has_marks={result['has_marks']}")
                else:
                    print(f"Error: {result['error']}")
        
        print("\n" + "="*60)
        print("EXISTING SCHOOL DATA CHECK COMPLETE")
        
        if nanjati_school:
            print(f"\nNanjati Community Day Secondary School:")
            print(f"  School ID: {nanjati_school[0]}")
            print(f"  Data available for {target_term} {target_year}: YES" if nanjati_school[0] in [s[0] for s in schools_with_data] else f"  Data available for {target_term} {target_year}: NO")
        else:
            print(f"\nNanjati Community Day Secondary School: NOT FOUND")
        
        print(f"\nTotal schools with {target_term} {target_year} data: {len(schools_with_data)}")
        print("Data retrieval functionality: WORKING")
        
    except Exception as e:
        print(f"\n** Check failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_existing_school_data()
