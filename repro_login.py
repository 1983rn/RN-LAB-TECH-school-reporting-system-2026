from app_minimal import app

with app.test_client() as c:
    try:
        resp = c.get('/login')
        print('STATUS:', resp.status_code)
        print('DATA:', resp.data.decode('utf-8')[:500])
    except Exception as e:
        import traceback
        print('EXCEPTION:', e)
        traceback.print_exc()