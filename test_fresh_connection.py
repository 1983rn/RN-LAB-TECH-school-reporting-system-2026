#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Force reimport of the updated module
import importlib
import school_database

def test_fresh_connection():
    """Test with fresh database connection"""
    print("=== TESTING WITH FRESH CONNECTION ===\n")
    
    # Force reload of the module
    importlib.reload(school_database)
    
    # Create fresh instance
    db = school_database.SchoolDatabase()
    
    # Test HAMIDA KAIWE position again
    student_id = 176
    subject = "English"
    term = "Term 3"
    academic_year = "2025-2026"
    form_level = 1
    
    print(f"Testing: Student {student_id}, Subject: {subject}")
    position = db.get_subject_position(student_id, subject, term, academic_year, form_level)
    print(f"Result: {position}")
    
    # Also test overall position
    overall_data = db.get_student_position_and_points(student_id, term, academic_year, form_level)
    overall_pos = overall_data.get('position', 'N/A')
    total_students = overall_data.get('total_students', 'N/A')
    print(f"Overall Position: {overall_pos}/{total_students}")

if __name__ == "__main__":
    test_fresh_connection()
