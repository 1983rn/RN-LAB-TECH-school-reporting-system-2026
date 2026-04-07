#!/usr/bin/env python3
"""
Render Deployment Script
Handles deployment-specific tasks and data protection
"""

import os
import sys
import logging
from datetime import datetime

def setup_render_environment():
    """Setup Render-specific environment"""
    print("=== Render Deployment Setup ===")
    
    # Set Render environment variables
    os.environ['RENDER'] = 'true'
    os.environ['DATABASE_PATH'] = '/opt/render/project/src/data/school_reports_persistent.db'
    os.environ['BACKUP_DIR'] = '/opt/render/project/src/backups'
    os.environ['AUTO_BACKUP_ENABLED'] = 'true'
    os.environ['DATA_PROTECTION_ENABLED'] = 'true'
    os.environ['LOG_LEVEL'] = 'INFO'
    os.environ['FLASK_ENV'] = 'production'
    
    # Create necessary directories
    directories = [
        '/opt/render/project/src/data',
        '/opt/render/project/src/backups',
        '/opt/render/project/src/logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('/opt/render/project/src/logs/deploy.log'),
            logging.StreamHandler()
        ]
    )
    
    print("Render environment setup completed")
    return True

def verify_deployment_readiness():
    """Verify that the deployment is ready"""
    print("\n=== Deployment Readiness Check ===")
    
    try:
        # Test database connection
        sys.path.insert(0, '/opt/render/project/src')
        from school_database import SchoolDatabase
        
        db = SchoolDatabase()
        print("✓ Database connection successful")
        
        # Test data integrity
        integrity = db.verify_data_integrity_on_startup()
        print(f"✓ Data integrity: {integrity['status']}")
        
        # Test persistent storage
        db_path = db.get_database_path()
        if os.path.exists(db_path):
            size = os.path.getsize(db_path)
            print(f"✓ Database accessible: {size} bytes")
        else:
            print("✓ Database path ready (new installation)")
        
        print("\n✓ Deployment is ready!")
        return True
        
    except Exception as e:
        print(f"✗ Deployment check failed: {e}")
        return False

if __name__ == "__main__":
    success = setup_render_environment()
    if success:
        verify_deployment_readiness()
    else:
        print("✗ Deployment setup failed")
        sys.exit(1)
