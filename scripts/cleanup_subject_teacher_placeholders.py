#!/usr/bin/env python3
"""
Clean placeholder subject teacher labels in subject_teachers.

Targets values like:
  - "Business Studies Teacher F3"
  - "Home Economics Teacher F4"

Usage:
  python scripts/cleanup_subject_teacher_placeholders.py          # dry-run
  python scripts/cleanup_subject_teacher_placeholders.py --apply  # persist changes
"""

import argparse
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from school_database import SchoolDatabase


PLACEHOLDER_REGEX = r"^\s*.+\s+Teacher\s+F[1-4]\s*$"


def main():
    parser = argparse.ArgumentParser(description="Cleanup placeholder subject teacher values.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply updates. Without this flag, script runs in dry-run mode.",
    )
    args = parser.parse_args()

    db = SchoolDatabase()

    with db.get_connection() as conn:
        cursor = conn.cursor()

        # Find placeholder rows first so user can inspect exactly what will change.
        cursor.execute(
            """
            SELECT id, subject, form_level, school_id, teacher_name
            FROM subject_teachers
            WHERE teacher_name IS NOT NULL
              AND teacher_name ~* ?
            ORDER BY school_id, form_level, subject
            """,
            (PLACEHOLDER_REGEX,),
        )
        rows = cursor.fetchall()

        if not rows:
            print("No placeholder subject teacher values found.")
            return

        print(f"Found {len(rows)} placeholder subject teacher value(s):")
        for row_id, subject, form_level, school_id, teacher_name in rows:
            print(
                f"  id={row_id}, school_id={school_id}, form={form_level}, "
                f"subject='{subject}', teacher_name='{teacher_name}'"
            )

        if not args.apply:
            print("\nDry-run only. Re-run with --apply to persist cleanup.")
            return

        cursor.execute(
            """
            UPDATE subject_teachers
            SET teacher_name = ''
            WHERE teacher_name IS NOT NULL
              AND teacher_name ~* ?
            """,
            (PLACEHOLDER_REGEX,),
        )
        updated = cursor.rowcount
        conn.commit()
        print(f"\nUpdated {updated} row(s): placeholder values set to empty string.")


if __name__ == "__main__":
    main()
