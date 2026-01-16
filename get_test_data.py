"""
Extract test data from MongoDB for testing incident analyzer
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database import get_db_client

def get_test_incidents():
    """Get sample incidents from MongoDB for testing"""
    
    db_client = get_db_client()
    
    print("\n" + "="*80)
    print("TEST INCIDENTS FROM MONGODB")
    print("="*80)
    print(f"\nTotal incidents in database: {db_client.get_incident_count()}")
    print(f"Categories: {', '.join(db_client.get_categories()[:10])}")
    
    # Get some random incidents with good descriptions
    incidents = db_client.get_all_incidents(limit=20)
    
    print("\n" + "="*80)
    print("SAMPLE INCIDENTS FOR TESTING:")
    print("="*80)
    
    test_cases = []
    for i, inc in enumerate(incidents[:10], 1):
        short_desc = inc.get('short_description', '')[:100]
        description = inc.get('description', '')[:200]
        category = inc.get('category', 'General')
        resolution = inc.get('resolution_notes', '')[:150]
        
        if len(description) > 30:  # Only incidents with decent descriptions
            test_cases.append({
                'number': inc.get('number', 'Unknown'),
                'short_desc': short_desc,
                'description': description,
                'category': category,
                'has_resolution': bool(resolution)
            })
            
            print(f"\n--- Test Case {i} ---")
            print(f"Incident: {inc.get('number', 'Unknown')}")
            print(f"Category: {category}")
            print(f"Short Description: {short_desc}")
            print(f"Description: {description}")
            if resolution:
                print(f"Resolution: {resolution}")
            else:
                print(f"Resolution: (None - will use similar incidents)")
            print("-" * 40)
    
    print("\n" + "="*80)
    print("HOW TO TEST:")
    print("="*80)
    print("1. Go to: http://127.0.0.1:5000")
    print("2. Copy any 'Short Description' and 'Description' from above")
    print("3. Paste into the incident form")
    print("4. Select matching Category")
    print("5. Click 'AI Suggest Resolution' button")
    print("6. System will find similar incidents and suggest resolution")
    print("="*80)
    
    return test_cases

if __name__ == "__main__":
    try:
        get_test_incidents()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure MongoDB is running and the application has data imported.")
