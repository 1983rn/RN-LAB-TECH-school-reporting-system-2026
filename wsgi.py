#!/usr/bin/env python3
"""
WSGI Configuration for Malawi School Reporting System
Production deployment entry point
"""

import os
import sys
import logging
from flask import render_template  # type: ignore[import-not-found]

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure template and static directories exist
try:
    os.makedirs(os.path.join(current_dir, 'templates'), exist_ok=True)
    os.makedirs(os.path.join(current_dir, 'static'), exist_ok=True)
    logger.info("Ensured template and static directories exist")
except Exception as e:
    logger.error(f"Error creating directories: {e}")

# Import the Flask app
try:
    from app import app
    application = app
    logger.info("Successfully imported app from app")
except Exception as e:
    logger.error(f"Error importing app: {e}")
    # Try importing from app_fixed as fallback
    try:
        from app_fixed import app as app_fixed
        application = app_fixed
        logger.info("Falling back to app_fixed")
    except Exception as e2:
        logger.error(f"Failed to import from app_fixed: {e2}")
        raise

# Configure Flask for production
application.config['ENV'] = os.environ.get('FLASK_ENV', 'production')
application.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'

# Configure SERVER_NAME from environment if provided
server_name = os.environ.get('SERVER_NAME')
if server_name:
    application.config['SERVER_NAME'] = server_name
    logger.info(f'Configured SERVER_NAME from environment: {server_name}')

# Wrap application static handling with WhiteNoise when available
# WhiteNoise serves static files efficiently in production
try:
    from whitenoise import WhiteNoise  # type: ignore[import-not-found]
    # WhiteNoise wraps the Flask app to serve static files
    # Note: Flask's url_for('static', ...) will still work correctly
    application = WhiteNoise(application, root=os.path.join(current_dir, 'static'))
    logger.info("WhiteNoise configured for static file serving")
except ImportError:
    # WhiteNoise not installed; static files will be served by Flask
    logger.warning("WhiteNoise not available; static files will be served by Flask")
except Exception as e:
    logger.warning(f"Error configuring WhiteNoise: {e}; static files will be served by Flask")

if __name__ == "__main__":
    application.run()