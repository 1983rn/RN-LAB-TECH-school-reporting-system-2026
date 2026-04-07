from app_minimal import app as minimal_app


def test_health_endpoint():
    client = minimal_app.test_client()
    rv = client.get('/health')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data.get('status') == 'ok'
    assert 'service' in data
