#!/usr/bin/env python3
"""
Debug the data leakage issue found in school isolation test
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from school_database import SchoolDatabase

def debug_data_leakage():
    """Debug why marks count doesn't add up correctly"""
    
    try:
        db = SchoolDatabase()
        
        print("=== Data Leakage Debug ===\n")
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            print("1. Detailed Marks Analysis by School")
            print("-" * 50)
            
            # Get all schools
            cursor.execute("SELECT school_id, school_name FROM schools ORDER BY school_id")
            schools = cursor.fetchall()
            
            total_marks_by_school = 0
            
            for school_id, school_name in schools:
                # Count marks for this specific school
                cursor.execute("""
                    SELECT COUNT(*) FROM student_marks 
                    WHERE school_id = ? AND form_level = 1
                """, (school_id,))
                school_marks = cursor.fetchone()[0]
                
                print(f"School {school_id} ({school_name}): {school_marks} Form 1 marks")
                total_marks_by_school += school_marks
                
                # Show sample marks for this school
                cursor.execute("""
                    SELECT sm.mark_id, s.first_name, s.last_name, sm.subject, sm.mark
                    FROM student_marks sm
                    JOIN students s ON sm.student_id = s.student_id
                    WHERE sm.school_id = ? AND sm.form_level = 1
                    LIMIT 3
                """, (school_id,))
                sample_marks = cursor.fetchall()
                
                if sample_marks:
                    print(f"  Sample marks:")
                    for mark in sample_marks:
                        print(f"    {mark[1]} {mark[2]} - {mark[3]}: {mark[4]}")
                else:
                    print(f"  No marks found")
                print()
            
            print(f"Total marks by school: {total_marks_by_school}")
            
            # Count total marks in database
            cursor.execute("""
                SELECT COUNT(*) FROM student_marks 
                WHERE form_level = 1
            """)
            total_marks_db = cursor.fetchone()[0]
            
            print(f"Total marks in database: {total_marks_db}")
            print(f"Difference: {total_marks_db - total_marks_by_school}")
            
            print("\n2. Checking for NULL school_id values")
            print("-" * 50)
            
            # Check for marks with NULL school_id
            cursor.execute("""
                SELECT COUNT(*) FROM student_marks 
                WHERE school_id IS NULL AND form_level = 1
            """)
            null_school_marks = cursor.fetchone()[0]
            
            print(f"Marks with NULL school_id: {null_school_marks}")
            
            if null_school_marks > 0:
                print("Sample marks with NULL school_id:")
                cursor.execute("""
                    SELECT sm.mark_id, s.first_name, s.last_name, sm.subject, sm.mark
                    FROM student_marks sm
                    JOIN students s ON sm.student_id = s.student_id
                    WHERE sm.school_id IS NULL AND sm.form_level = 1
                    LIMIT 5
                """)
                null_marks = cursor.fetchall()
                for mark in null_marks:
                    print(f"  {mark[1]} {mark[2]} - {mark[3]}: {mark[4]}")
            
            print("\n3. Checking for Invalid school_id values")
            print("-" * 50)
            
            # Check for marks with invalid school_id (not in schools table)
            cursor.execute("""
                SELECT COUNT(*) FROM student_marks sm
                LEFT JOIN schools s ON sm.school_id = s.school_id
                WHERE sm.form_level = 1 AND s.school_id IS NULL
            """)
            invalid_school_marks = cursor.fetchone()[0]
            
            print(f"Marks with invalid school_id: {invalid_school_marks}")
            
            if invalid_school_marks > 0:
                print("Sample marks with invalid school_id:")
                cursor.execute("""
                    SELECT sm.mark_id, sm.school_id, s.first_name, s.last_name, sm.subject, sm.mark
                    FROM student_marks sm
                    JOIN students s ON sm.student_id = s.student_id
                    LEFT JOIN schools sc ON sm.school_id = sc.school_id
                    WHERE sm.form_level = 1 AND sc.school_id IS NULL
                    LIMIT 5
                """)
                invalid_marks = cursor.fetchall()
                for mark in invalid_marks:
                    print(f"  mark_id: {mark[0]}, school_id: {mark[1]}, {mark[2]} {mark[3]} - {mark[4]}: {mark[5]}")
            
            print("\n4. Checking Student-School Consistency")
            print("-" * 50)
            
            # Check if students and their marks have consistent school_id
            cursor.execute("""
                SELECT COUNT(*) FROM student_marks sm
                JOIN students s ON sm.student_id = s.student_id
                WHERE sm.form_level = 1 AND sm.school_id != s.school_id
            """)
            inconsistent_school_marks = cursor.fetchone()[0]
            
            print(f"Marks with inconsistent school_id (marks.school_id != students.school_id): {inconsistent_school_marks}")
            
            if inconsistent_school_marks > 0:
                print("Sample inconsistent records:")
                cursor.execute("""
                    SELECT sm.mark_id, sm.school_id as marks_school, s.school_id as student_school, 
                           s.first_name, s.last_name, sm.subject, sm.mark
                    FROM student_marks sm
                    JOIN students s ON sm.student_id = s.student_id
                    WHERE sm.form_level = 1 AND sm.school_id != s.school_id
                    LIMIT 5
                """)
                inconsistent = cursor.fetchall()
                for record in inconsistent:
                    print(f"  {record[3]} {record[4]} - marks_school: {record[1]}, student_school: {record[2]}, {record[5]}: {record[6]}")
            
            print("\n5. Fix Recommendations")
            print("-" * 50)
            
            if null_school_marks > 0:
                print("ISSUE: Found marks with NULL school_id")
                print("FIX: Update NULL school_id values to appropriate school values")
            
            if invalid_school_marks > 0:
                print("ISSUE: Found marks with invalid school_id")
                print("FIX: Update invalid school_id values or remove orphaned records")
            
            if inconsistent_school_marks > 0:
                print("ISSUE: Found inconsistent school_id between students and marks")
                print("FIX: Align school_id values between students and marks tables")
            
            if null_school_marks == 0 and invalid_school_marks == 0 and inconsistent_school_marks == 0:
                print("No data leakage issues detected")
                print("The discrepancy might be due to:")
                print("- Cached data in pandas operations")
                print("- Timing issues during data entry")
                print("- Different counting methods")
        
        print("\n=== Debug Complete ===")
        
    except Exception as e:
        print(f"Error during debugging: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_data_leakage()
