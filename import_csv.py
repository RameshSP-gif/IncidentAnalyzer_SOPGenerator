"""
CSV Import Utility

Provides command-line interface for importing incidents from CSV to MongoDB.
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database import get_db_client
from loguru import logger


def import_csv_to_mongodb(csv_file: str, connection_string: str = None):
    """
    Import incidents from CSV file to MongoDB
    
    Args:
        csv_file: Path to CSV file
        connection_string: MongoDB connection string (optional)
    """
    # Initialize database client
    db_client = get_db_client(connection_string=connection_string)
    
    logger.info(f"Starting CSV import from: {csv_file}")
    
    # Import from CSV
    result = db_client.import_from_csv(csv_file)
    
    # Display results
    print("\n" + "="*60)
    print("CSV IMPORT RESULTS")
    print("="*60)
    print(f"Total Records: {result.get('total', 0)}")
    print(f"Successfully Imported: {result.get('imported', 0)}")
    print(f"Skipped (duplicates): {result.get('skipped', 0)}")
    print(f"Errors: {result.get('errors', 0)}")
    
    if 'error_message' in result:
        print(f"\nError Message: {result['error_message']}")
    
    print("="*60)
    
    # Display database stats
    total_count = db_client.get_incident_count()
    print(f"\nTotal Incidents in Database: {total_count}")
    
    categories = db_client.get_categories()
    print(f"Categories: {', '.join(categories) if categories else 'None'}")
    print()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Import incidents from CSV to MongoDB"
    )
    parser.add_argument(
        'csv_file',
        help="Path to CSV file containing incident data"
    )
    parser.add_argument(
        '--connection-string',
        default=None,
        help="MongoDB connection string (default: mongodb://localhost:27017/)"
    )
    parser.add_argument(
        '--database',
        default="incident_analyzer",
        help="Database name (default: incident_analyzer)"
    )
    
    args = parser.parse_args()
    
    # Check if file exists
    if not Path(args.csv_file).exists():
        print(f"Error: File not found: {args.csv_file}")
        sys.exit(1)
    
    try:
        import_csv_to_mongodb(args.csv_file, args.connection_string)
    except Exception as e:
        logger.error(f"Import failed: {e}")
        print(f"\nImport failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
