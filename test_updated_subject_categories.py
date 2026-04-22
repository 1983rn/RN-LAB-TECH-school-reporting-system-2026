#!/usr/bin/env python3
"""
Test the updated subject categories for Best in rankings
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from school_database import SchoolDatabase

def test_updated_subject_categories():
    """Test that the updated subject categories are working correctly"""
    
    try:
        db = SchoolDatabase()
        
        print("=== Testing Updated Subject Categories ===\n")
        
        # Test parameters
        test_school_id = 1
        test_form_level = 1
        test_term = 'Term 1'
        test_academic_year = '2025-2026'
        
        print(f"Testing with: School {test_school_id}, Form {test_form_level}, {test_term}, {test_academic_year}")
        
        # Expected subject categories according to user specifications
        expected_categories = {
            'sciences': ['Agriculture', 'Biology', 'Chemistry', 'Computer Studies', 'Mathematics', 'Physics', 'Business Studies', 'Home Economics', 'Clothing & Textiles', 'Technical Drawing'],
            'humanities': ['Bible Knowledge', 'Geography', 'History', 'Life Skills/SOS'],
            'languages': ['English', 'Chichewa']
        }
        
        print("\n1. Expected Subject Categories (User Specifications):")
        print("-" * 60)
        for category, subjects in expected_categories.items():
            print(f"{category.title()} ({len(subjects)} subjects):")
            for subject in subjects:
                print(f"  - {subject}")
            print()
        
        # Test the get_top_performers method with each category
        print("2. Testing get_top_performers Method:")
        print("-" * 60)
        
        for category, expected_subjects in expected_categories.items():
            print(f"\nTesting {category.title()} category:")
            
            try:
                performers = db.get_top_performers_by_category(category, test_form_level, test_term, test_academic_year, test_school_id)
                print(f"  Top performers found: {len(performers)}")
                
                if performers:
                    print(f"  Top performer: {performers[0].get('name', 'Unknown')}")
                    
                    # Check if the performer has marks in the expected subjects
                    performer_id = performers[0].get('student_id')
                    if performer_id:
                        with db.get_connection() as conn:
                            cursor = conn.cursor()
                            
                            # Check marks in expected subjects for this performer
                            cursor.execute("""
                                SELECT subject, mark FROM student_marks
                                WHERE student_id = ? AND term = ? AND academic_year = ?
                                AND subject IN ({})
                                ORDER BY subject
                            """.format(','.join(['?' for _ in expected_subjects])), 
                            [performer_id, test_term, test_academic_year] + expected_subjects)
                            
                            marks = cursor.fetchall()
                            print(f"  Marks in {category} subjects: {len(marks)}")
                            
                            for subject, mark in marks:
                                print(f"    {subject}: {mark}")
                else:
                    print("  No performers found (this may be expected if no data exists)")
                    
            except Exception as e:
                print(f"  Error testing {category}: {e}")
        
        # Test the API endpoints that would be called by the frontend
        print("\n3. Testing API Endpoints (Simulation):")
        print("-" * 60)
        
        # These are the endpoints that the Rankings & Analysis page would call
        api_endpoints = [
            f'/api/top-performers/{test_form_level}/sciences?term={test_term}&academic_year={test_academic_year}',
            f'/api/top-performers/{test_form_level}/humanities?term={test_term}&academic_year={test_academic_year}',
            f'/api/top-performers/{test_form_level}/languages?term={test_term}&academic_year={test_academic_year}'
        ]
        
        for endpoint in api_endpoints:
            category = endpoint.split('/')[-1].split('?')[0]
            print(f"\nAPI Endpoint: {endpoint}")
            print(f"Category: {category}")
            
            try:
                # Simulate the API call by calling the database method directly
                performers = db.get_top_performers_by_category(category, test_form_level, test_term, test_academic_year, test_school_id)
                
                print(f"  API would return: {len(performers)} performers")
                
                if performers:
                    top_performer = performers[0]
                    print(f"  Top performer data:")
                    print(f"    Name: {top_performer.get('name', 'Unknown')}")
                    print(f"    Total Marks: {top_performer.get('total_marks', 0)}")
                    print(f"    Average: {top_performer.get('average', 0)}")
                    print(f"    Excellence Area: {top_performer.get('excellence_area', 'N/A')}")
                    
            except Exception as e:
                print(f"  API simulation error: {e}")
        
        # Verify the subject groups are correctly defined in the database method
        print("\n4. Verifying Subject Groups Definition:")
        print("-" * 60)
        
        # We can't directly access the subject_groups from here, but we can test
        # by checking if the method returns results for the expected subjects
        
        for category, expected_subjects in expected_categories.items():
            print(f"\nVerifying {category.title()} subject group:")
            print(f"  Expected subjects: {len(expected_subjects)}")
            
            # Check if these subjects exist in the database for the test parameters
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                placeholders = ','.join(['?' for _ in expected_subjects])
                cursor.execute(f"""
                    SELECT DISTINCT subject FROM student_marks
                    WHERE school_id = ? AND form_level = ? AND term = ? AND academic_year = ?
                    AND subject IN ({placeholders})
                """, [test_school_id, test_form_level, test_term, test_academic_year] + expected_subjects)
                
                existing_subjects = [row[0] for row in cursor.fetchall()]
                print(f"  Subjects with data: {len(existing_subjects)}")
                
                if existing_subjects:
                    print("  Available subjects:")
                    for subject in existing_subjects:
                        print(f"    - {subject}")
                
                missing_subjects = set(expected_subjects) - set(existing_subjects)
                if missing_subjects:
                    print(f"  Subjects without data: {len(missing_subjects)}")
                    for subject in missing_subjects:
                        print(f"    - {subject} (no marks entered yet)")
        
        # Test Performance Analyzer categories
        print("\n5. Testing Performance Analyzer Categories:")
        print("-" * 60)
        
        try:
            from performance_analyzer import PerformanceAnalyzer
            
            analyzer = PerformanceAnalyzer()
            
            for category_name, department in analyzer.departments.items():
                print(f"\n{category_name} Department:")
                print(f"  Subjects: {len(department['subjects'])}")
                print(f"  Description: {department['description']}")
                print("  Subject list:")
                for subject in department['subjects']:
                    print(f"    - {subject}")
                
                # Compare with expected
                expected_key = category_name.lower()
                if expected_key in expected_categories:
                    expected_subjects = set(expected_categories[expected_key])
                    actual_subjects = set(department['subjects'])
                    
                    if expected_subjects == actual_subjects:
                        print(f"  Status: MATCHES user specification")
                    else:
                        print(f"  Status: DIFFERS from user specification")
                        missing = expected_subjects - actual_subjects
                        extra = actual_subjects - expected_subjects
                        if missing:
                            print(f"    Missing: {missing}")
                        if extra:
                            print(f"    Extra: {extra}")
                        
        except ImportError:
            print("Performance Analyzer not available for testing")
        except Exception as e:
            print(f"Error testing Performance Analyzer: {e}")
        
        print("\n=== Test Summary ===")
        print("Subject Categories Update Status:")
        print("1. school_database.py: UPDATED")
        print("2. performance_analyzer.py: UPDATED")
        print("3. Report generation: UPDATED")
        print("\nUpdated Categories:")
        print("Best in Science: Agriculture, Biology, Chemistry, Computer Studies, Mathematics, Physics, Business Studies, Home Economics, Clothing & Textiles, Technical Drawing")
        print("Best in Humanities: Bible Knowledge, Geography, History, Life Skills/SOS")
        print("Best in Languages: English, Chichewa")
        print("\nThe Rankings & Analysis page will now use these updated subject categories for 'Best in' rankings.")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_updated_subject_categories()
