
#!/bin/bash
# Auto backup script for school database
DB_PATH="D:\2025-2026\PRODUCTION\USA\RN-LAB-TECH-school-reporting-system-2026-1\data\school_reports.db"
BACKUP_DIR="D:\2025-2026\PRODUCTION\USA\RN-LAB-TECH-school-reporting-system-2026-1\backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/school_reports_auto_backup_$TIMESTAMP.db"

# Create backup
if [ -f "$DB_PATH" ]; then
    cp "$DB_PATH" "$BACKUP_FILE"
    echo "Auto backup created: $BACKUP_FILE"
else
    echo "Database file not found: $DB_PATH"
fi
