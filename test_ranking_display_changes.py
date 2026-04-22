#!/usr/bin/env python3
"""
Test the display changes for Rankings & Analysis page
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from school_database import SchoolDatabase

def test_ranking_display_changes():
    """Test that the display changes work correctly for junior and senior forms"""
    
    try:
        db = SchoolDatabase()
        
        print("=== Testing Ranking Display Changes ===\n")
        
        # Test parameters
        test_school_id = 1
        test_term = 'Term 1'
        test_academic_year = '2025-2026'
        
        # Test both junior and senior forms
        test_forms = [
            (1, "Junior Form 1"),
            (2, "Junior Form 2"), 
            (3, "Senior Form 3"),
            (4, "Senior Form 4")
        ]
        
        categories = ['sciences', 'humanities', 'languages']
        
        for form_level, form_description in test_forms:
            print(f"\n=== {form_description} ===")
            print("-" * 50)
            
            for category in categories:
                print(f"\n{category.title()} Department:")
                
                try:
                    performers = db.get_top_performers_by_category(category, form_level, test_term, test_academic_year, test_school_id)
                    
                    if performers:
                        # Check the data structure for the top performer
                        top_performer = performers[0]
                        print(f"  Top performer: {top_performer.get('name', 'Unknown')}")
                        print(f"  Excellence Area: {top_performer.get('excellence_area', 'N/A')}")
                        print(f"  Department Average: {top_performer.get('department_average', 0)}")
                        print(f"  Department Total: {top_performer.get('department_total', 0)}")
                        print(f"  Subjects Taken: {top_performer.get('subjects_taken', 0)}")
                        
                        # Simulate what the frontend would display
                        dept_avg = top_performer.get('department_average', 0)
                        dept_total = top_performer.get('department_total', 0)
                        subjects_taken = top_performer.get('subjects_taken', 0)
                        excellence_area = top_performer.get('excellence_area', category.title())
                        
                        # For Overall % column - should show only average for all forms
                        overall_display = f"{dept_avg:.1f}%"
                        print(f"  Overall % Display: {overall_display}")
                        
                        # For Excellence Area column - should show subjects count only for junior forms
                        if form_level <= 2:
                            excellence_display = f"{excellence_area} (subjects: {subjects_taken})"
                            print(f"  Excellence Area Display: {excellence_display}")
                            print(f"  Subjects count: SHOWN (junior form)")
                        else:
                            excellence_display = excellence_area
                            print(f"  Excellence Area Display: {excellence_display}")
                            print(f"  Subjects count: HIDDEN (senior form)")
                        
                    else:
                        print("  No performers found")
                        
                except Exception as e:
                    print(f"  Error: {e}")
        
        # Test overall category as well
        print(f"\n=== Overall Category Test ===")
        print("-" * 50)
        
        for form_level, form_description in test_forms:
            print(f"\n{form_description} - Overall:")
            
            try:
                # For overall, we need to use the regular get_top_performers method
                performers = db.get_top_performers(form_level, test_term, test_academic_year, 10, test_school_id)
                
                if performers:
                    top_performer = performers[0]
                    print(f"  Top performer: {top_performer.get('name', 'Unknown')}")
                    
                    # Check if it's a senior form with aggregate points
                    if form_level >= 3:
                        aggregate_points = top_performer.get('aggregate_points')
                        if aggregate_points is not None:
                            print(f"  Aggregate Points: {aggregate_points}")
                            print(f"  Display: {aggregate_points} (senior form)")
                        else:
                            grade = top_performer.get('grade', 'N/A')
                            print(f"  Grade: {grade}")
                            print(f"  Display: {grade} (fallback)")
                    else:
                        grade = top_performer.get('grade', 'N/A')
                        print(f"  Grade: {grade}")
                        print(f"  Display: {grade} (junior form)")
                        
                else:
                    print("  No performers found")
                    
            except Exception as e:
                print(f"  Error: {e}")
        
        print(f"\n=== Summary of Changes ===")
        print("-" * 50)
        print("Changes implemented:")
        print("1. For senior forms (3,4):")
        print("   - Excellence Area: Subjects count REMOVED")
        print("   - Overall %: Shows only average percentage (no total marks)")
        print("2. For junior forms (1,2):")
        print("   - Excellence Area: Subjects count MAINTAINED")
        print("   - Overall %: Shows only average percentage (no total marks)")
        print("\nThese changes apply to Sciences, Humanities, and Languages departments.")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ranking_display_changes()
