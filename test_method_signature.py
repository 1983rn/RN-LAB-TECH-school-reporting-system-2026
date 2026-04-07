#!/usr/bin/env python3
"""
Test script to check get_student_by_id method signature
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from school_database import SchoolDatabase
    
    # Initialize database
    db = SchoolDatabase()
    
    # Check method signature
    import inspect
    sig = inspect.signature(db.get_student_by_id)
    print(f"Method signature: {sig}")
    print(f"Parameters: {list(sig.parameters.keys())}")
    
    # Try to call the method with correct parameters
    try:
        result = db.get_student_by_id(1)
        print(f"Method call successful: {result is not None}")
    except Exception as e:
        print(f"Method call failed: {e}")
    
    print("Test completed successfully!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()