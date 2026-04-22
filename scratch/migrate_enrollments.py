from school_database import SchoolDatabase
import sqlite3

def migrate_enrollments():
    db = SchoolDatabase()
    print(f"Migrating enrollments from student_marks to student_term_enrollment...")
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Find all unique student presence in terms
            cursor.execute("""
                SELECT DISTINCT student_id, term, academic_year, form_level, school_id 
                FROM student_marks
            """)
            
            records = cursor.fetchall()
            print(f"Found {len(records)} unique student-term records in student_marks.")
            
            count = 0
            for record in records:
                student_id, term, academic_year, form_level, school_id = record
                cursor.execute("""
                    INSERT OR IGNORE INTO student_term_enrollment 
                    (student_id, term, academic_year, form_level, school_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (student_id, term, academic_year, form_level, school_id))
                if cursor.rowcount > 0:
                    count += 1
            
            conn.commit()
            print(f"Successfully migrated {count} enrollment records.")
            
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate_enrollments()
