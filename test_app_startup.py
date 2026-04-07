#!/usr/bin/env python3
"""
Test script to verify the Flask application can start without errors
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_imports():
    """Test if all modules can be imported"""
    try:
        print("Testing imports...")
        
        # Test database import
        from school_database import SchoolDatabase
        print("✅ SchoolDatabase imported successfully")
        
        # Test report generator import
        from termly_report_generator import TermlyReportGenerator
        print("✅ TermlyReportGenerator imported successfully")
        
        # Test performance analyzer import
        from performance_analyzer import PerformanceAnalyzer
        print("✅ PerformanceAnalyzer imported successfully")
        
        # Test Flask app import
        from app import app
        print("✅ Flask app imported successfully")
        
        assert True
    except Exception as e:
        print(f"❌ Import error: {e}")
        assert False, f"Import error: {e}"

def test_database_connection():
    """Test database connection"""
    try:
        print("\nTesting database connection...")
        from school_database import SchoolDatabase
        db = SchoolDatabase()
        print("✅ Database connection successful")
        assert True
    except Exception as e:
        print(f"❌ Database error: {e}")
        assert False, f"Database error: {e}"

def test_app_creation():
    """Test Flask app creation"""
    try:
        print("\nTesting Flask app creation...")
        from app import app, db, generator, analyzer
        print("✅ Flask app created successfully")
        print(f"✅ Database instance: {type(db).__name__}")
        print(f"✅ Generator instance: {type(generator).__name__}")
        print(f"✅ Analyzer instance: {type(analyzer).__name__}")
        assert True
    except Exception as e:
        print(f"❌ App creation error: {e}")
        assert False, f"App creation error: {e}"

def main():
    """Run all tests"""
    print("🧪 Testing School Reporting System Application")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_database_connection,
        test_app_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application should start successfully.")
        print("\nTo start the application:")
        print("1. Run: run_web_app.bat (Windows)")
        print("2. Or run: python app.py")
        print("3. Open browser to: http://localhost:5000")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)