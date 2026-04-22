
import psycopg2
import os


def load_env_file():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(base_dir, '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()

def check_schema():
    load_env_file()
    dsn = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/school_reports')

    try:
        conn = psycopg2.connect(dsn)
        cur = conn.cursor()
        
        tables = ['students', 'student_marks', 'student_term_enrollment']
        for table in tables:
            print(f"\nTable: {table}")
            cur.execute(f"SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = '{table}' ORDER BY ordinal_position")
            for row in cur.fetchall():
                print(f"  {row[0]}: {row[1]} (Nullable: {row[2]})")
                
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()
