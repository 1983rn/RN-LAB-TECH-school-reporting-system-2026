from app import app as flask_app
from school_database import SchoolDatabase
import re

# Get a school id
db = SchoolDatabase()
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT school_id FROM schools LIMIT 1")
    row = cursor.fetchone()
if not row:
    print('No school found in DB')
    raise SystemExit(1)
school_id = row[0]

client = flask_app.test_client()
with client.session_transaction() as sess:
    sess['user_id'] = school_id
    sess['user_type'] = 'school'
    sess['days_remaining'] = 365

rv = client.get('/form/1')
print('Status:', rv.status_code)
body = rv.get_data(as_text=True)
# print body trimmed
start = body.find('<thead')
end = body.find('</thead>')
print(body[start:end+8])

headers = re.findall(r'<th[^>]*class="subject-column"[^>]*>\s*([^<]+?)\s*</th>', body)
print('Subjects headers found:', headers)

# Also search for the exact strings
for s in ['Business Studies', 'Home Economics']:
    print(s, 'in page?', s in body)
