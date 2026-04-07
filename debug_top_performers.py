#!/usr/bin/env python3
"""
Debug script to test top performers functionality
"""

from school_database import SchoolDatabase
from performance_analyzer import PerformanceAnalyzer

def test_top_performers():
    """Test the top performers functionality"""
    db = SchoolDatabase()
    analyzer = PerformanceAnalyzer()
    
    print("=== DEBUGGING TOP PERFORMERS ===")
    
    # Check if we have any students
    print("\n1. Checking students in database:")
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]
        print(f"Total students: {student_count}")
        
        if student_count > 0:
            cursor.execute("SELECT grade_level, COUNT(*) FROM students GROUP BY grade_level")
            for row in cursor.fetchall():
                print(f"  Form {row[0]}: {row[1]} students")
    
    # Check if we have any marks
    print("\n2. Checking marks in database:")
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM student_marks")
        marks_count = cursor.fetchone()[0]
        print(f"Total marks: {marks_count}")
        
        if marks_count > 0:
            cursor.execute("SELECT term, academic_year, COUNT(*) FROM student_marks GROUP BY term, academic_year")
            for row in cursor.fetchall():
                print(f"  {row[0]} {row[1]}: {row[2]} marks")
    
    # Test top performers for each category
    test_params = {
        'form_level': 1,
        'term': 'Term 1',
        'academic_year': '2024-2025'
    }
    
    categories = ['overall', 'sciences', 'humanities', 'languages']
    
    print(f"\n3. Testing top performers for Form {test_params['form_level']}, {test_params['term']} {test_params['academic_year']}:")
    
    for category in categories:
        print(f"\n--- {category.upper()} ---")
        try:
            performers = db.get_top_performers(category, **test_params)
            print(f"Found {len(performers)} performers")
            for i, performer in enumerate(performers[:3], 1):
                print(f"  {i}. {performer['name']} - {performer['average']:.1f}%")
        except Exception as e:
            print(f"Error getting {category} performers: {e}")
    
    # Test with different form levels and terms
    print("\n4. Testing different parameters:")
    for form in [1, 2, 3, 4]:
        for term in ['Term 1', 'Term 2', 'Term 3']:
            try:
                performers = db.get_top_performers('overall', form, term, '2024-2025')
                if performers:
                    print(f"  Form {form}, {term}: {len(performers)} performers found")
            except Exception as e:
                print(f"  Form {form}, {term}: Error - {e}")

if __name__ == "__main__":
    test_top_performers()
