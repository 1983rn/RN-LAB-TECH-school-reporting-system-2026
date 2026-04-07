#!/usr/bin/env python3
"""
Test script to verify Flask template configuration
"""

import os
import sys

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_template_config():
    """Test Flask template configuration"""
    print("Testing Flask template configuration...")
    
    # Check if directories exist
    template_dir = os.path.join(current_dir, 'templates')
    static_dir = os.path.join(current_dir, 'static')
    
    print(f"Current directory: {current_dir}")
    print(f"Template directory: {template_dir}")
    print(f"Static directory: {static_dir}")
    
    print(f"Templates directory exists: {os.path.exists(template_dir)}")
    print(f"Static directory exists: {os.path.exists(static_dir)}")
    
    # Check if login.html exists
    login_template = os.path.join(template_dir, 'login.html')
    print(f"login.html exists: {os.path.exists(login_template)}")
    
    # List all templates
    if os.path.exists(template_dir):
        templates = os.listdir(template_dir)
        print(f"Available templates: {templates}")
    
    # Test Flask app import
    try:
        from app import app
        print(f"Flask app imported successfully")
        print(f"App template folder: {app.template_folder}")
        print(f"App static folder: {app.static_folder}")
        
        # Test template rendering
        with app.app_context():
            from flask import render_template
            try:
                # Just check if template can be found (don't actually render)
                template = app.jinja_env.get_template('login.html')
                print("✅ login.html template found successfully!")
                return True
            except Exception as e:
                print(f"❌ Error finding template: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Error importing Flask app: {e}")
        return False

if __name__ == '__main__':
    success = test_template_config()
    sys.exit(0 if success else 1)