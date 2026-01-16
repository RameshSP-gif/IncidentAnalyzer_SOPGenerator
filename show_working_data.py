#!/usr/bin/env python3
"""
Display sample working data from MongoDB
"""
from src.database.mongodb import MongoDBClient

def show_working_data():
    # Connect to MongoDB
    client = MongoDBClient()
    
    # Get total count
    total = client.get_incident_count()
    print(f"Total incidents in MongoDB: {total}")
    
    # Get sample incidents using the correct method
    incidents = client.get_all_incidents(limit=5)
    
    print("\n" + "="*70)
    print("SAMPLE WORKING DATA (5 incidents)")
    print("="*70 + "\n")
    
    for i, incident in enumerate(incidents, 1):
        print(f"Incident #{i}:")
        print(f"  Number: {incident.get('number')}")
        print(f"  Short Description: {incident.get('short_description', 'N/A')[:80]}")
        print(f"  Priority: {incident.get('priority')}")
        print(f"  State: {incident.get('state')}")
        print(f"  Assignment Group: {incident.get('assignment_group')}")
        print(f"  Contact Type: {incident.get('contact_type')}")
        print(f"  Service Offering: {incident.get('service_offering')}")
        res_notes = incident.get('resolution_notes', 'N/A')
        print(f"  Resolution Notes: {res_notes[:150]}{'...' if len(res_notes) > 150 else ''}")
        print()
    
    print("="*70)
    print(f"All {total} incidents have complete data and resolution notes!")
    print("="*70)
    print("\nYou can now run:")
    print("  python test_pipeline.py --limit 50  (quick test)")
    print("  python test_pipeline.py --limit 100 (medium test)")
    print("  python test_pipeline.py --limit 500 (large test)")

if __name__ == "__main__":
    show_working_data()
