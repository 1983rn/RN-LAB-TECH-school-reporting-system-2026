#!/usr/bin/env python3
"""Migrate SQLite DB to Postgres

Usage: set DATABASE_URL to target Postgres, and optionally DATABASE_PATH for source SQLite file.
"""
import os
import sqlite3
import psycopg2
from psycopg2.extras import execute_values

def load_env_file():
    """Simple .env file parser to avoid python-dotenv dependency"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(base_dir, '.env')
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
        except Exception as e:
            print(f"Warning: Error reading .env file: {e}")

# Load .env variables
load_env_file()

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

try:
    tgt_conn = psycopg2.connect(TARGET_DSN)
except psycopg2.OperationalError as e:
    error_msg = str(e)
    if "password authentication failed" in error_msg:
        print("\n" + "!"*60)
        print("DATABASE AUTHENTICATION ERROR:")
        print(f"Password authentication failed for user 'postgres'.")
        print("Please check your .env file password.")
        print("!"*60 + "\n")
    elif ("Connection refused" in error_msg or "connection to server at" in error_msg) and "localhost" in TARGET_DSN:
        try:
            fallback_dsn = TARGET_DSN.replace("localhost", "127.0.0.1")
            print(f"Retrying connection with 127.0.0.1 instead of localhost...")
            tgt_conn = psycopg2.connect(fallback_dsn)
            TARGET_DSN = fallback_dsn
        except Exception:
            raise e
    else:
        raise e

tgt_cur = tgt_conn.cursor()

TABLES = [
    'schools', 'school_settings', 'students', 'student_marks', 'student_term_enrollment',
    'subject_teachers', 'school_fees', 'academic_periods', 'subscription_notifications',
    'school_users', 'user_activity_log'
]

# Mapping of tables to their primary key columns for sequence reset
PK_COLUMNS = {
    'schools': 'school_id',
    'school_settings': 'setting_id',
    'students': 'student_id',
    'student_marks': 'mark_id',
    'student_term_enrollment': 'enrollment_id',
    'subject_teachers': 'id',
    'school_fees': 'id',
    'academic_periods': 'period_id',
    'subscription_notifications': 'notification_id',
    'school_users': 'user_id',
    'user_activity_log': 'activity_id'
}

for table in TABLES:
    print(f"Migrating table: {table}")
    
    # Check if source table exists
    try:
        src_cur.execute(f"SELECT * FROM {table}")
    except sqlite3.OperationalError:
        print(f"  Source table {table} does not exist in SQLite, skipping")
        continue
        
    rows = src_cur.fetchall()
    if not rows:
        print("  No rows to migrate")
        continue

    cols = rows[0].keys()
    col_list = ','.join(cols)
    
    # Clear target table
    tgt_cur.execute(f"TRUNCATE TABLE {table} CASCADE")

    values = [tuple(row) for row in rows]

    try:
        execute_values(tgt_cur, f"INSERT INTO {table} ({col_list}) VALUES %s", values)
        tgt_conn.commit()
        print(f"  Inserted {len(values)} rows")
        
        # Reset sequence for the primary key
        if table in PK_COLUMNS:
            pk = PK_COLUMNS[table]
            seq_query = f"SELECT setval(pg_get_serial_sequence('{table}', '{pk}'), (SELECT MAX({pk}) FROM {table}))"
            tgt_cur.execute(seq_query)
            tgt_conn.commit()
            print(f"  Sequence for {table}.{pk} reset")
            
    except Exception as e:
        print(f"  Error migrating {table}: {e}")
        tgt_conn.rollback()

src_cur.close()
src_conn.close()

tgt_cur.close()
tgt_conn.close()

print("Migration complete")
