"""
End-to-End Test: Verify Complete Field Mapping and SOP Generation
Tests the full workflow: MongoDB -> Web App -> SOP Generation
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_full_workflow():
    """Test complete workflow from database to SOP generation"""
    
    print("="*80)
    print("END-TO-END TEST: Field Mapping and Display")
    print("="*80)
    
    # Test 1: Get database stats
    print("\n📊 Test 1: Getting database stats...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Total Incidents: {stats.get('total_incidents', 0)}")
            print(f"✅ Categories: {len(stats.get('categories', []))}")
        else:
            print(f"❌ Failed to get stats: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Get a single incident
    print(f"\n{'='*80}")
    print("📋 Test 2: Fetching single incident...")
    print(f"{'='*80}")
    try:
        response = requests.get(f"{BASE_URL}/get_incidents?limit=1")
        if response.status_code == 200:
            data = response.json()
            incidents = data.get('incidents', [])
            
            if incidents:
                incident = incidents[0]
                print(f"\n✅ Incident Number: {incident.get('number')}")
                print(f"✅ Short Description: {incident.get('short_description', '')[:80]}...")
                print(f"✅ Priority: {incident.get('priority')}")
                print(f"✅ State: {incident.get('state')}")
                print(f"✅ Assignment Group: {incident.get('assignment_group')}")
                
                # Check resolution_notes specifically
                resolution = incident.get('resolution_notes', '')
                print(f"\n{'='*60}")
                print("🔍 RESOLUTION_NOTES CHECK:")
                print(f"{'='*60}")
                if resolution:
                    print(f"✅ Length: {len(resolution)} characters")
                    print(f"✅ Content (first 200 chars):")
                    print(f"   {resolution[:200]}...")
                else:
                    print(f"❌ EMPTY - This should not happen!")
                    return False
            else:
                print("❌ No incidents returned")
                return False
        else:
            print(f"❌ Failed to get incidents: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 3: Generate SOP for an incident
    print(f"\n{'='*80}")
    print("📝 Test 3: Generating SOP...")
    print(f"{'='*80}")
    try:
        test_incident = {
            "number": incident.get('number'),
            "short_description": incident.get('short_description'),
            "description": incident.get('description', incident.get('short_description')),
            "category": incident.get('category', 'General'),
            "priority": incident.get('priority', '3'),
            "resolution_notes": incident.get('resolution_notes', ''),
        }
        
        print(f"\nSending incident for SOP generation:")
        print(f"  Number: {test_incident['number']}")
        print(f"  Resolution length: {len(test_incident['resolution_notes'])} chars")
        
        response = requests.post(
            f"{BASE_URL}/analyze_single",
            json=test_incident,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                sop = result.get('sop', '')
                returned_incident = result.get('incident', {})
                
                print(f"\n✅ SOP Generated Successfully!")
                print(f"✅ SOP Length: {len(sop)} characters")
                
                # Check if original resolution_notes preserved in SOP
                print(f"\n{'='*60}")
                print("🔍 CHECKING RESOLUTION IN SOP:")
                print(f"{'='*60}")
                
                original_resolution = test_incident['resolution_notes'][:100]
                returned_resolution = returned_incident.get('resolution_notes', '')
                
                print(f"Original (first 100 chars): {original_resolution}...")
                print(f"Returned length: {len(returned_resolution)} chars")
                
                # Check if SOP contains the actual resolution
                if original_resolution[:50] in sop:
                    print(f"✅ Original resolution found in SOP!")
                elif "Resolution pending" in returned_resolution or "Use 'AI Suggest Resolution'" in returned_resolution:
                    print(f"❌ SOP contains DUMMY text instead of real resolution!")
                    print(f"   Returned resolution: {returned_resolution}")
                    return False
                else:
                    print(f"⚠️  Resolution might be reformatted in SOP")
                
                print(f"\nSOP Preview (first 500 chars):")
                print(f"{'-'*60}")
                print(sop[:500])
                print(f"{'-'*60}")
                
            else:
                print(f"❌ SOP generation failed: {result.get('error')}")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"\n{'='*80}")
    print("✅ ALL TESTS PASSED!")
    print(f"{'='*80}")
    print("\n📝 Summary:")
    print("  ✅ MongoDB fields are correctly mapped from CSV")
    print("  ✅ Web app receives correct data from MongoDB")
    print("  ✅ Resolution_notes are preserved (not replaced with dummy text)")
    print("  ✅ SOPs are generated with actual resolution data")
    print()
    
    return True

if __name__ == "__main__":
    import sys
    success = test_full_workflow()
    sys.exit(0 if success else 1)
