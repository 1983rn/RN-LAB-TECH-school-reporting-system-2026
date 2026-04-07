#!/usr/bin/env python3
"""
Check and delete Term 3 periods with grade data
Shows periods with actual grade data and deletes specified ones
"""

from school_database import SchoolDatabase

def check_and_delete_periods():
    """Check periods with grade data and delete specified Term 3 periods"""
    
    # Initialize database
    db = SchoolDatabase()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # First, check what periods actually have grade data
            print("=== PERIODS WITH GRADE DATA ===")
            cursor.execute("""
                SELECT DISTINCT sm.term, sm.academic_year, COUNT(*) as mark_count
                FROM student_marks sm
                GROUP BY sm.term, sm.academic_year
                ORDER BY sm.academic_year DESC, sm.term
            """)
            
            periods_with_data = cursor.fetchall()
            print(f"Found {len(periods_with_data)} periods with grade data:")
            
            term3_periods = []
            for term, year, count in periods_with_data:
                print(f"  - {term} {year}: {count} marks")
                if term == 'Term 3' and year in ['2024-2025', '2020-2021']:
                    term3_periods.append((term, year, count))
            
            print(f"\n=== TERM 3 PERIODS TO DELETE ===")
            if term3_periods:
                for term, year, count in term3_periods:
                    print(f"Found: {term} {year} with {count} marks")
                    
                    # Ask for confirmation before deleting data
                    response = input(f"Delete {term} {year} and its {count} marks? (yes/no): ")
                    if response.lower() == 'yes':
                        # Delete marks first
                        cursor.execute("""
                            DELETE FROM student_marks 
                            WHERE term = ? AND academic_year = ?
                        """, (term, year))
                        marks_deleted = cursor.rowcount
                        
                        # Delete from academic_periods
                        cursor.execute("""
                            DELETE FROM academic_periods 
                            WHERE period_name = ? AND academic_year = ?
                        """, (term, year))
                        periods_deleted = cursor.rowcount
                        
                        print(f"✓ Deleted {marks_deleted} marks and {periods_deleted} period records for {term} {year}")
                    else:
                        print(f"✗ Skipped {term} {year}")
            else:
                print("No Term 3 periods found for 2024-2025 or 2020-2021")
                
                # Show all Term 3 periods that exist
                print("\n=== ALL TERM 3 PERIODS ===")
                cursor.execute("""
                    SELECT DISTINCT sm.term, sm.academic_year, COUNT(*) as mark_count
                    FROM student_marks sm
                    WHERE sm.term = 'Term 3'
                    GROUP BY sm.term, sm.academic_year
                    ORDER BY sm.academic_year DESC
                """)
                
                all_term3 = cursor.fetchall()
                for term, year, count in all_term3:
                    print(f"  - {term} {year}: {count} marks")
            
            print("\nOperation completed!")
                
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    check_and_delete_periods()