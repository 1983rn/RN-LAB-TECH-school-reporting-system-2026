from app_minimal import app

with app.test_client() as c:
    r = c.get('/login')
    print('/login ->', r.status_code)
    r2 = c.get('/_debug/template-check')
    print('/_debug/template-check ->', r2.status_code)
    print('template-check data (first 400 chars):')
    print(r2.data.decode('utf-8')[:400])
