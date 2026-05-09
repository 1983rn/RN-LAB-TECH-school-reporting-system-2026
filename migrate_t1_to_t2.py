import os
import sys
import json
from school_database import SchoolDatabase

def migrate():
    db = SchoolDatabase()
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Identify schools where "selected_term" is "Term 2"
            cursor.execute("SELECT school_id, settings FROM schools")
            schools = cursor.fetchall()
            
            schools_to_fix = []
            for school_id, settings_json in schools:
                try:
                    settings = json.loads(settings_json) if isinstance(settings_json, str) else settings_json
                    if settings.get('selected_term') == 'Term 2' and settings.get('selected_academic_year') == '2025-2026':
                        schools_to_fix.append(school_id)
                except:
                    continue
            
            if not schools_to_fix:
                print("No schools found with 'Term 2' and '2025-2026' as active settings.")
                return

            print(f"Found {len(schools_to_fix)} schools to process: {schools_to_fix}")
            
            for school_id in schools_to_fix:
                print(f"\nProcessing School ID: {school_id}")
                
                # Check for Term 1 marks in 2025-2026 for this school
                cursor.execute("""
                    SELECT COUNT(*) FROM student_marks 
                    WHERE school_id = ? AND academic_year = '2025-2026' AND term = 'Term 1'
                """, (school_id,))
                t1_count = cursor.fetchone()[0]
                
                if t1_count == 0:
                    print("  No Term 1 marks found for 2025-2026. Skipping.")
                    continue
                
                print(f"  Found {t1_count} marks in Term 1 for 2025-2026.")
                
                # UPDATE: Move Term 1 marks to Term 2 for 2025-2026
                # We use ON CONFLICT logic equivalent: Update if T2 exists, or rename if not.
                # Actually, simple UPDATE is best if they don't have T2 marks yet.
                # If they have BOTH, we keep T2 (most recent usually).
                
                cursor.execute("""
                    UPDATE student_marks 
                    SET term = 'Term 2'
                    WHERE school_id = ? AND academic_year = '2025-2026' AND term = 'Term 1'
                    AND NOT EXISTS (
                        SELECT 1 FROM student_marks sm2 
                        WHERE sm2.student_id = student_marks.student_id 
                        AND sm2.subject = student_marks.subject 
                        AND sm2.academic_year = '2025-2026' 
                        AND sm2.term = 'Term 2'
                        AND sm2.school_id = ?
                    )
                """, (school_id, school_id))
                
                moved_count = cursor.rowcount
                print(f"  Moved {moved_count} marks from Term 1 to Term 2.")
                
                # Delete any remaining Term 1 marks that were duplicates (T2 already existed)
                cursor.execute("""
                    DELETE FROM student_marks 
                    WHERE school_id = ? AND academic_year = '2025-2026' AND term = 'Term 1'
                """, (school_id,))
                deleted_count = cursor.rowcount
                if deleted_count > 0:
                    print(f"  Removed {deleted_count} duplicate Term 1 marks (Term 2 was already present).")
            
            conn.commit()
            print("\nMigration completed successfully.")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate()
