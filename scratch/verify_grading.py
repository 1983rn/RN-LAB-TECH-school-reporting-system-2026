from school_database import SchoolDatabase

db = SchoolDatabase()

print("--- Testing Junior Defaults ---")
for grade in ['A', 'B', 'C', 'D', 'F']:
    comment = db.get_teacher_comment(grade, form_level=1)
    print(f"Grade {grade}: {comment}")

print("\n--- Testing Senior Defaults ---")
for grade in ['1', '4', '7', '9']:
    comment = db.get_teacher_comment(grade, form_level=3)
    print(f"Grade {grade}: {comment}")

# Simulate a school with custom rules
school_id = 999
custom_junior = [
    {"grade": "A", "min": 85, "max": 100, "comment": "Superb"},
    {"grade": "D", "min": 50, "max": 59, "comment": "Room for Improvement"}
]

from unittest.mock import MagicMock
db.get_school_settings = MagicMock(return_value={'junior_grading_rules': custom_junior})

print("\n--- Testing Custom Rules (Mocked School 999) ---")
print(f"Grade A (Custom): {db.get_teacher_comment('A', form_level=1, school_id=school_id)}")
print(f"Grade D (Custom): {db.get_teacher_comment('D', form_level=1, school_id=school_id)}")
print(f"Grade B (Fallback): {db.get_teacher_comment('B', form_level=1, school_id=school_id)}")
