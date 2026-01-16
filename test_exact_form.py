#!/usr/bin/env python3
"""Test with exact data from user's screenshot"""
import requests
import json

# Exact data from the screenshot
test_data = {
    "incident_number": "INC0001234",
    "category": "Other",
    "priority": "3",
    "short_description": "ISELL ORDER 483444667 NEEDS TO BE MARKED AS DELIVERED BY ANOTHER CARRIER",
    "description": "THIS ISELL ORDER IS SHOWING DELIVERED 12/3/25 BUT IT WAS NOT DELIVERED BY NAL IT NEEDS TO BE MARKED DELIVERED BY ANOTHER CARRIER. IT WAS DELIVERED BY DOLLY ON 12/3/25. WOULD YOU PLEASE ASSIST US? Variables: ------------------ Requested By: Holly Barlin Requested For: Holly Barlin Keep Informed: Christina Gallego, Isaih Stewart Title: ISELL ORDER 483444667 NEEDS TO BE MARKED AS ANOTHER CARRIER Description: THIS ISELL ORDER IS SHOWING DELIVERED 12/3/25 BUT IT WAS NOT DELIVERED BY NAL IT NEEDS TO BE MARKED DELIVERED BY ANOTHER CARRIER. IT WAS DELIVERED BY DOLLY ON 12/3/25. WOULD YOU PLEASE ASSIST US? Impact: My team (issue affects multiple people I work with) Urgency: Important, but can continue working",
    "resolution_notes": "Issue Description (in short) : ISELL ORDER 483444667 NEEDS TO BE MARKED AS DELIVERED BY ANOTHER CARRIER\nResolution Confirmation : The second-level support team has provided resolution."
}

print("Testing /analyze_single with exact form data...")
print(f"\nResolution notes length: {len(test_data['resolution_notes'])} characters")
print(f"Description length: {len(test_data['description'])} characters")

try:
    response = requests.post(
        'http://127.0.0.1:5000/analyze_single',
        json=test_data,
        headers={'Content-Type': 'application/json'},
        timeout=30
    )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("SUCCESS - SOP Generated!")
            print(f"SOP Length: {len(data.get('sop', ''))} characters")
            print(f"\nFirst 300 characters of SOP:")
            print("-" * 60)
            print(data.get('sop', '')[:300])
            print("-" * 60)
        else:
            print("FAILED - API returned success=False")
            print(f"Errors: {data.get('errors')}")
    else:
        print(f"HTTP ERROR {response.status_code}")
        try:
            error_data = response.json()
            print(f"Error details: {json.dumps(error_data, indent=2)}")
        except:
            print(f"Response text: {response.text[:500]}")
            
except Exception as e:
    print(f"ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
