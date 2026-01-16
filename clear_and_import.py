"""
Clear MongoDB and Import New CSV Data

This script will:
1. Delete all existing incidents from MongoDB
2. Import all incidents from the new CSV file
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database import get_db_client
from loguru import logger


def clear_and_import(csv_file: str):
    """
    Clear database and import new CSV file
    
    Args:
        csv_file: Path to CSV file
    """
    print("\n" + "="*70)
    print("DATABASE REPLACEMENT OPERATION")
    print("="*70)
    print(f"CSV File: {csv_file}")
    print()
    
    # Initialize database client
    db_client = get_db_client()
    
    # Step 1: Show current database stats
    current_count = db_client.get_incident_count()
    print(f"Current incidents in database: {current_count}")
    print()
    
    # Step 2: Confirm deletion
    print("⚠️  WARNING: This will DELETE ALL existing incidents!")
    response = input("Type 'YES' to confirm deletion and proceed: ")
    
    if response.strip().upper() != 'YES':
        print("\n❌ Operation cancelled by user.")
        return
    
    print()
    print("="*70)
    print("STEP 1: Deleting all existing incidents...")
    print("="*70)
    
    # Delete all incidents
    deleted_count = db_client.delete_all_incidents()
    print(f"✓ Deleted {deleted_count} incidents")
    print()
    
    # Step 3: Import new data
    print("="*70)
    print("STEP 2: Importing new CSV data...")
    print("="*70)
    
    logger.info(f"Starting CSV import from: {csv_file}")
    
    # Import from CSV
    result = db_client.import_from_csv(csv_file)
    
    # Display results
    print("\n" + "="*70)
    print("IMPORT RESULTS")
    print("="*70)
    print(f"Total Records Processed: {result.get('total', 0)}")
    print(f"Successfully Imported: {result.get('imported', 0)}")
    print(f"Skipped (duplicates): {result.get('skipped', 0)}")
    print(f"Errors: {result.get('errors', 0)}")
    
    if 'error_message' in result:
        print(f"\nError Message: {result['error_message']}")
    
    print("="*70)
    
    # Display final database stats
    final_count = db_client.get_incident_count()
    print(f"\n✓ Total Incidents in Database: {final_count}")
    
    categories = db_client.get_categories()
    print(f"✓ Categories: {', '.join(categories) if categories else 'None'}")
    
    # Show sample incident
    print("\n" + "="*70)
    print("SAMPLE INCIDENT FROM DATABASE")
    print("="*70)
    
    sample = db_client.collection.find_one({}, {'_id': 0})
    if sample:
        print(f"Number: {sample.get('number')}")
        print(f"Short Description: {sample.get('short_description', '')[:80]}")
        print(f"Contact Type: {sample.get('contact_type', 'N/A')}")
        print(f"Service Offering: {sample.get('service_offering', 'N/A')}")
        print(f"Priority: {sample.get('priority', 'N/A')}")
        print(f"State: {sample.get('state', 'N/A')}")
        print(f"Assignment Group: {sample.get('assignment_group', 'N/A')}")
        print(f"Assigned To: {sample.get('assigned_to', 'N/A')}")
        print(f"Closed By: {sample.get('closed_by', 'N/A')}")
        print(f"Created: {sample.get('sys_created_on', 'N/A')}")
        print(f"Updated: {sample.get('sys_updated_on', 'N/A')}")
        print(f"Resolved: {sample.get('resolved_at', 'N/A')}")
        resolution = sample.get('resolution_notes', '')
        if resolution:
            print(f"Resolution Notes: {resolution[:200]}...")
    
    print("\n" + "="*70)
    print("✅ DATABASE REPLACEMENT COMPLETED SUCCESSFULLY!")
    print("="*70)
    print()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Clear MongoDB and import new CSV data"
    )
    parser.add_argument(
        'csv_file',
        help="Path to CSV file containing incident data"
    )
    
    args = parser.parse_args()
    
    # Check if file exists
    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        print(f"Error: File not found: {args.csv_file}")
        sys.exit(1)
    
    print(f"\n📊 CSV File Size: {csv_path.stat().st_size / (1024*1024):.2f} MB")
    
    try:
        clear_and_import(args.csv_file)
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        print(f"\n❌ Operation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
