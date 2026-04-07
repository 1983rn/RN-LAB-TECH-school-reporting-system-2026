#!/usr/bin/env python3
"""
Test the API endpoint with authentication
"""

from app import app


def test_with_authentication():
    """Test the API with proper authentication using Flask test client"""
    login_data = {
        "username": "MAKONOKAya",
        "password": "NAMADEYIMKOLOWEKO1949",
        "user_type": "developer"
    }

    with app.test_client() as client:
        # Login
        login_response = client.post('/api/login', json=login_data)
        assert login_response.status_code == 200
        login_result = login_response.get_json()
        assert login_result.get('success') is True

        # Test top performers API
        test_data = {
            "category": "overall",
            "form_level": 1,
            "term": "Term 1",
            "academic_year": "2024-2025"
        }

        api_response = client.post('/api/get-top-performers', json=test_data)
        assert api_response.status_code == 200
        data = api_response.get_json()
        assert data.get('success') in (True, False)
