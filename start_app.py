#!/usr/bin/env python3
"""
Simple startup script for the School Reporting System
This script will start the Flask application with proper error handling
"""

import sys
import os
import traceback

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def main():
    """Start the Flask application"""
    try:
        print("🚀 Starting School Reporting System...")
        print("=" * 50)
        
        # Import the Flask app
        from app import app

        # If the app failed initialization during import, report and pause so the
        # console doesn't flash and close when users double-click the script.
        if not getattr(app, 'INIT_OK', True):
            msg = 'Application failed to initialize during import. The server will not start. See the earlier traceback for details.'
            # Prefer app's GUI-friendly message when available
            try:
                if hasattr(app, 'show_error_message'):
                    app.show_error_message('Initialization Error', msg)
                else:
                    print('\n❌ ' + msg)
                    try:
                        input('Press Enter to exit...')
                    except Exception:
                        pass
            except Exception:
                # Fallback to a simple print/pause if anything goes wrong
                print('\n❌ ' + msg)
                try:
                    input('Press Enter to exit...')
                except Exception:
                    pass
            return False

        print("✅ Flask application loaded successfully!")
        print("🌐 Starting web server...")
        print("📱 Open your browser and go to: http://localhost:5000")
        print("🔑 Login credentials:")
        print("   Developer: MAKONOKAya / NAMADEYIMKOLOWEKO1949")
        print("=" * 50)
        print("Press Ctrl+C to stop the server")
        print()
        
        # Start the Flask development server
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=False  # Disable reloader to avoid double startup
        )
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure all required packages are installed:")
        print("   pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        print("\n🔍 Full error details:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        input("Press Enter to exit...")
        sys.exit(1)