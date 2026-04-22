import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

base_db_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:blessings1983%2F@localhost:5432/school_reports')
TEST_DB_NAME = "school_reports_test"
TEST_DATABASE_URL = base_db_url.replace('school_reports', TEST_DB_NAME)
postgres_url = TEST_DATABASE_URL.replace(TEST_DB_NAME, 'postgres')

print(f"Connecting to: {postgres_url}")
try:
    conn = psycopg2.connect(postgres_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    print("Connected successfully. Attempting to drop database...")
    # Terminate other connections first
    cur.execute(f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{TEST_DB_NAME}' AND pid <> pg_backend_pid();")
    cur.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")
    print("Attempting to create database...")
    cur.execute(f"CREATE DATABASE {TEST_DB_NAME}")
    print("Success!")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
