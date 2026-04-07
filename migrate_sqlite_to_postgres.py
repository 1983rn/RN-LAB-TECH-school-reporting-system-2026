#!/usr/bin/env python3
"""Migrate SQLite DB to Postgres

Usage: set DATABASE_URL to target Postgres, and optionally DATABASE_PATH for source SQLite file.
"""
import os
import sqlite3
import psycopg2
from psycopg2.extras import execute_values

SOURCE_DB = os.environ.get('DATABASE_PATH', 'school_reports.db')
TARGET_DSN = os.environ.get('DATABASE_URL')

if not TARGET_DSN:
    raise SystemExit('Please set DATABASE_URL to the target Postgres database')

print(f"Source SQLite: {SOURCE_DB}")
print(f"Target Postgres: {TARGET_DSN}")

# Connect to source and target
src_conn = sqlite3.connect(SOURCE_DB)
src_conn.row_factory = sqlite3.Row
src_cur = src_conn.cursor()

tgt_conn = psycopg2.connect(TARGET_DSN)
tgt_cur = tgt_conn.cursor()

TABLES = [
    'students', 'student_marks', 'school_settings', 'schools', 'subject_teachers', 'school_fees', 'academic_periods', 'subscription_notifications'
]

for table in TABLES:
    print(f"Migrating table: {table}")
    src_cur.execute(f"SELECT * FROM {table}")
    rows = src_cur.fetchall()
    if not rows:
        print("  No rows to migrate")
        continue

    cols = rows[0].keys()
    col_list = ','.join(cols)
    placeholders = ','.join(['%s'] * len(cols))

    insert_sql = f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})"

    values = [tuple(row) for row in rows]

    try:
        execute_values(tgt_cur, f"INSERT INTO {table} ({col_list}) VALUES %s", values)
        tgt_conn.commit()
        print(f"  Inserted {len(values)} rows")
    except Exception as e:
        print(f"  Error migrating {table}: {e}")
        tgt_conn.rollback()

src_cur.close()
src_conn.close()

tgt_cur.close()
tgt_conn.close()

print("Migration complete")
