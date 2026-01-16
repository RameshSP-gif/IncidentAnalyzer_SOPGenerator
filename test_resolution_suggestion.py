#!/usr/bin/env python3
"""
Quick test of resolution suggestion endpoint
"""
import requests
import json

url = "http://127.0.0.1:5000/suggest_resolution"

test_data = {
    "short_description": "Antivirus update failed",
    "description": "Antivirus definitions not updating",
    "category": "Software"
}

print("Testing resolution suggestion endpoint...")
print(f"URL: {url}")
print(f"Request: {json.dumps(test_data, indent=2)}")
print("\nSending request...")

try:
    response = requests.post(url, json=test_data, timeout=10)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"\n✓ SUCCESS! Resolution suggested:")
            print(f"  Confidence: {data.get('confidence')}%")
            print(f"  Source: {data.get('primary_source', {}).get('number')}")
            print(f"  Resolution: {data.get('suggested_resolution')[:100]}...")
        else:
            print(f"\n✗ No match found: {data.get('message')}")
    else:
        print(f"\n✗ Error: Status {response.status_code}")
        
except Exception as e:
    print(f"\n✗ Exception: {e}")
    import traceback
    traceback.print_exc()
