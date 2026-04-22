#!/usr/bin/env python3
"""
Simple test to debug the get_top_performers SQL issue
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from school_database import SchoolDatabase

def test_simple_top_performers():
    """Simple test to debug the SQL parameter binding issue"""
    
    try:
        db = SchoolDatabase()
        
        print("=== Simple Top Performers Test ===\n")
        
        # Test parameters
        test_school_id = 1
        test_form_level = 1
        test_term = 'Term 1'
        test_academic_year = '2025-2026'
        
        print(f"Testing with: School {test_school_id}, Form {test_form_level}, {test_term}, {test_academic_year}")
        
        # Test with a simple category first
        print("\n1. Testing Languages category (simplest):")
        print("-" * 50)
        
        try:
            performers = db.get_top_performers(test_form_level, 'languages', test_term, test_academic_year, test_school_id)
            print(f"SUCCESS: Found {len(performers)} performers")
            
            if performers:
                for i, performer in enumerate(performers[:3]):
                    print(f"  {i+1}. {performer.get('name', 'Unknown')} - Total: {performer.get('total_marks', 0)}")
            
        except Exception as e:
            print(f"ERROR: {e}")
            
            # Let's debug the SQL query step by step
            print("\nDebugging SQL query...")
            
            # Test the subject groups directly
            subject_groups = {
                'sciences': ['Agriculture', 'Biology', 'Chemistry', 'Computer Studies', 'Mathematics', 'Physics', 'Business Studies', 'Home Economics', 'Clothing & Textiles', 'Technical Drawing'],
                'humanities': ['Bible Knowledge', 'Geography', 'History', 'Life Skills/SOS'],
                'languages': ['English', 'Chichewa']
            }
            
            category = 'languages'
            subjects = subject_groups[category]
            placeholders = ','.join(['?' for _ in subjects])
            
            print(f"Category: {category}")
            print(f"Subjects: {subjects}")
            print(f"Placeholders: {placeholders}")
            
            # Test the SQL query manually
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                sql_query = f"""
                    SELECT s.student_id, s.first_name, s.last_name, 
                           SUM(sm.mark) as department_total,
                           COUNT(DISTINCT sm.subject) as subjects_taken
                    FROM students s
                    JOIN student_marks sm ON s.student_id = sm.student_id
                    WHERE sm.form_level = ? AND sm.term = ? AND sm.academic_year = ? AND s.school_id = ?
                    AND sm.subject IN ({placeholders})
                    GROUP BY s.student_id, s.first_name, s.last_name
                    HAVING subjects_taken >= 1
                    ORDER BY department_total DESC
                    LIMIT 10
                """
                
                params = (test_form_level, test_term, test_academic_year, test_school_id, *subjects)
                
                print(f"SQL Query: {sql_query}")
                print(f"Parameters: {params}")
                print(f"Number of parameters: {len(params)}")
                
                try:
                    cursor.execute(sql_query, params)
                    rows = cursor.fetchall()
                    print(f"SUCCESS: Found {len(rows)} rows")
                    
                    for row in rows[:3]:
                        student_id, first_name, last_name, department_total, subjects_taken = row
                        print(f"  {first_name} {last_name}: {department_total} marks from {subjects_taken} subjects")
                        
                except Exception as sql_error:
                    print(f"SQL Error: {sql_error}")
                    
                    # Try with fewer parameters to isolate the issue
                    print("\nTesting with minimal parameters...")
                    try:
                        simple_query = """
                            SELECT COUNT(*) FROM student_marks
                            WHERE form_level = ? AND term = ? AND academic_year = ? AND school_id = ?
                        """
                        simple_params = (test_form_level, test_term, test_academic_year, test_school_id)
                        cursor.execute(simple_query, simple_params)
                        count = cursor.fetchone()[0]
                        print(f"Simple query SUCCESS: {count} marks found")
                        
                    except Exception as simple_error:
                        print(f"Simple query ERROR: {simple_error}")
        
        print("\n2. Testing with actual API endpoint simulation:")
        print("-" * 50)
        
        # Test what the actual API would do
        try:
            # This simulates the Flask API call
            from flask import Flask
            app = Flask(__name__)
            
            with app.test_request_context(f'/api/top-performers/{test_form_level}/languages?term={test_term}&academic_year={test_academic_year}'):
                # This simulates the actual API endpoint logic
                performers = db.get_top_performers(test_form_level, 'languages', test_term, test_academic_year, test_school_id)
                print(f"API simulation SUCCESS: {len(performers)} performers")
                
                if performers:
                    print(f"Top performer: {performers[0].get('name', 'Unknown')}")
                    
        except Exception as api_error:
            print(f"API simulation ERROR: {api_error}")
        
    except Exception as e:
        print(f"Error during simple test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_top_performers()
