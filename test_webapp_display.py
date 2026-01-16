"""
Test Web App Field Display
Tests that web app properly displays all MongoDB fields including resolution_notes
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from database import get_db_client
import json

def test_web_app_display():
    """Test that web app receives correct data from MongoDB"""
    
    print("="*80)
    print("TESTING WEB APP DATA FLOW")
    print("="*80)
    
    # Get MongoDB client (same as web_app.py uses)
    db = get_db_client()
    
    # Test 1: Get incidents like web app does
    print("\n📋 Test 1: Getting incidents from MongoDB (like web app)")
    incidents = db.get_all_incidents(limit=2)
    
    for idx, incident in enumerate(incidents, 1):
        print(f"\n{'='*60}")
        print(f"Incident #{idx}: {incident.get('number')}")
        print(f"{'='*60}")
        print(f"Short Description: {incident.get('short_description', '')[:80]}...")
        
        resolution = incident.get('resolution_notes', '')
        if resolution:
            print(f"✅ Resolution Notes ({len(resolution)} chars):")
            print(f"   {resolution[:150]}...")
        else:
            print(f"❌ Resolution Notes: EMPTY")
    
    # Test 2: Simulate what happens in analyze_single endpoint
    print(f"\n{'='*80}")
    print("📋 Test 2: Simulating analyze_single endpoint logic")
    print(f"{'='*80}")
    
    test_incident = incidents[0]
    print(f"\nOriginal resolution_notes from MongoDB:")
    print(f"Length: {len(test_incident.get('resolution_notes', ''))} chars")
    print(f"Content: {test_incident.get('resolution_notes', '')[:200]}...")
    
    # Check the condition from web_app.py line 582
    resolution = test_incident.get('resolution_notes', '')
    print(f"\nCondition check:")
    print(f"  - resolution_notes exists: {bool(resolution)}")
    print(f"  - length > 10: {len(resolution) > 10}")
    print(f"  - stripped length: {len(resolution.strip())}")
    
    # This is what should NOT happen anymore
    if not resolution:
        print(f"\n❌ WOULD ADD DUMMY TEXT (resolution empty)")
    else:
        print(f"\n✅ KEEPING ORIGINAL RESOLUTION (not empty)")
    
    print(f"\n{'='*80}")
    print("TEST COMPLETE")
    print(f"{'='*80}")
    
    return True

if __name__ == "__main__":
    test_web_app_display()
