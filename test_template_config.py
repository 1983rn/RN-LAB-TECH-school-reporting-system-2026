#!/usr/bin/env python3
"""
Template Configuration Test
Tests if Flask can properly locate and render templates
"""

import os
import sys
from flask import Flask, render_template

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_template_config():
    """Test Flask template configuration"""
    
    # Configure Flask app with explicit paths (same as main app)
    template_dir = os.path.join(current_dir, 'templates')
    static_dir = os.path.join(current_dir, 'static')
    
    print(f"Testing template configuration...")
    print(f"Current directory: {current_dir}")
    print(f"Template directory: {template_dir}")
    print(f"Static directory: {static_dir}")
    
    # Check if directories exist
    print(f"\nDirectory checks:")
    print(f"Templates exist: {os.path.exists(template_dir)}")
    print(f"Static exists: {os.path.exists(static_dir)}")
    
    if os.path.exists(template_dir):
        templates = os.listdir(template_dir)
        print(f"Template files found: {templates}")
    
    # Create Flask app
    app = Flask(__name__, 
               template_folder=template_dir,
               static_folder=static_dir)
    
    @app.route('/test')
    def test_route():
        return render_template('login.html')
    
    # Test template rendering with request context
    with app.test_request_context():
        try:
            # Try to render a simple template
            rendered = render_template('login.html')
            print(f"\nSUCCESS: Template rendering works!")
            print(f"Rendered content length: {len(rendered)} characters")
            return True
        except Exception as e:
            print(f"\nERROR: Template rendering failed: {e}")
            return False

if __name__ == '__main__':
    success = test_template_config()
    if success:
        print("\nTemplate configuration is working correctly!")
    else:
        print("\nTemplate configuration needs attention.")