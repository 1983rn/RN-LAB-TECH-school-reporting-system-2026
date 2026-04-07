# NANJATI CDSS DATA RESTORATION GUIDE

## Overview
This document outlines the complete data restoration process for Nanjati Community Day Secondary School (CDSS) in the School Reporting System.

## Current System Status
- **School Name**: Nanjati CDSS
- **Database**: SQLite (school_reports.db)
- **Active Forms**: Form 1, Form 2, Form 3, Form 4
- **Academic Year**: 2024
- **Terms**: Term 1, Term 2, Term 3

## Data Restoration Scripts

### 1. Main Restoration Script
**File**: `restore_nanjati_term3_data.py`
- Restores Term 3 marks for all forms
- Handles subject-specific data entry
- Maintains academic integrity

### 2. Batch Execution
**Files**: 
- `restore_nanjati_data.bat` (Windows Batch)
- `restore_nanjati_data.ps1` (PowerShell)

## Restoration Process

### Step 1: Database Backup
```bash
# Create backup before restoration
copy school_reports.db school_reports_backup.db
```

### Step 2: Execute Restoration
```bash
# Run the restoration script
python restore_nanjati_term3_data.py
```

### Step 3: Verification
```bash
# Verify data integrity
python check_term3_marks.py
python verify_term3_marks.py
```

## Data Structure

### Students by Form Level
- **Form 1**: 45 students
- **Form 2**: 38 students  
- **Form 3**: 42 students
- **Form 4**: 35 students

### Subjects Covered
- Mathematics
- English
- Chichewa
- Biology
- Chemistry
- Physics
- Geography
- History
- Agriculture
- Life Skills

## Key Features Restored

### 1. Academic Records
- Complete student enrollment data
- Subject allocations per form
- Term-wise mark entries
- Grade calculations

### 2. Reporting Capabilities
- Individual student reports
- Class performance analysis
- Top performers identification
- Statistical summaries

### 3. Administrative Functions
- Teacher assignments
- Subject management
- Academic period tracking
- School settings configuration

## Quality Assurance

### Data Validation Checks
1. **Student Count Verification**
   - Ensure all students are properly enrolled
   - Verify form level assignments

2. **Mark Entry Validation**
   - Check for complete subject coverage
   - Validate grade calculations
   - Ensure proper term assignments

3. **Report Generation Testing**
   - Generate sample reports for each form
   - Verify PDF output formatting
   - Test ranking calculations

## Troubleshooting

### Common Issues
1. **Database Lock Errors**
   - Close all database connections
   - Restart the application
   - Re-run restoration script

2. **Missing Student Data**
   - Check student enrollment status
   - Verify form level assignments
   - Re-run specific form restoration

3. **Incorrect Calculations**
   - Verify subject mark entries
   - Check grade boundary settings
   - Recalculate aggregates

### Debug Scripts Available
- `debug_form3.py` - Form 3 specific debugging
- `simple_debug.py` - General system debugging
- `check_database_state.py` - Database integrity check

## System Integration

### Web Application
- **URL**: http://localhost:5000
- **Login**: School-specific credentials
- **Features**: Full reporting suite available

### API Endpoints
- Student data management
- Mark entry and retrieval
- Report generation
- Performance analytics

## Maintenance Schedule

### Daily Tasks
- Database backup
- System health check
- User activity monitoring

### Weekly Tasks
- Performance optimization
- Data integrity verification
- Report generation testing

### Monthly Tasks
- Complete system backup
- Security audit
- Feature updates deployment

## Contact Information
- **System Administrator**: Nanjati CDSS IT Department
- **Developer Support**: Available via system logs
- **Emergency Contact**: School Administration

## Version History
- **v1.0**: Initial data restoration (Term 3 2024)
- **v1.1**: Enhanced validation and error handling
- **v1.2**: Improved reporting capabilities
- **v1.3**: Multi-form optimization

---
*Last Updated: December 2024*
*Document Version: 1.0*