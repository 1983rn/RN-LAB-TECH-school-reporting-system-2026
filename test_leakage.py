import psycopg2
import os
import json
from school_database import SchoolDatabase, DEFAULT_DATABASE_URL

def test_leakage():
    db_url = os.environ.get('DATABASE_URL', DEFAULT_DATABASE_URL)
    db = SchoolDatabase()
    
    # Create two test schools if they don't exist
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    # Clean up old test data
    cur.execute("DELETE FROM schools WHERE username IN ('test_school_a', 'test_school_b')")
    cur.execute("DELETE FROM school_settings WHERE school_id IN (SELECT school_id FROM schools WHERE username IN ('test_school_a', 'test_school_b'))")
    conn.commit()
    
    # Add School A
    cur.execute("INSERT INTO schools (school_name, username, password_hash) VALUES ('School A', 'test_school_a', 'hash') RETURNING school_id")
    id_a = cur.fetchone()[0]
    
    # Add School B
    cur.execute("INSERT INTO schools (school_name, username, password_hash) VALUES ('School B', 'test_school_b', 'hash') RETURNING school_id")
    id_b = cur.fetchone()[0]
    conn.commit()
    
    print(f"Created School A (ID: {id_a}) and School B (ID: {id_b})")
    
    # Initialize settings for both (should happen automatically but let's be sure)
    db.update_school_settings({'school_name': 'Original A'}, id_a)
    db.update_school_settings({'school_name': 'Original B'}, id_b)
    
    print(f"Initial Settings A: {db.get_school_settings(id_a)['school_name']}")
    print(f"Initial Settings B: {db.get_school_settings(id_b)['school_name']}")
    
    # Update School A's settings
    print("\nUpdating School A's name to 'New Name A'...")
    db.update_school_settings({'school_name': 'New Name A'}, id_a)
    
    # Check both
    name_a = db.get_school_settings(id_a)['school_name']
    name_b = db.get_school_settings(id_b)['school_name']
    
    print(f"Settings A after update: {name_a}")
    print(f"Settings B after update: {name_b}")
    
    if name_b == 'New Name A':
        print("\n!!! LEAKAGE DETECTED !!!")
    else:
        print("\nNo leakage detected between School A and School B.")
        
    cur.close()
    conn.close()

if __name__ == "__main__":
    test_leakage()
