#!/usr/bin/env python3
"""
Debug the SQL issue by examining the exact query being generated
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from school_database import SchoolDatabase

def debug_sql_issue():
    """Debug the SQL parameter binding issue"""
    
    try:
        db = SchoolDatabase()
        
        print("=== SQL Issue Debug ===\n")
        
        # Test parameters
        test_school_id = 1
        test_form_level = 1
        test_term = 'Term 1'
        test_academic_year = '2025-2026'
        
        # Test subjects for languages
        subjects = ['English', 'Chichewa']
        
        # Generate placeholders the same way the method does
        placeholders = ','.join(['?' for _ in subjects])
        
        print(f"Subjects: {subjects}")
        print(f"Placeholders: {placeholders}")
        print(f"Number of placeholders: {len(placeholders.split(','))}")
        
        # Build the SQL query
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
        
        print(f"\nGenerated SQL Query:")
        print(sql_query)
        
        # Parameters
        params = (test_form_level, test_term, test_academic_year, test_school_id, *subjects)
        print(f"\nParameters: {params}")
        print(f"Number of parameters: {len(params)}")
        
        # Count the ? placeholders in the query
        question_mark_count = sql_query.count('?')
        print(f"Question marks in query: {question_mark_count}")
        
        if question_mark_count != len(params):
            print(f"MISMATCH: {question_mark_count} placeholders vs {len(params)} parameters")
            print("This is the cause of the SQL error!")
        else:
            print("Parameter count matches - this should work")
        
        # Test the query manually
        print("\nTesting manual query execution:")
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql_query, params)
                rows = cursor.fetchall()
                print(f"SUCCESS: {len(rows)} rows returned")
                
        except Exception as e:
            print(f"ERROR: {e}")
            
            # Let's try to fix it by checking if there are any issues with the f-string
            print("\nTrying alternative approach...")
            
            # Try building the query step by step
            base_query = """
                SELECT s.student_id, s.first_name, s.last_name, 
                       SUM(sm.mark) as department_total,
                       COUNT(DISTINCT sm.subject) as subjects_taken
                FROM students s
                JOIN student_marks sm ON s.student_id = sm.student_id
                WHERE sm.form_level = ? AND sm.term = ? AND sm.academic_year = ? AND s.school_id = ?
            """
            
            if subjects:
                subject_list = ', '.join([f"'{subject}'" for subject in subjects])
                full_query = f"{base_query} AND sm.subject IN ({subject_list})"
            else:
                full_query = base_query
            
            full_query += """
                GROUP BY s.student_id, s.first_name, s.last_name
                HAVING subjects_taken >= 1
                ORDER BY department_total DESC
                LIMIT 10
            """
            
            print(f"Alternative query:")
            print(full_query)
            
            # Now we only need the basic parameters
            alt_params = (test_form_level, test_term, test_academic_year, test_school_id)
            print(f"Alternative parameters: {alt_params}")
            
            try:
                cursor.execute(full_query, alt_params)
                rows = cursor.fetchall()
                print(f"Alternative SUCCESS: {len(rows)} rows returned")
                
                for row in rows[:3]:
                    student_id, first_name, last_name, department_total, subjects_taken = row
                    print(f"  {first_name} {last_name}: {department_total} marks from {subjects_taken} subjects")
                    
            except Exception as alt_error:
                print(f"Alternative ERROR: {alt_error}")
        
    except Exception as e:
        print(f"Debug error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_sql_issue()
