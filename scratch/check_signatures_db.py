
from school_database import SchoolDatabase
import json

db = SchoolDatabase()
# Let's assume school_id 1 for testing, or we can check all
with db.get_connection() as conn:
    cur = conn.cursor()
    cur.execute("SELECT school_id, school_name, head_teacher_signature, form_1_teacher_signature FROM school_settings")
    rows = cur.fetchall()
    for row in rows:
        print(f"School ID: {row[0]}, Name: {row[1]}")
        print(f"  Head Teacher Sig: {row[2]}")
        print(f"  Form 1 Teacher Sig: {row[3]}")
        print("-" * 20)
