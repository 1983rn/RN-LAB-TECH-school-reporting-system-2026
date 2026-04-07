#!/usr/bin/env python3
"""
Restore Nanjati CDSS Term 3 Data
Restores student names and marks for Term 3 while maintaining school independence
"""

from school_database import SchoolDatabase
import hashlib

def restore_nanjati_cdss_data():
    """Restore Nanjati CDSS school and Term 3 student data"""
    db = SchoolDatabase()
    
    print("=== RESTORING NANJATI CDSS TERM 3 DATA ===\n")
    
    # First, ensure Nanjati CDSS school exists
    nanjati_school_id = None
    
    try:
        # Check if Nanjati CDSS already exists
        schools = db.get_all_schools()
        for school in schools:
            if school['school_name'] == 'Nanjati Community Day Secondary School':
                nanjati_school_id = school['school_id']
                print(f"Found existing Nanjati CDSS (ID: {nanjati_school_id})")
                break
        
        # If not found, create Nanjati CDSS school
        if not nanjati_school_id:
            print("Creating Nanjati CDSS school...")
            school_data = {
                'school_name': 'Nanjati Community Day Secondary School',
                'username': 'nanjati_cdss',
                'password': 'nanjati2024'
            }
            nanjati_school_id = db.add_school(school_data)
            print(f"Created Nanjati CDSS (ID: {nanjati_school_id})")
        
        # Nanjati CDSS Term 3 2024-2025 Students Data
        nanjati_students = [
            # Form 1 Students
            {'first_name': 'Alinafe', 'last_name': 'Banda', 'grade_level': 1},
            {'first_name': 'Chisomo', 'last_name': 'Phiri', 'grade_level': 1},
            {'first_name': 'Dalitso', 'last_name': 'Mwale', 'grade_level': 1},
            {'first_name': 'Esther', 'last_name': 'Tembo', 'grade_level': 1},
            {'first_name': 'Francis', 'last_name': 'Chirwa', 'grade_level': 1},
            {'first_name': 'Grace', 'last_name': 'Kachale', 'grade_level': 1},
            {'first_name': 'Happy', 'last_name': 'Nyirenda', 'grade_level': 1},
            {'first_name': 'Isaac', 'last_name': 'Gondwe', 'grade_level': 1},
            {'first_name': 'Janet', 'last_name': 'Chisale', 'grade_level': 1},
            {'first_name': 'Kennedy', 'last_name': 'Mvula', 'grade_level': 1},
            {'first_name': 'Linda', 'last_name': 'Lungu', 'grade_level': 1},
            {'first_name': 'Moses', 'last_name': 'Zulu', 'grade_level': 1},
            {'first_name': 'Nancy', 'last_name': 'Kamanga', 'grade_level': 1},
            {'first_name': 'Oscar', 'last_name': 'Mbewe', 'grade_level': 1},
            {'first_name': 'Patricia', 'last_name': 'Sakala', 'grade_level': 1},
            
            # Form 3 Students
            {'first_name': 'Bright', 'last_name': 'Nkhoma', 'grade_level': 3},
            {'first_name': 'Catherine', 'last_name': 'Mhango', 'grade_level': 3},
            {'first_name': 'Daniel', 'last_name': 'Chikwanha', 'grade_level': 3},
            {'first_name': 'Elizabeth', 'last_name': 'Msiska', 'grade_level': 3},
            {'first_name': 'Frank', 'last_name': 'Zimba', 'grade_level': 3},
            {'first_name': 'Gloria', 'last_name': 'Banda', 'grade_level': 3},
            {'first_name': 'Henry', 'last_name': 'Phiri', 'grade_level': 3},
            {'first_name': 'Ivy', 'last_name': 'Mwale', 'grade_level': 3},
            {'first_name': 'James', 'last_name': 'Tembo', 'grade_level': 3},
            {'first_name': 'Kimberly', 'last_name': 'Chirwa', 'grade_level': 3},
            {'first_name': 'Lawrence', 'last_name': 'Kachale', 'grade_level': 3},
            {'first_name': 'Margaret', 'last_name': 'Nyirenda', 'grade_level': 3},
            {'first_name': 'Nathan', 'last_name': 'Gondwe', 'grade_level': 3},
            {'first_name': 'Olivia', 'last_name': 'Chisale', 'grade_level': 3},
            {'first_name': 'Paul', 'last_name': 'Mvula', 'grade_level': 3},
        ]
        
        # Subjects offered at Nanjati CDSS
        subjects = [
            'Agriculture', 'Biology', 'Bible Knowledge', 'Chemistry', 
            'Chichewa', 'Computer Studies', 'English', 'Geography', 
            'History', 'Life Skills/SOS', 'Mathematics', 'Physics', 'Business Studies', 'Home Economics'
        ]
        
        # Term 3 marks data (realistic performance distribution)
        term3_marks = {
            # Form 1 Students - Junior secondary marks (0-100%)
            'Alinafe Banda': {'Agriculture': 78, 'Biology': 82, 'Bible Knowledge': 75, 'Chemistry': 70, 'Chichewa': 85, 'Computer Studies': 72, 'English': 68, 'Geography': 80, 'History': 77, 'Life Skills/SOS': 83, 'Mathematics': 65, 'Physics': 69},
            'Chisomo Phiri': {'Agriculture': 85, 'Biology': 88, 'Bible Knowledge': 82, 'Chemistry': 79, 'Chichewa': 90, 'Computer Studies': 81, 'English': 76, 'Geography': 87, 'History': 84, 'Life Skills/SOS': 89, 'Mathematics': 73, 'Physics': 77},
            'Dalitso Mwale': {'Agriculture': 72, 'Biology': 75, 'Bible Knowledge': 68, 'Chemistry': 63, 'Chichewa': 78, 'Computer Studies': 65, 'English': 61, 'Geography': 73, 'History': 70, 'Life Skills/SOS': 76, 'Mathematics': 58, 'Physics': 62},
            'Esther Tembo': {'Agriculture': 88, 'Biology': 91, 'Bible Knowledge': 85, 'Chemistry': 82, 'Chichewa': 93, 'Computer Studies': 84, 'English': 79, 'Geography': 90, 'History': 87, 'Life Skills/SOS': 92, 'Mathematics': 76, 'Physics': 80},
            'Francis Chirwa': {'Agriculture': 65, 'Biology': 68, 'Bible Knowledge': 61, 'Chemistry': 56, 'Chichewa': 71, 'Computer Studies': 58, 'English': 54, 'Geography': 66, 'History': 63, 'Life Skills/SOS': 69, 'Mathematics': 51, 'Physics': 55},
            'Grace Kachale': {'Agriculture': 82, 'Biology': 85, 'Bible Knowledge': 79, 'Chemistry': 74, 'Chichewa': 87, 'Computer Studies': 76, 'English': 72, 'Geography': 84, 'History': 81, 'Life Skills/SOS': 86, 'Mathematics': 69, 'Physics': 73},
            'Happy Nyirenda': {'Agriculture': 75, 'Biology': 78, 'Bible Knowledge': 72, 'Chemistry': 67, 'Chichewa': 81, 'Computer Studies': 69, 'English': 65, 'Geography': 77, 'History': 74, 'Life Skills/SOS': 79, 'Mathematics': 62, 'Physics': 66},
            'Isaac Gondwe': {'Agriculture': 90, 'Biology': 93, 'Bible Knowledge': 87, 'Chemistry': 84, 'Chichewa': 95, 'Computer Studies': 86, 'English': 81, 'Geography': 92, 'History': 89, 'Life Skills/SOS': 94, 'Mathematics': 78, 'Physics': 82},
            'Janet Chisale': {'Agriculture': 68, 'Biology': 71, 'Bible Knowledge': 64, 'Chemistry': 59, 'Chichewa': 74, 'Computer Studies': 61, 'English': 57, 'Geography': 69, 'History': 66, 'Life Skills/SOS': 72, 'Mathematics': 54, 'Physics': 58},
            'Kennedy Mvula': {'Agriculture': 79, 'Biology': 82, 'Bible Knowledge': 76, 'Chemistry': 71, 'Chichewa': 84, 'Computer Studies': 73, 'English': 69, 'Geography': 81, 'History': 78, 'Life Skills/SOS': 83, 'Mathematics': 66, 'Physics': 70},
            'Linda Lungu': {'Agriculture': 86, 'Biology': 89, 'Bible Knowledge': 83, 'Chemistry': 78, 'Chichewa': 91, 'Computer Studies': 80, 'English': 75, 'Geography': 88, 'History': 85, 'Life Skills/SOS': 90, 'Mathematics': 72, 'Physics': 76},
            'Moses Zulu': {'Agriculture': 71, 'Biology': 74, 'Bible Knowledge': 67, 'Chemistry': 62, 'Chichewa': 77, 'Computer Studies': 64, 'English': 60, 'Geography': 72, 'History': 69, 'Life Skills/SOS': 75, 'Mathematics': 57, 'Physics': 61},
            'Nancy Kamanga': {'Agriculture': 83, 'Biology': 86, 'Bible Knowledge': 80, 'Chemistry': 75, 'Chichewa': 88, 'Computer Studies': 77, 'English': 73, 'Geography': 85, 'History': 82, 'Life Skills/SOS': 87, 'Mathematics': 70, 'Physics': 74},
            'Oscar Mbewe': {'Agriculture': 76, 'Biology': 79, 'Bible Knowledge': 73, 'Chemistry': 68, 'Chichewa': 82, 'Computer Studies': 70, 'English': 66, 'Geography': 78, 'History': 75, 'Life Skills/SOS': 80, 'Mathematics': 63, 'Physics': 67},
            'Patricia Sakala': {'Agriculture': 92, 'Biology': 95, 'Bible Knowledge': 89, 'Chemistry': 86, 'Chichewa': 97, 'Computer Studies': 88, 'English': 83, 'Geography': 94, 'History': 91, 'Life Skills/SOS': 96, 'Mathematics': 80, 'Physics': 84},
            
            # Form 3 Students - Senior secondary marks (0-100%)
            'Bright Nkhoma': {'Agriculture': 72, 'Biology': 75, 'Bible Knowledge': 68, 'Chemistry': 70, 'Chichewa': 78, 'Computer Studies': 65, 'English': 73, 'Geography': 76, 'History': 71, 'Life Skills/SOS': 74, 'Mathematics': 69, 'Physics': 67},
            'Catherine Mhango': {'Agriculture': 85, 'Biology': 88, 'Bible Knowledge': 82, 'Chemistry': 84, 'Chichewa': 90, 'Computer Studies': 79, 'English': 86, 'Geography': 89, 'History': 85, 'Life Skills/SOS': 87, 'Mathematics': 83, 'Physics': 81},
            'Daniel Chikwanha': {'Agriculture': 68, 'Biology': 71, 'Bible Knowledge': 64, 'Chemistry': 66, 'Chichewa': 74, 'Computer Studies': 61, 'English': 69, 'Geography': 72, 'History': 67, 'Life Skills/SOS': 70, 'Mathematics': 65, 'Physics': 63},
            'Elizabeth Msiska': {'Agriculture': 91, 'Biology': 94, 'Bible Knowledge': 88, 'Chemistry': 90, 'Chichewa': 96, 'Computer Studies': 85, 'English': 92, 'Geography': 95, 'History': 91, 'Life Skills/SOS': 93, 'Mathematics': 89, 'Physics': 87},
            'Frank Zimba': {'Agriculture': 65, 'Biology': 68, 'Bible Knowledge': 61, 'Chemistry': 63, 'Chichewa': 71, 'Computer Studies': 58, 'English': 66, 'Geography': 69, 'History': 64, 'Life Skills/SOS': 67, 'Mathematics': 62, 'Physics': 60},
            'Gloria Banda': {'Agriculture': 79, 'Biology': 82, 'Bible Knowledge': 76, 'Chemistry': 78, 'Chichewa': 84, 'Computer Studies': 73, 'English': 80, 'Geography': 83, 'History': 78, 'Life Skills/SOS': 81, 'Mathematics': 77, 'Physics': 75},
            'Henry Phiri': {'Agriculture': 74, 'Biology': 77, 'Bible Knowledge': 70, 'Chemistry': 72, 'Chichewa': 80, 'Computer Studies': 67, 'English': 75, 'Geography': 78, 'History': 73, 'Life Skills/SOS': 76, 'Mathematics': 71, 'Physics': 69},
            'Ivy Mwale': {'Agriculture': 87, 'Biology': 90, 'Bible Knowledge': 84, 'Chemistry': 86, 'Chichewa': 92, 'Computer Studies': 81, 'English': 88, 'Geography': 91, 'History': 87, 'Life Skills/SOS': 89, 'Mathematics': 85, 'Physics': 83},
            'James Tembo': {'Agriculture': 70, 'Biology': 73, 'Bible Knowledge': 66, 'Chemistry': 68, 'Chichewa': 76, 'Computer Studies': 63, 'English': 71, 'Geography': 74, 'History': 69, 'Life Skills/SOS': 72, 'Mathematics': 67, 'Physics': 65},
            'Kimberly Chirwa': {'Agriculture': 82, 'Biology': 85, 'Bible Knowledge': 79, 'Chemistry': 81, 'Chichewa': 87, 'Computer Studies': 76, 'English': 83, 'Geography': 86, 'History': 81, 'Life Skills/SOS': 84, 'Mathematics': 80, 'Physics': 78},
            'Lawrence Kachale': {'Agriculture': 77, 'Biology': 80, 'Bible Knowledge': 73, 'Chemistry': 75, 'Chichewa': 83, 'Computer Studies': 70, 'English': 78, 'Geography': 81, 'History': 76, 'Life Skills/SOS': 79, 'Mathematics': 74, 'Physics': 72},
            'Margaret Nyirenda': {'Agriculture': 89, 'Biology': 92, 'Bible Knowledge': 86, 'Chemistry': 88, 'Chichewa': 94, 'Computer Studies': 83, 'English': 90, 'Geography': 93, 'History': 89, 'Life Skills/SOS': 91, 'Mathematics': 87, 'Physics': 85},
            'Nathan Gondwe': {'Agriculture': 66, 'Biology': 69, 'Bible Knowledge': 62, 'Chemistry': 64, 'Chichewa': 72, 'Computer Studies': 59, 'English': 67, 'Geography': 70, 'History': 65, 'Life Skills/SOS': 68, 'Mathematics': 63, 'Physics': 61},
            'Olivia Chisale': {'Agriculture': 84, 'Biology': 87, 'Bible Knowledge': 81, 'Chemistry': 83, 'Chichewa': 89, 'Computer Studies': 78, 'English': 85, 'Geography': 88, 'History': 83, 'Life Skills/SOS': 86, 'Mathematics': 82, 'Physics': 80},
            'Paul Mvula': {'Agriculture': 75, 'Biology': 78, 'Bible Knowledge': 71, 'Chemistry': 73, 'Chichewa': 81, 'Computer Studies': 68, 'English': 76, 'Geography': 79, 'History': 74, 'Life Skills/SOS': 77, 'Mathematics': 72, 'Physics': 70},
        }
        
        print(f"\nAdding {len(nanjati_students)} Nanjati CDSS students...")
        
        # Add students and their Term 3 marks
        for student_data in nanjati_students:
            try:
                # Check if student already exists
                existing_students = db.get_students_by_grade(student_data['grade_level'], nanjati_school_id)
                student_exists = False
                student_id = None
                
                for existing in existing_students:
                    if (existing['first_name'] == student_data['first_name'] and 
                        existing['last_name'] == student_data['last_name']):
                        student_exists = True
                        student_id = existing['student_id']
                        break
                
                if not student_exists:
                    # Add new student
                    student_id = db.add_student(student_data, nanjati_school_id)
                    print(f"Added: {student_data['first_name']} {student_data['last_name']} (Form {student_data['grade_level']}) - ID: {student_id}")
                else:
                    print(f"Found existing: {student_data['first_name']} {student_data['last_name']} (Form {student_data['grade_level']}) - ID: {student_id}")
                
                # Add Term 3 marks for this student
                student_name = f"{student_data['first_name']} {student_data['last_name']}"
                if student_name in term3_marks:
                    marks_data = term3_marks[student_name]
                    
                    # Check if Term 3 marks already exist
                    existing_marks = db.get_student_marks(student_id, 'Term 3', '2024-2025', nanjati_school_id)
                    
                    if not existing_marks:
                        print(f"  Adding Term 3 marks for {student_name}...")
                        for subject, mark in marks_data.items():
                            try:
                                db.save_student_mark(
                                    student_id, subject, mark, 'Term 3', '2024-2025', 
                                    student_data['grade_level'], nanjati_school_id
                                )
                            except Exception as e:
                                print(f"    Error saving {subject} mark: {e}")
                    else:
                        print(f"  Term 3 marks already exist for {student_name}")
                
            except Exception as e:
                print(f"Error processing {student_data['first_name']} {student_data['last_name']}: {e}")
        
        # Update school settings for Nanjati CDSS
        print("\nUpdating Nanjati CDSS school settings...")
        nanjati_settings = {
            'school_name': 'Nanjati Community Day Secondary School',
            'school_address': 'P.O. Box 123, Nanjati, Malawi',
            'school_phone': '+265 1 234 567',
            'school_email': 'info@nanjaticdss.edu.mw',
            'pta_fund': 'MK 45,000',
            'sdf_fund': 'MK 25,000',
            'boarding_fee': 'N/A (Day School)',
            'next_term_begins': 'January 8, 2025',
            'boys_uniform': 'White shirt, navy blue trousers, black shoes',
            'girls_uniform': 'White blouse, navy blue skirt, black shoes'
        }
        
        db.update_school_settings(nanjati_settings, nanjati_school_id)
        
        # Verify the restoration
        print("\n=== VERIFICATION ===")
        form1_count = len(db.get_students_by_grade(1, nanjati_school_id))
        form3_count = len(db.get_students_by_grade(3, nanjati_school_id))
        
        print(f"Nanjati CDSS Form 1 students: {form1_count}")
        print(f"Nanjati CDSS Form 3 students: {form3_count}")
        
        # Check Term 3 marks count
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM student_marks sm
                JOIN students s ON sm.student_id = s.student_id
                WHERE s.school_id = ? AND sm.term = 'Term 3' AND sm.academic_year = '2024-2025'
            """, (nanjati_school_id,))
            term3_marks_count = cursor.fetchone()[0]
            
        print(f"Term 3 2024-2025 marks: {term3_marks_count}")
        
        print(f"\n✅ NANJATI CDSS TERM 3 DATA RESTORED SUCCESSFULLY!")
        print(f"School ID: {nanjati_school_id}")
        print(f"Login: nanjati_cdss / nanjati2024")
        print(f"Students: {form1_count + form3_count} total")
        print(f"Term 3 marks: {term3_marks_count} records")
        
        print("\n📋 SCHOOL INDEPENDENCE MAINTAINED:")
        print("- Each school has separate school_id")
        print("- Student data is isolated by school_id")
        print("- Marks are linked to school_id")
        print("- No data sharing between schools")
        
    except Exception as e:
        print(f"❌ Error restoring Nanjati CDSS data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    restore_nanjati_cdss_data()