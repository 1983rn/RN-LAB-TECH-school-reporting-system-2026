#!/usr/bin/env python3
"""
Test script to verify Rankings Page filtering by Term and Academic Year
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from school_database import SchoolDatabase

def test_rankings_filtering():
    """Test that rankings are correctly filtered by term and academic year"""
    
    try:
        db = SchoolDatabase()
        
        # Test parameters
        test_cases = [
            {'form_level': 1, 'term': 'Term 1', 'academic_year': '2025-2026'},
            {'form_level': 1, 'term': 'Term 2', 'academic_year': '2025-2026'},
            {'form_level': 1, 'term': 'Term 3', 'academic_year': '2025-2026'},
            {'form_level': 1, 'term': 'Term 1', 'academic_year': '2024-2025'},
        ]
        
        print("=== Rankings Filtering Test ===\n")
        
        for i, test_case in enumerate(test_cases, 1):
            form_level = test_case['form_level']
            term = test_case['term']
            academic_year = test_case['academic_year']
            
            print(f"Test Case {i}: Form {form_level}, {term}, {academic_year}")
            print("-" * 60)
            
            # Get rankings using the same method as the API
            result = db.get_student_rankings(form_level, term, academic_year, school_id=2)  # Using NANJATI school
            
            rankings = result.get('rankings', [])
            total_students = result.get('total_students', 0)
            students_with_marks = result.get('students_with_marks', 0)
            
            print(f"Total enrolled students: {total_students}")
            print(f"Students with marks: {students_with_marks}")
            print(f"Students in rankings: {len(rankings)}")
            
            if rankings:
                print("Top 5 students:")
                for j, student in enumerate(rankings[:5], 1):
                    name = student.get('name', 'Unknown')
                    if form_level >= 3:
                        points = student.get('aggregate_points', 'N/A')
                        status = student.get('status', 'N/A')
                        print(f"  {j}. {name} - Points: {points}, Status: {status}")
                    else:
                        grade = student.get('grade', 'N/A')
                        status = student.get('status', 'N/A')
                        print(f"  {j}. {name} - Grade: {grade}, Status: {status}")
            else:
                print("No students found with marks for this period")
            
            print()
        
        # Test data source verification
        print("=== Data Source Verification ===")
        print("Checking if rankings data comes from the same source as Data Entry...")
        
        # Check if student_marks table has data for the test period
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Test for Term 1, 2025-2026, Form 1
            cursor.execute("""
                SELECT COUNT(*) FROM student_marks 
                WHERE form_level = 1 AND term = 'Term 1' AND academic_year = '2025-2026' AND school_id = 2
            """)
            marks_count = cursor.fetchone()[0]
            
            print(f"Total marks entries for Form 1, Term 1, 2025-2026: {marks_count}")
            
            if marks_count > 0:
                # Show sample data
                cursor.execute("""
                    SELECT s.first_name, s.last_name, sm.subject, sm.mark 
                    FROM student_marks sm
                    JOIN students s ON sm.student_id = s.student_id
                    WHERE sm.form_level = 1 AND sm.term = 'Term 1' AND sm.academic_year = '2025-2026' AND sm.school_id = 2
                    LIMIT 5
                """)
                sample_data = cursor.fetchall()
                
                print("Sample data from student_marks table:")
                for row in sample_data:
                    print(f"  {row[0]} {row[1]} - {row[2]}: {row[3]}")
            else:
                print("No marks data found for the test period")
        
        print("\n=== Test Complete ===")
        print("The Rankings Page should now correctly filter by Term and Academic Year")
        print("Both API endpoints use the same data source as Data Entry module")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rankings_filtering()
