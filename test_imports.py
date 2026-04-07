#!/usr/bin/env python3
"""
Test script to check if all imports work correctly
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_imports():
    """Test all required imports"""
    try:
        print("Testing Flask import...")
        from flask import Flask
        print("✅ Flask imported successfully")
        
        print("Testing database module...")
        from school_database import SchoolDatabase
        print("✅ SchoolDatabase imported successfully")
        
        print("Testing report generator...")
        from termly_report_generator import TermlyReportGenerator
        print("✅ TermlyReportGenerator imported successfully")
        
        print("Testing performance analyzer...")
        from performance_analyzer import PerformanceAnalyzer
        print("✅ PerformanceAnalyzer imported successfully")
        
        print("Testing main app...")
        from app import app
        print("✅ Flask app imported successfully")
        
        print("\n🎉 All imports successful! The application should work.")
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure all required packages are installed")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_imports()
    input("Press Enter to exit...")