#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from school_database import SchoolDatabase

def trace_subject_position_logic():
    """Trace step by step through subject position logic"""
    db = SchoolDatabase()
    
    print("=== TRACING SUBJECT POSITION LOGIC ===\n")
    
    # Test data: HAMIDA KAIWE with NULL mark, ALFRED with 77 marks
    test_data = [
        {'student_id': 176, 'mark': None},      # HAMIDA
        {'student_id': 166, 'mark': 77},       # ALFRED
    ]
    
    # Simulate the sorting logic from get_subject_position
    print("Test data:")
    for i, data in enumerate(test_data):
        print(f"  {i+1}. Student {data['student_id']}: {data['mark']}")
    
    # Apply the sorting logic
    sorted_data = sorted(test_data, key=lambda x: (x['mark'] is None, 1, -x['mark'] if x['mark'] is not None else 0))
    
    print("\nSorted data:")
    for i, data in enumerate(sorted_data):
        print(f"  {i+1}. Student {data['student_id']}: {data['mark']}")
    
    # Find position of student 176 (HAMIDA)
    target_student_id = 176
    student_position = 0
    for i, student_mark_data in enumerate(sorted_data):
        if student_mark_data['student_id'] == target_student_id:
            student_position = i + 1
            print(f"Found target student at position {student_position}")
            break
    
    print(f"\nResult: Student {target_student_id} position = {student_position}")
    print("Expected: Position 2 (since ALFRED has 77 marks)")
    print("This matches the function behavior we're seeing")

if __name__ == "__main__":
    trace_subject_position_logic()
