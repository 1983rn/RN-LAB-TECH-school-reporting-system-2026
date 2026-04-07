from app import app


def test_app_health_endpoint():
    client = app.test_client()
    rv = client.get('/health')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data.get('status') == 'ok'
