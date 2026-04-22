
import os
import psycopg2
from psycopg2.extras import RealDictCursor

def load_env_file():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(base_dir, '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()

load_env_file()
DATABASE_URL = os.environ.get('DATABASE_URL')

def check_settings():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    print("--- Schools ---")
    cur.execute("SELECT school_id, school_name, username FROM schools")
    schools = cur.fetchall()
    for s in schools:
        print(f"ID: {s['school_id']}, Name: '{s['school_name']}', User: {s['username']}")
        
    print("\n--- School Settings ---")
    cur.execute("SELECT * FROM school_settings")
    settings = cur.fetchall()
    for s in settings:
        print(f"School ID: {s['school_id']}, Name: '{s['school_name']}', Address: '{s['school_address']}', Phone: '{s['school_phone']}'")
        
    conn.close()

if __name__ == "__main__":
    check_settings()
