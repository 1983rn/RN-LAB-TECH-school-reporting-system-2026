#!/usr/bin/env python3
"""
Check what data periods actually exist in the database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from school_database import SchoolDatabase

def check_existing_data_periods():
    """Check what periods have actual data in the database"""
    
    try:
        db = SchoolDatabase()
        
        print("=== Checking Existing Data Periods ===\n")
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check what terms and academic years have data
            cursor.execute("""
                SELECT DISTINCT term, academic_year, form_level, COUNT(*) as mark_count
                FROM student_marks
                GROUP BY term, academic_year, form_level
                ORDER BY academic_year, term, form_level
            """)
            
            periods = cursor.fetchall()
            
            if periods:
                print("Existing data periods:")
                for term, academic_year, form_level, count in periods:
                    print(f"  Form {form_level}, {term}, {academic_year}: {count} marks")
            else:
                print("No marks data found in student_marks table")
            
            # Check if there's any data in alternative tables (PostgreSQL version)
            cursor.execute("SELECT tablename FROM pg_tables WHERE tablename LIKE '%mark%'")
            mark_tables = cursor.fetchall()
            
            print(f"\nTables containing 'mark': {[table[0] for table in mark_tables]}")
            
            if mark_tables:
                for table in mark_tables:
                    table_name = table[0]
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"  {table_name}: {count} records")
                    
                    if count > 0:
                        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                        sample = cursor.fetchall()
                        print(f"    Sample data: {sample}")
        
        print("\n=== Testing with Existing Data ===")
        
        # If we found any periods, test rankings with them
        if periods:
            for term, academic_year, form_level, count in periods[:2]:  # Test first 2 periods
                print(f"\nTesting rankings for Form {form_level}, {term}, {academic_year}")
                print("-" * 60)
                
                result = db.get_student_rankings(form_level, term, academic_year, school_id=2)
                
                rankings = result.get('rankings', [])
                total_students = result.get('total_students', 0)
                students_with_marks = result.get('students_with_marks', 0)
                
                print(f"Total enrolled students: {total_students}")
                print(f"Students with marks: {students_with_marks}")
                print(f"Students in rankings: {len(rankings)}")
                
                if rankings:
                    print("Top 3 students:")
                    for j, student in enumerate(rankings[:3], 1):
                        name = student.get('name', 'Unknown')
                        if form_level >= 3:
                            points = student.get('aggregate_points', 'N/A')
                            status = student.get('status', 'N/A')
                            print(f"  {j}. {name} - Points: {points}, Status: {status}")
                        else:
                            grade = student.get('grade', 'N/A')
                            status = student.get('status', 'N/A')
                            print(f"  {j}. {name} - Grade: {grade}, Status: {status}")
        
    except Exception as e:
        print(f"Error checking data periods: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_existing_data_periods()
