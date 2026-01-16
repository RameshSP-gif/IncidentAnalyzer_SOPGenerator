"""Quick test script to import CSV data"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database.mongodb import MongoDBClient

def main():
    print("\n" + "="*60)
    print("Testing CSV Import to MongoDB")
    print("="*60 + "\n")
    
    # Create MongoDB client
    db_client = MongoDBClient(
        connection_string="mongodb://localhost:27017/",
        database_name="incident_analyzer"
    )
    
    # Import CSV
    csv_file = "sample_incidents.csv"
    print(f"Importing from: {csv_file}")
    
    result = db_client.import_from_csv(csv_file)
    
    print(f"\n✅ Import Results:")
    print(f"   - Imported: {result.get('imported', 0)} incidents")
    print(f"   - Skipped: {result.get('skipped', 0)} incidents")
    print(f"   - Errors: {result.get('errors', 0)} incidents")
    print(f"   - Total processed: {result.get('total', 0)} rows")
    
    # Get total count
    total = db_client.get_incident_count()
    print(f"\n📊 Total incidents in database: {total}")
    
    # Get some sample incidents
    print(f"\n📋 Sample incidents:")
    incidents = db_client.get_all_incidents(limit=3)
    for inc in incidents:
        print(f"   - {inc.get('number')}: {inc.get('short_description')}")
        print(f"     Created: {inc.get('sys_created_on')}")
        print(f"     Resolved: {inc.get('resolved_at')}")
    
    db_client.close()
    print("\n✅ Import test completed successfully!")

if __name__ == "__main__":
    main()
