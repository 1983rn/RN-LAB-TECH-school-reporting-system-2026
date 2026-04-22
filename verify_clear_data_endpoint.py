#!/usr/bin/env python3
"""
Test script to verify the clear-form-data API endpoint is properly registered
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_endpoint_registration():
    """Test that the API endpoint is properly registered in Flask"""
    
    print("=== Verifying Clear Data API Endpoint ===")
    
    try:
        # Import the Flask app
        from app import app
        
        # Print all registered routes
        print("\nRegistered API routes:")
        for rule in app.url_map.iter_rules():
            if '/api/' in rule.rule:
                print(f"  {rule.rule} - {rule.methods}")
        
        # Check if our specific endpoint exists
        target_endpoint = '/api/clear-form-data'
        endpoint_exists = False
        
        for rule in app.url_map.iter_rules():
            if rule.rule == target_endpoint:
                endpoint_exists = True
                print(f"\n** FOUND: {rule.rule} - {rule.methods} **")
                break
        
        if not endpoint_exists:
            print(f"\n** ERROR: Endpoint {target_endpoint} not found! **")
            print("\nTroubleshooting steps:")
            print("1. Restart the Flask application")
            print("2. Check for syntax errors in app.py")
            print("3. Verify the endpoint is properly indented")
            
            # Try to find the endpoint function in the source
            print(f"\nChecking source code...")
            try:
                with open(os.path.join(current_dir, 'app.py'), 'r') as f:
                    content = f.read()
                    if '@app.route(\'/api/clear-form-data\'' in content:
                        print("  - Route decorator found in source code")
                    else:
                        print("  - Route decorator NOT found in source code")
                    
                    if 'def api_clear_form_data():' in content:
                        print("  - Function definition found in source code")
                    else:
                        print("  - Function definition NOT found in source code")
                        
            except Exception as e:
                print(f"  - Error reading source code: {e}")
        else:
            print(f"\n** SUCCESS: Endpoint {target_endpoint} is properly registered! **")
        
        # Test the endpoint function directly
        print(f"\nTesting endpoint function directly...")
        try:
            # Import the function
            from app import api_clear_form_data
            print("  - Function imported successfully")
            print("  - Function signature:", api_clear_form_data.__name__)
        except ImportError as e:
            print(f"  - Error importing function: {e}")
        
        return endpoint_exists
        
    except Exception as e:
        print(f"\n** Error testing endpoint: {e} **")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_endpoint_registration()
    
    if success:
        print(f"\n** NEXT STEPS: **")
        print("1. Restart your Flask application")
        print("2. Try the Clear Data functionality in the web interface")
        print("3. Check browser console for any JavaScript errors")
    else:
        print(f"\n** FIXES NEEDED: **")
        print("1. Check app.py for syntax errors")
        print("2. Ensure proper indentation of the endpoint")
        print("3. Restart the Flask application after fixing")
