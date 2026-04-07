#!/usr/bin/env python3
"""
Test Web Application - Quick verification
"""

def test_imports():
    """Test all imports work correctly"""
    try:
        from app import app
        from school_database import SchoolDatabase
        from termly_report_generator import TermlyReportGenerator
        from performance_analyzer import PerformanceAnalyzer
        print("SUCCESS: All imports working correctly!")
        return True
    except Exception as e:
        print(f"ERROR: Import failed - {e}")
        return False

def test_database():
    """Test database operations"""
    try:
        from school_database import SchoolDatabase
        db = SchoolDatabase()
        
        # Test getting students
        students = db.get_students_by_grade(1)
        print(f"SUCCESS: Found {len(students)} students in Form 1")
        
        if students:
            # Test getting marks
            marks = db.get_student_marks(students[0]['student_id'], 'Term 1', '2024-2025')
            print(f"SUCCESS: Retrieved marks for student {students[0]['student_id']}")
        
        return True
    except Exception as e:
        print(f"ERROR: Database test failed - {e}")
        return False

def test_report_generation():
    """Test report generation"""
    try:
        from termly_report_generator import TermlyReportGenerator
        generator = TermlyReportGenerator()
        
        # Test with sample data
        report = generator.generate_progress_report(1, 'Term 1', '2024-2025')
        if report:
            print("SUCCESS: Progress report generated")
        else:
            print("INFO: No data for progress report (expected if no marks entered)")
        
        return True
    except Exception as e:
        print(f"ERROR: Report generation test failed - {e}")
        return False

if __name__ == "__main__":
    print("Testing Malawi School Reporting System Web Application")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Database Test", test_database),
        ("Report Generation Test", test_report_generation)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        if test_func():
            passed += 1
        
    print(f"\n{'='*60}")
    print(f"Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("WEB APPLICATION IS READY!")
        print("Run 'python app.py' to start the server")
        print("Then open http://localhost:5000 in your browser")
    else:
        print("Some tests failed - check errors above")