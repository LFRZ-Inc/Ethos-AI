#!/usr/bin/env python3
"""
Test script to verify CORS configuration is working
"""

import requests
import json

def test_cors():
    """Test CORS configuration on the Railway backend"""
    
    # Railway backend URL
    base_url = "https://cooking-ethos-ai-production-6bfd.up.railway.app"
    
    # Test endpoints
    endpoints = [
        "/health",
        "/",
        "/test",
        "/api/models"
    ]
    
    print("Testing CORS configuration...")
    print(f"Backend URL: {base_url}")
    print("-" * 50)
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\nTesting: {endpoint}")
        
        try:
            # Test GET request
            response = requests.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            # Check for CORS headers
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            print(f"CORS Headers: {cors_headers}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"Response: {json.dumps(data, indent=2)}")
                except:
                    print(f"Response: {response.text[:200]}...")
            else:
                print(f"Error: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_cors()
