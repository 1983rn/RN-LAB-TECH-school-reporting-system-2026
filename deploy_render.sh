#!/bin/bash
# Render Deployment Script with Persistent Data Storage
# Ensures data remains intact across deployments

set -e

echo "=== Render Deployment with Persistent Data Storage ==="
echo "Starting deployment at $(date)"

# Check if we're on Render
if [ "$RENDER" != "true" ]; then
    echo "WARNING: Not running on Render - using local deployment"
    export DATABASE_PATH="./data/school_reports.db"
    export BACKUP_DIR="./backups"
else
    echo "Render deployment detected"
    echo "Setting up persistent storage..."
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p "$(dirname "$DATABASE_PATH")"
mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

# Set permissions
echo "Setting permissions..."
chmod 755 "$(dirname "$DATABASE_PATH")"
chmod 644 "$DATABASE_PATH" 2>/dev/null || true
chmod 755 "$BACKUP_DIR"

# Check for existing database
if [ -f "$DATABASE_PATH" ]; then
    echo "Existing database found"
    echo "Database size: $(du -h "$DATABASE_PATH" | cut -f1)"
    
    # Create backup before deployment
    if [ "$AUTO_BACKUP_ENABLED" = "true" ]; then
        echo "Creating pre-deployment backup..."
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        BACKUP_FILE="$BACKUP_DIR/pre_deploy_backup_$TIMESTAMP.db"
        cp "$DATABASE_PATH" "$BACKUP_FILE"
        echo "Backup created: $BACKUP_FILE"
    fi
else
    echo "No existing database - will create new one"
fi

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Run database integrity check
echo "Running database integrity check..."
python -c "
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from school_database import SchoolDatabase
    db = SchoolDatabase()
    print('Database initialized successfully')
    
    # Test basic operations
    result = db.verify_data_integrity_on_startup()
    print(f'Integrity check: {result[\"status\"]} - {result[\"message\"]}')
    
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "ERROR: Database integrity check failed"
    exit 1
fi

# Set up secret key
if [ ! -f "$SECRET_KEY_FILE" ]; then
    echo "Generating secret key..."
    python -c "import secrets; print(secrets.token_hex(32))" > "$SECRET_KEY_FILE"
    chmod 600 "$SECRET_KEY_FILE"
fi

echo "=== Deployment completed successfully ==="
echo "Database path: $DATABASE_PATH"
echo "Backup directory: $BACKUP_DIR"
echo "Log file: $LOG_FILE"

# Start the application
echo "Starting application..."
exec python app.py
