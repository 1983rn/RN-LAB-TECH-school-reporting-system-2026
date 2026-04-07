#!/usr/bin/env python3
"""
Test the API endpoint directly to see what's being returned
"""

import requests
import json

def test_api_endpoint():
    """Test the /api/get-top-performers endpoint"""
    url = "http://localhost:5000/api/get-top-performers"
    
    test_data = {
        "category": "overall",
        "form_level": 1,
        "term": "Term 1",
        "academic_year": "2024-2025"
    }
    
    print("=== TESTING API ENDPOINT ===")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(url, json=test_data)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nResponse Data:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Error Response: {response.text}")
            
    except Exception as e:
        print(f"Error making request: {e}")

if __name__ == "__main__":
    test_api_endpoint()
