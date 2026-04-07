#!/usr/bin/env python3
"""
Persistent Data Storage Manager for Render Deployment
Ensures data remains intact across deployments and restarts
"""

import os
import sqlite3
import shutil
import logging
from datetime import datetime
from typing import Dict, List, Optional

class PersistentDataManager:
    """Manages persistent data storage for Render deployment environments"""
    
    def __init__(self):
        self.setup_persistent_storage()
        self.logger = logging.getLogger(__name__)
        
        # Setup auto-backup after logger is initialized
        self.setup_auto_backup()
    
    def setup_persistent_storage(self):
        """Setup persistent storage paths for Render deployment.

        Behavior:
        - If `RENDER=true`, the code prefers a persistent directory. You may
          override the chosen persistent dir with `RENDER_PERSISTENT_DIR` env var.
        - If `RENDER` is not true, it falls back to a local `data/` folder.
        - Environment variable `DATABASE_PATH` is set to a file inside the
          chosen persistent directory so the app and other scripts can read it.
        """

        # Setup logger first
        self.logger = logging.getLogger(__name__)

        # Allow explicit override for persistent dir (useful for testing and non-standard mounts)
        env_override = os.environ.get('RENDER_PERSISTENT_DIR')

        # Check if we're on Render
        is_render = os.environ.get('RENDER', '').lower() == 'true'

        if is_render:
            # Default Render persistent path (common layout)
            default_persistent_dir = '/opt/render/project/src/data'
            persistent_dir = env_override or default_persistent_dir
            backup_dir = os.path.join(persistent_dir, 'backups')

            # Create directories if they don't exist
            os.makedirs(persistent_dir, exist_ok=True)
            os.makedirs(backup_dir, exist_ok=True)

            # Set environment variables for database path if not already set
            os.environ.setdefault('DATABASE_PATH', os.path.join(persistent_dir, 'school_reports_persistent.db'))
            os.environ.setdefault('BACKUP_DIR', backup_dir)

            self.logger.info("Render deployment detected - using persistent storage")
            self.logger.info(f"Database path: {os.environ.get('DATABASE_PATH')}")
            self.logger.info(f"Backup directory: {os.environ.get('BACKUP_DIR')}")

            # Quick validation: ensure DATABASE_PATH is indeed under the persistent dir
            db_path = os.environ.get('DATABASE_PATH')
            try:
                db_real = os.path.realpath(db_path)
                persistent_real = os.path.realpath(persistent_dir)
                if not db_real.startswith(persistent_real):
                    self.logger.warning("Configured DATABASE_PATH does not appear to be on the configured persistent disk")
                    self.logger.warning(f"DATABASE_PATH={db_real}, persistent_dir={persistent_real}")
            except Exception as e:
                self.logger.warning(f"Could not verify DATABASE_PATH location: {e}")

        else:
            # Local development - use current directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(current_dir, 'data')
            backup_dir = os.path.join(current_dir, 'backups')

            os.makedirs(data_dir, exist_ok=True)
            os.makedirs(backup_dir, exist_ok=True)

            os.environ.setdefault('DATABASE_PATH', os.path.join(data_dir, 'school_reports.db'))
            os.environ.setdefault('BACKUP_DIR', backup_dir)

            self.logger.info("Local development detected - using local storage")

    def is_using_persistent_disk(self) -> bool:
        """Return True if the configured `DATABASE_PATH` looks like it's on a persistent disk."""
        db_path = os.environ.get('DATABASE_PATH')
        if not db_path:
            return False
        # Heuristic: if RENDER is true or path starts with /opt/render or custom override
        if os.environ.get('RENDER', '').lower() == 'true':
            return True
        # Also treat explicitly set DATABASE_PATH outside the repo as persistent
        repo_root = os.path.dirname(os.path.abspath(__file__))
        db_real = os.path.realpath(db_path)
        if not db_real.startswith(repo_root):
            return True
        return False
    
    def get_database_path(self) -> str:
        """Get the persistent database path"""
        return os.environ.get('DATABASE_PATH', 'school_reports.db')
    
    def create_backup(self, db_path: str) -> str:
        """Create a backup of the current database"""
        try:
            backup_dir = os.environ.get('BACKUP_DIR', 'backups')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'school_reports_backup_{timestamp}.db'
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # Copy database to backup location
            shutil.copy2(db_path, backup_path)
            
            self.logger.info(f"Database backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return None
    
    def restore_from_backup(self, backup_path: str, target_path: str) -> bool:
        """Restore database from backup"""
        try:
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, target_path)
                self.logger.info(f"Database restored from backup: {backup_path}")
                return True
            else:
                self.logger.error(f"Backup file not found: {backup_path}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to restore from backup: {e}")
            return False
    
    def verify_data_integrity(self, db_path: str) -> Dict:
        """Verify data integrity and return status"""
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Check essential tables exist
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name IN ('students', 'student_marks', 'school_settings', 'schools')
                """)
                tables = [row[0] for row in cursor.fetchall()]
                
                # Count records in essential tables
                table_counts = {}
                for table in ['students', 'student_marks', 'school_settings', 'schools']:
                    if table in tables:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        table_counts[table] = count
                    else:
                        table_counts[table] = 0
                
                return {
                    'tables_exist': len(tables),
                    'table_counts': table_counts,
                    'database_size': os.path.getsize(db_path) if os.path.exists(db_path) else 0,
                    'last_modified': datetime.fromtimestamp(os.path.getmtime(db_path)).isoformat() if os.path.exists(db_path) else None
                }
                
        except Exception as e:
            self.logger.error(f"Data integrity check failed: {e}")
            return {'error': str(e)}
    
    def setup_auto_backup(self):
        """Setup automatic backup system"""
        backup_dir = os.environ.get('BACKUP_DIR', 'backups')
        
        # Create backup script
        backup_script = f"""
#!/bin/bash
# Auto backup script for school database
DB_PATH="{os.environ.get('DATABASE_PATH', 'school_reports.db')}"
BACKUP_DIR="{backup_dir}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/school_reports_auto_backup_$TIMESTAMP.db"

# Create backup
if [ -f "$DB_PATH" ]; then
    cp "$DB_PATH" "$BACKUP_FILE"
    echo "Auto backup created: $BACKUP_FILE"
else
    echo "Database file not found: $DB_PATH"
fi
"""
        
        script_path = os.path.join(backup_dir, 'auto_backup.sh')
        with open(script_path, 'w') as f:
            f.write(backup_script)
        
        # Make script executable
        os.chmod(script_path, 0o755)
        
        self.logger.info(f"Auto backup script created: {script_path}")

def initialize_persistent_storage():
    """Initialize persistent storage for the application"""
    return PersistentDataManager()

if __name__ == "__main__":
    # Test the persistent storage setup
    manager = initialize_persistent_storage()
    
    print("Persistent Data Storage Test")
    print("=" * 40)
    
    db_path = manager.get_database_path()
    print(f"Database path: {db_path}")
    
    # Test data integrity
    integrity = manager.verify_data_integrity(db_path)
    if 'error' not in integrity:
        print(f"Tables found: {integrity['tables_exist']}")
        print(f"Table counts: {integrity['table_counts']}")
        print(f"Database size: {integrity['database_size']} bytes")
        print(f"Last modified: {integrity['last_modified']}")
        
        # Test backup creation
        backup_path = manager.create_backup(db_path)
        if backup_path:
            print(f"Test backup created: {backup_path}")
        
        print("\nSUCCESS: Persistent storage is working correctly!")
    else:
        print(f"ERROR: {integrity['error']}")
