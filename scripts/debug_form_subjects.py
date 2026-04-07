from app import app as flask_app
from school_database import SchoolDatabase

with flask_app.test_client() as client:
    # pick first school
    db = SchoolDatabase()
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT school_id FROM schools LIMIT 1")
        row = cursor.fetchone()
    if not row:
        print("No school found in DB")
        raise SystemExit(1)
    school_id = row[0]

    with client.session_transaction() as sess:
        sess['user_id'] = school_id
        sess['user_type'] = 'school'
        sess['days_remaining'] = 365

    rv = client.get('/form/1')
    print('Status:', rv.status_code)
    body = rv.get_data(as_text=True)
    # print subject headers
    import re
    headers = re.findall(r'<th[^>]*class="subject-column"[^>]*>\s*([^<]+?)\s*</th>', body)
    print('Found headers:', headers)
    for s in ['Business Studies', 'Home Economics']:
        print(s, 'in page?', s in body)

    # Also print the subjects variable presence near header
    m = re.search(r'<th[^>]*class="subject-column"[^>]*>([^<]+?)</th>', body)
    if m:
        print('First subject header sample:', m.group(1))
