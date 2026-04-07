from school_database import SchoolDatabase
import json

db = SchoolDatabase()
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT subject, form_level, teacher_name, school_id FROM subject_teachers WHERE subject IN ('Business Studies','Home Economics') ORDER BY school_id, form_level")
    rows = cursor.fetchall()
    print(json.dumps(rows, ensure_ascii=False, indent=2))
