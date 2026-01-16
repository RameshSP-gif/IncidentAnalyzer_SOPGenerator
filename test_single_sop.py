#!/usr/bin/env python3
"""Test the single incident SOP generation endpoint"""
import requests
import json

# Test data matching the screenshot
test_data = {
    "incident_number": "INC0001234",
    "category": "Other",
    "priority": "3",
    "short_description": "ISELL ORDER 483444667 NEEDS TO BE MARKED AS DELIVERED BY ANOTHER CARRIER",
    "description": """THIS ISELL ORDER IS SHOWING DELIVERED 12/3/25 BUT IT WAS NOT DELIVERED BY NAL IT NEEDS TO BE MARKED DELIVERED BY ANOTHER CARRIER. IT WAS DELIVERED BY DOLLY ON 12/3/25. WOULD YOU PLEASE ASSIST US? Variables: ------------------ Requested By: Holly Barlin Requested For: Holly Barlin Keep Informed: Christina Gallego, Isaih Stewart Title: ISELL ORDER 483444667 NEEDS TO BE MARKED AS ANOTHER CARRIER Description: THIS ISELL ORDER IS SHOWING DELIVERED 12/3/25 BUT IT WAS NOT DELIVERED BY NAL IT NEEDS TO BE MARKED DELIVERED BY ANOTHER CARRIER. IT WAS DELIVERED BY DOLLY ON 12/3/25. WOULD YOU PLEASE ASSIST US?""",
    "resolution_notes": """Issue Description (in short) : ISELL ORDER 483444667 NEEDS TO BE MARKED AS DELIVERED BY ANOTHER CARRIER
Resolution Confirmation : The second-level support team has provided resolution."""
}

print("Testing /analyze_single endpoint...")
print(f"URL: http://127.0.0.1:5000/analyze_single")
print(f"\nSending data:")
print(json.dumps(test_data, indent=2))

try:
    response = requests.post(
        'http://127.0.0.1:5000/analyze_single',
        json=test_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"\n{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"{'='*60}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ SUCCESS!")
        print(f"\nResponse Keys: {list(data.keys())}")
        
        if data.get('success'):
            print(f"\nSOP Content Preview (first 500 chars):")
            print(f"{'-'*60}")
            sop_preview = data.get('sop', '')[:500]
            print(sop_preview)
            print(f"{'-'*60}")
            print(f"\nTotal SOP Length: {len(data.get('sop', ''))} characters")
        else:
            print(f"\n❌ API returned success=False")
            print(f"Errors: {data.get('errors', [])}")
            print(f"Error: {data.get('error', 'Unknown')}")
    else:
        print(f"\n❌ HTTP Error {response.status_code}")
        try:
            error_data = response.json()
            print(f"Error response: {json.dumps(error_data, indent=2)}")
        except:
            print(f"Response text: {response.text[:500]}")
            
except requests.exceptions.ConnectionError:
    print("\n❌ CONNECTION ERROR!")
    print("Flask server is not running at http://127.0.0.1:5000")
    print("Please start the server with: python web_app.py")
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
