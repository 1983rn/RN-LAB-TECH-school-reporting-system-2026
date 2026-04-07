#!/usr/bin/env python3
"""
Setup Sample Data - Malawi School Reporting System
Creates sample students for testing the data entry system

Created by: RN_LAB_TECH
"""

from school_database import SchoolDatabase

def setup_sample_students():
    """Add sample students to the database"""
    db = SchoolDatabase()
    
    # Sample students for each form
    sample_students = [
        # Form 1 students
        {'student_number': 'F1001', 'first_name': 'John', 'last_name': 'Banda', 'grade_level': 1},
        {'student_number': 'F1002', 'first_name': 'Mary', 'last_name': 'Phiri', 'grade_level': 1},
        {'student_number': 'F1003', 'first_name': 'Peter', 'last_name': 'Mwale', 'grade_level': 1},
        {'student_number': 'F1004', 'first_name': 'Grace', 'last_name': 'Tembo', 'grade_level': 1},
        {'student_number': 'F1005', 'first_name': 'James', 'last_name': 'Chirwa', 'grade_level': 1},
        
        # Form 2 students
        {'student_number': 'F2001', 'first_name': 'Sarah', 'last_name': 'Kachale', 'grade_level': 2},
        {'student_number': 'F2002', 'first_name': 'David', 'last_name': 'Nyirenda', 'grade_level': 2},
        {'student_number': 'F2003', 'first_name': 'Ruth', 'last_name': 'Gondwe', 'grade_level': 2},
        {'student_number': 'F2004', 'first_name': 'Moses', 'last_name': 'Chisale', 'grade_level': 2},
        {'student_number': 'F2005', 'first_name': 'Esther', 'last_name': 'Mvula', 'grade_level': 2},
        
        # Form 3 students
        {'student_number': 'F3001', 'first_name': 'Michael', 'last_name': 'Lungu', 'grade_level': 3},
        {'student_number': 'F3002', 'first_name': 'Patricia', 'last_name': 'Zulu', 'grade_level': 3},
        {'student_number': 'F3003', 'first_name': 'Francis', 'last_name': 'Kamanga', 'grade_level': 3},
        {'student_number': 'F3004', 'first_name': 'Joyce', 'last_name': 'Mbewe', 'grade_level': 3},
        {'student_number': 'F3005', 'first_name': 'Emmanuel', 'last_name': 'Sakala', 'grade_level': 3},
        
        # Form 4 students
        {'student_number': 'F4001', 'first_name': 'Catherine', 'last_name': 'Nkhoma', 'grade_level': 4},
        {'student_number': 'F4002', 'first_name': 'Joseph', 'last_name': 'Mhango', 'grade_level': 4},
        {'student_number': 'F4003', 'first_name': 'Elizabeth', 'last_name': 'Chikwanha', 'grade_level': 4},
        {'student_number': 'F4004', 'first_name': 'Daniel', 'last_name': 'Msiska', 'grade_level': 4},
        {'student_number': 'F4005', 'first_name': 'Agnes', 'last_name': 'Zimba', 'grade_level': 4},
    ]
    
    print("Setting up sample students...")
    
    for student_data in sample_students:
        try:
            student_id = db.add_student(student_data)
            print(f"Added: {student_data['first_name']} {student_data['last_name']} (Form {student_data['grade_level']}) - ID: {student_id}")
        except Exception as e:
            print(f"Error adding {student_data['first_name']} {student_data['last_name']}: {e}")
    
    print(f"\nSample data setup complete! Added {len(sample_students)} students.")
    print("You can now test the data entry forms.")

if __name__ == "__main__":
    setup_sample_students()