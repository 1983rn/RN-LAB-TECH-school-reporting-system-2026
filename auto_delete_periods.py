#!/usr/bin/env python3
"""
Automatically delete Term 3 periods for specified academic years
Deletes both grade data and period records
"""

from school_database import SchoolDatabase

def delete_term3_periods():
    """Delete Term 3 for academic years 2024-2025 and 2020-2021"""
    
    # Initialize database
    db = SchoolDatabase()
    
    # Target periods to delete
    target_periods = [
        {'term': 'Term 3', 'academic_year': '2024-2025'},
        {'term': 'Term 3', 'academic_year': '2020-2021'}
    ]
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            print("=== DELETING TERM 3 PERIODS ===")
            
            for period in target_periods:
                term = period['term']
                year = period['academic_year']
                
                # Check if marks exist for this period
                cursor.execute("""
                    SELECT COUNT(*) FROM student_marks 
                    WHERE term = ? AND academic_year = ?
                """, (term, year))
                
                mark_count = cursor.fetchone()[0]
                
                if mark_count > 0:
                    # Delete marks first
                    cursor.execute("""
                        DELETE FROM student_marks 
                        WHERE term = ? AND academic_year = ?
                    """, (term, year))
                    marks_deleted = cursor.rowcount
                    print(f"DELETED {marks_deleted} marks for {term} {year}")
                else:
                    print(f"- No marks found for {term} {year}")
                
                # Delete from academic_periods table
                cursor.execute("""
                    DELETE FROM academic_periods 
                    WHERE period_name = ? AND academic_year = ?
                """, (term, year))
                periods_deleted = cursor.rowcount
                
                if periods_deleted > 0:
                    print(f"DELETED {periods_deleted} period record(s) for {term} {year}")
                else:
                    print(f"- No period records found for {term} {year}")
            
            print("\n=== VERIFICATION ===")
            # Verify deletion by checking remaining Term 3 periods
            cursor.execute("""
                SELECT DISTINCT sm.term, sm.academic_year, COUNT(*) as mark_count
                FROM student_marks sm
                WHERE sm.term = 'Term 3'
                GROUP BY sm.term, sm.academic_year
                ORDER BY sm.academic_year DESC
            """)
            
            remaining_term3 = cursor.fetchall()
            print(f"Remaining Term 3 periods with data: {len(remaining_term3)}")
            for term, year, count in remaining_term3:
                print(f"  - {term} {year}: {count} marks")
            
            # Check academic_periods table
            cursor.execute("""
                SELECT DISTINCT academic_year, period_name 
                FROM academic_periods 
                WHERE period_name = 'Term 3'
                ORDER BY academic_year DESC
            """)
            
            remaining_periods = cursor.fetchall()
            print(f"\nRemaining Term 3 in academic_periods: {len(remaining_periods)}")
            for year, term in remaining_periods:
                print(f"  - {term} {year}")
            
            print("\nDeletion completed successfully!")
                
    except Exception as e:
        print(f"Error deleting periods: {e}")
        raise

if __name__ == "__main__":
    delete_term3_periods()