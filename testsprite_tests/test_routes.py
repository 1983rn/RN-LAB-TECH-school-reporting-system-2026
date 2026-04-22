import pytest
from flask import session

def test_protected_routes_unauthenticated(client):
    """Test that protected routes redirect to login when unauthenticated."""
    protected_routes = [
        '/',
        '/form/1',
        '/ranking-analysis',
        '/top-performers',
        '/reports',
        '/settings'
    ]
    for route in protected_routes:
        response = client.get(route)
        assert response.status_code == 302
        assert '/login' in response.headers.get('Location', '')

def test_dashboard_authenticated(auth_client):
    """Test that dashboard loads for authenticated users."""
    response = auth_client.get('/')
    assert response.status_code == 200
    assert b'Form 1' in response.data or b'dashboard' in response.data.lower()

def test_data_entry_page(auth_client):
    """Test that data entry page loads."""
    response = auth_client.get('/form/1')
    assert response.status_code == 200
    assert b'Student' in response.data or b'marks' in response.data.lower()

def test_rankings_page(auth_client):
    """Test that rankings page loads and has required filters."""
    response = auth_client.get('/ranking-analysis')
    assert response.status_code == 200
    # Assuming standard HTML select for terms
    assert b'Term 1' in response.data or b'term' in response.data.lower()

def test_api_unauthorized_access(client):
    """Test API routes block unauthenticated access."""
    response = client.post('/api/save-student-marks', json={})
    assert response.status_code == 403
