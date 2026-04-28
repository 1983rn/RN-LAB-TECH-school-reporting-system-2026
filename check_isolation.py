import psycopg2
import os
from school_database import DEFAULT_DATABASE_URL

def check_db():
    db_url = os.environ.get('DATABASE_URL', DEFAULT_DATABASE_URL)
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    print("--- Schools ---")
    cur.execute("SELECT school_id, school_name, username FROM schools")
    for row in cur.fetchall():
        print(row)
        
    print("\n--- School Settings ---")
    cur.execute("SELECT school_id, school_name, school_address, school_phone FROM school_settings")
    for row in cur.fetchall():
        print(row)
        
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_db()
