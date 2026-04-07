#!/usr/bin/env python3
"""
Delete specific periods from settings
Removes Term 3 for academic years 2024-2025 and 2020-2021
"""

from school_database import SchoolDatabase

def delete_specified_periods():
    """Delete Term 3 for academic years 2024-2025 and 2020-2021"""
    
    # Initialize database
    db = SchoolDatabase()
    
    # Periods to delete
    periods_to_delete = [
        {'term': 'Term 3', 'academic_year': '2024-2025'},
        {'term': 'Term 3', 'academic_year': '2020-2021'}
    ]
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Delete the specified periods from academic_periods table
            for period in periods_to_delete:
                cursor.execute("""
                    DELETE FROM academic_periods 
                    WHERE period_name = ? AND academic_year = ?
                """, (period['term'], period['academic_year']))
                
                deleted_count = cursor.rowcount
                print(f"Deleted {deleted_count} record(s) for {period['term']} {period['academic_year']}")
            
            print("\nPeriod deletion completed successfully!")
            
            # Show remaining periods
            cursor.execute("""
                SELECT academic_year, period_name, school_id 
                FROM academic_periods 
                ORDER BY academic_year DESC, period_name
            """)
            
            remaining_periods = cursor.fetchall()
            print(f"\nRemaining periods in database: {len(remaining_periods)}")
            for year, term, school_id in remaining_periods:
                print(f"  - {term} {year} (School ID: {school_id})")
                
    except Exception as e:
        print(f"Error deleting periods: {e}")
        raise

if __name__ == "__main__":
    delete_specified_periods()