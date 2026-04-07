"""
Migration script to add Business Studies and Home Economics to subject_teachers
for all existing schools if they are missing.
Run with: python -m scripts.add_science_subjects_migration
"""
from school_database import SchoolDatabase

NEW_SUBJECTS = ['Business Studies', 'Home Economics']


def run_migration(db: SchoolDatabase):
    updated = 0
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT school_id, school_name FROM schools")
        schools = cursor.fetchall()

    for school_id, school_name in schools:
        missing_overall = []
        for form_level in [1, 2, 3, 4]:
            teachers = db.get_subject_teachers(form_level=form_level, school_id=school_id)
            missing = [sub for sub in NEW_SUBJECTS if sub not in teachers]
            for sub in missing:
                # Insert with placeholder teacher name using explicit SQL to ensure correct school_id
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM subject_teachers WHERE subject = ? AND form_level = ? AND school_id = ?", (sub, form_level, school_id))
                    if cursor.fetchone()[0] == 0:
                        # Insert a school-specific row for the subject/form
                        cursor.execute("""
                            INSERT INTO subject_teachers (subject, form_level, teacher_name, updated_date, school_id)
                            VALUES (?, ?, ?, ?, ?)
                        """, (sub, form_level, f"{sub} Teacher F{form_level}", __import__('datetime').datetime.now().isoformat(), school_id))
            if missing:
                missing_overall.extend(missing)
        if missing_overall:
            updated += 1
            print(f"Updated school {school_name} (id={school_id}) with: {sorted(set(missing_overall))}")

    print(f"Migration complete. {updated} schools updated.")


if __name__ == '__main__':
    db = SchoolDatabase()
    run_migration(db)
