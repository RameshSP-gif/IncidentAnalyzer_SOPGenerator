"""
Test CSV to MongoDB field mapping
Verifies that all fields from CSV are correctly imported and displayed
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from database import get_db_client
import json

def test_field_mapping():
    """Test that all CSV fields are properly mapped in MongoDB"""
    
    print("="*80)
    print("TESTING FIELD MAPPING - CSV to MongoDB")
    print("="*80)
    
    # Get MongoDB client
    db = get_db_client()
    
    # Get a few sample incidents
    incidents = db.get_all_incidents(limit=3)
    
    if not incidents:
        print("\n❌ No incidents found in database!")
        print("Please import incidents first using: python import_csv.py incidents.csv")
        return False
    
    print(f"\n✅ Found {len(incidents)} incidents in database")
    print("\n" + "="*80)
    print("CHECKING FIELD PRESENCE AND CONTENT")
    print("="*80)
    
    # Expected fields from CSV
    expected_fields = [
        'number', 'short_description', 'description', 
        'contact_type', 'service_offering', 'priority',
        'state', 'resolution_notes', 'closed_by',
        'assignment_group', 'assigned_to', 'sys_created_on',
        'sys_updated_on', 'resolved_at'
    ]
    
    for idx, incident in enumerate(incidents, 1):
        print(f"\n{'='*80}")
        print(f"INCIDENT #{idx}: {incident.get('number', 'NO NUMBER')}")
        print(f"{'='*80}")
        
        # Check each expected field
        for field in expected_fields:
            value = incident.get(field, '')
            status = "✅" if value else "❌"
            
            # Show field value (truncated if too long)
            if value:
                display_value = str(value)[:100]
                if len(str(value)) > 100:
                    display_value += "..."
                print(f"{status} {field:20s}: {display_value}")
            else:
                print(f"{status} {field:20s}: [EMPTY]")
        
        # Special check for resolution_notes
        resolution = incident.get('resolution_notes', '')
        print(f"\n{'='*80}")
        if resolution and len(resolution) > 10:
            print(f"✅ RESOLUTION_NOTES HAS CONTENT ({len(resolution)} chars)")
            print(f"First 200 chars: {resolution[:200]}")
        elif resolution:
            print(f"⚠️  RESOLUTION_NOTES EXISTS BUT TOO SHORT ({len(resolution)} chars)")
            print(f"Content: {resolution}")
        else:
            print(f"❌ RESOLUTION_NOTES IS EMPTY!")
    
    print(f"\n{'='*80}")
    print("FIELD MAPPING TEST COMPLETE")
    print(f"{'='*80}")
    
    # Summary
    print("\n📊 SUMMARY:")
    all_have_resolution = all(
        inc.get('resolution_notes') and len(inc.get('resolution_notes', '')) > 10 
        for inc in incidents
    )
    
    if all_have_resolution:
        print("✅ All sampled incidents have proper resolution_notes from CSV")
    else:
        print("❌ Some incidents are missing or have incomplete resolution_notes")
    
    return all_have_resolution


if __name__ == "__main__":
    success = test_field_mapping()
    sys.exit(0 if success else 1)
