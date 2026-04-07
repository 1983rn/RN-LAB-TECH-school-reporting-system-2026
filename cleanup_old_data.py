#!/usr/bin/env python3
"""
Delete all data before 2025-2026 academic year
Keep only Term 1 2025-2026 and later periods
"""

from school_database import SchoolDatabase

def delete_old_data():
    """Delete all academic data before 2025-2026"""
    
    db = SchoolDatabase()
    
    # Academic years to delete (before 2025-2026)
    years_to_delete = ['2024-2025', '2020-2021', '2023-2024', '2022-2023', '2021-2022']
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            print("=== DELETING OLD ACADEMIC DATA ===")
            
            total_marks_deleted = 0
            total_periods_deleted = 0
            
            for year in years_to_delete:
                # Delete all marks for this academic year
                cursor.execute("""
                    DELETE FROM student_marks 
                    WHERE academic_year = ?
                """, (year,))
                marks_deleted = cursor.rowcount
                total_marks_deleted += marks_deleted
                
                # Delete all periods for this academic year
                cursor.execute("""
                    DELETE FROM academic_periods 
                    WHERE academic_year = ?
                """, (year,))
                periods_deleted = cursor.rowcount
                total_periods_deleted += periods_deleted
                
                if marks_deleted > 0 or periods_deleted > 0:
                    print(f"Deleted {year}: {marks_deleted} marks, {periods_deleted} periods")
            
            print(f"\nTotal deleted: {total_marks_deleted} marks, {total_periods_deleted} periods")
            
            # Verify remaining data
            cursor.execute("""
                SELECT DISTINCT academic_year, COUNT(*) as count
                FROM student_marks 
                GROUP BY academic_year 
                ORDER BY academic_year DESC
            """)
            
            remaining_data = cursor.fetchall()
            print(f"\nRemaining academic years with data:")
            for year, count in remaining_data:
                print(f"  - {year}: {count} marks")
            
            print("\nData cleanup completed!")
                
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    delete_old_data()