#!/bin/bash
# Render Startup Script
# Ensures persistent data protection on application start

set -e

echo "=== Starting School Reporting System on Render ==="
echo "Start time: $(date)"

# Load environment variables
source /opt/render/project/src/.env.render 2>/dev/null || true

# Set up persistent storage
echo "Setting up persistent storage..."
mkdir -p /opt/render/project/src/data
mkdir -p /opt/render/project/src/backups
mkdir -p /opt/render/project/src/logs

# Check database integrity
echo "Checking database integrity..."
python -c "
import sys
import os
sys.path.insert(0, '/opt/render/project/src')

try:
    from school_database import SchoolDatabase
    from persistent_data_manager import PersistentDataManager
    
    print('Initializing persistent data storage...')
    manager = PersistentDataManager()
    db = SchoolDatabase()
    
    # Verify data integrity
    result = db.verify_data_integrity_on_startup()
    print(f'Data status: {result[\"status\"]} - {result[\"message\"]}')
    
    if result.get('status') == 'valid':
        print('Creating protection checkpoint...')
        db.create_data_protection_checkpoint()
        print('Data protection enabled')
    
except Exception as e:
    print(f'Initialization error: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "ERROR: Database initialization failed"
    exit 1
fi

# Start the application
echo "Starting web application..."
cd /opt/render/project/src
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH
exec python app.py
