"""
CSV Import Quick Test & Demo
Demonstrates the CSV import functionality
"""

import sys
from pathlib import Path
import csv
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.csv_importer import CSVIncidentImporter
from src.data_validation import DataValidator


def create_demo_csv():
    """Create a demo CSV file with sample incident data"""
    csv_file = Path(__file__).parent / 'demo_incidents.csv'
    
    sample_data = [
        {
            'Incident Number': 'INC0001234',
            'Short Description': 'Database connection timeout',
            'Description': 'Application unable to connect to primary database server. Users unable to log in or access data. Error message: "Connection timeout after 30 seconds". Affects all services.',
            'Category': 'Database',
            'Priority': '1',
            'Status': 'Closed',
            'Assignment Group': 'Database Team',
            'Assigned To': 'John Doe',
            'Resolution Notes': 'Root cause: Database service hung due to memory leak in connection pool. Fixed by: 1) Restarted database service 2) Applied latest patches 3) Implemented connection pooling with better resource management 4) Verified with load test. Status: Resolved and monitored.',
            'Created Date': '2024-01-15 09:30',
            'Resolved Date': '2024-01-15 14:45'
        },
        {
            'Incident Number': 'INC0001235',
            'Short Description': 'Email delivery failure',
            'Description': 'System unable to send email notifications. Queue is stuck with 500+ pending emails. Users report missing password reset emails and notifications. SMTP service shows connection refused errors.',
            'Category': 'Email',
            'Priority': '2',
            'Status': 'Closed',
            'Assignment Group': 'Application Team',
            'Assigned To': 'Jane Smith',
            'Resolution Notes': 'Issue identified: Email service crashed due to large attachment processing failure. Solution applied: 1) Cleared stuck mail queue manually 2) Restarted mail service 3) Increased timeout settings 4) Updated DNS MX records 5) Implemented queue monitoring. All pending emails resent successfully.',
            'Created Date': '2024-01-16 08:15',
            'Resolved Date': '2024-01-17 11:20'
        },
        {
            'Incident Number': 'INC0001236',
            'Short Description': 'Login page not responding',
            'Description': 'Users report that login page fails to load or times out after 60 seconds. Affects both web and mobile apps. API returns 503 Service Unavailable.',
            'Category': 'Authentication',
            'Priority': '1',
            'Status': 'Closed',
            'Assignment Group': 'Web Team',
            'Assigned To': 'Mike Johnson',
            'Resolution Notes': 'Root cause: Web server cache corrupted, SSL certificate expired on secondary server. Fixed by: 1) Cleared web server cache on all nodes 2) Restarted nginx processes 3) Updated and renewed SSL certificates 4) Verified HTTPS connectivity 5) Load tested. Performance restored.',
            'Created Date': '2024-01-17 07:00',
            'Resolved Date': '2024-01-17 09:30'
        },
        {
            'Incident Number': 'INC0001237',
            'Short Description': 'Report generation timeout',
            'Description': 'Monthly financial reports take over 90 minutes to generate, causing batch job failures. Users waiting for reports experience significant delays. Database queries show full table scans.',
            'Category': 'Reporting',
            'Priority': '3',
            'Status': 'Closed',
            'Assignment Group': 'Analytics Team',
            'Assigned To': 'Sarah Williams',
            'Resolution Notes': 'Performance issue: Missing database indexes on large transaction tables. Solution: 1) Analyzed slow query logs 2) Created indexes on transaction_date and account_id columns 3) Optimized report SQL queries 4) Implemented query result caching 5) Reduced generation time from 90min to 12min. Verified with historical data.',
            'Created Date': '2024-01-18 06:30',
            'Resolved Date': '2024-01-19 16:00'
        },
        {
            'Incident Number': 'INC0001238',
            'Short Description': 'API rate limit errors',
            'Description': 'Third-party integrations (Salesforce, Slack, Teams) receiving 429 rate limit errors. Integration fails after first 100 requests per minute. Causes data sync failures.',
            'Category': 'Integration',
            'Priority': '2',
            'Status': 'Closed',
            'Assignment Group': 'API Team',
            'Assigned To': 'Tom Brown',
            'Resolution Notes': 'Issue: Rate limits too restrictive, burst traffic not handled. Resolution: 1) Increased rate limit thresholds from 100 to 1000 req/min 2) Implemented request throttling with queue management 3) Added exponential backoff for retries 4) Optimized batch endpoints to reduce calls 5) Tested with simulated load. Integrations now stable.',
            'Created Date': '2024-01-19 10:00',
            'Resolved Date': '2024-01-20 15:30'
        },
        {
            'Incident Number': 'INC0001239',
            'Short Description': 'Payment processing delay',
            'Description': 'Credit card transactions taking 5-10 minutes to process instead of 30 seconds. Users unable to complete purchases. Payment gateway showing timeout errors.',
            'Category': 'Payment',
            'Priority': '1',
            'Status': 'Closed',
            'Assignment Group': 'Payment Team',
            'Assigned To': 'Lisa Chen',
            'Resolution Notes': 'Root cause: Payment gateway connection pooling exhausted, network latency to processor high. Fixed by: 1) Increased connection pool size from 20 to 100 2) Optimized network route to payment processor 3) Implemented connection keepalive 4) Added retry logic with exponential backoff 5) Deployed to all regions. Processing time now <1 second average.',
            'Created Date': '2024-01-20 09:15',
            'Resolved Date': '2024-01-20 13:45'
        }
    ]
    
    # Write CSV file
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = list(sample_data[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sample_data)
    
    print(f"✓ Demo CSV created: {csv_file}")
    return csv_file


def test_csv_import():
    """Test CSV import functionality"""
    
    print("\n" + "="*70)
    print("CSV IMPORT TEST")
    print("="*70 + "\n")
    
    # Create demo CSV
    csv_file = create_demo_csv()
    
    # Initialize validator
    validator = DataValidator(
        required_fields=["number", "short_description"],
        min_description_length=20,
        min_resolution_length=30
    )
    
    # Create importer
    print("Initializing CSV importer...")
    importer = CSVIncidentImporter(validator=validator)
    
    # Import from CSV
    print(f"\nImporting incidents from: {csv_file}")
    imported_incidents, errors, warnings = importer.import_from_csv(
        str(csv_file),
        skip_invalid=True
    )
    
    # Display results
    print("\n" + "-"*70)
    print("IMPORT RESULTS")
    print("-"*70)
    print(f"✓ Successfully imported: {len(imported_incidents)} incidents")
    print(f"⚠ Warnings: {len(warnings)}")
    print(f"❌ Errors: {len(errors)}")
    
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  • {w}")
    
    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  • {e}")
    
    # Display imported incidents
    print("\n" + "-"*70)
    print("IMPORTED INCIDENTS")
    print("-"*70)
    for inc in imported_incidents:
        print(f"\n▪ {inc.get('number', 'Unknown')} - {inc.get('short_description', 'No description')}")
        print(f"  Category: {inc.get('category', 'Unknown')}")
        print(f"  Has Resolution: {'Yes' if inc.get('resolution_notes') else 'No'}")
        if inc.get('resolution_notes'):
            res_preview = inc['resolution_notes'][:100] + ('...' if len(inc['resolution_notes']) > 100 else '')
            print(f"  Resolution: {res_preview}")
    
    # Test knowledge base update
    print("\n" + "-"*70)
    print("KNOWLEDGE BASE UPDATE TEST")
    print("-"*70)
    
    kb_file = Path(__file__).parent / 'data' / 'test_knowledge_base.json'
    print(f"\nAdding incidents to KB: {kb_file}")
    
    count_added, kb_errors = importer.add_to_knowledge_base(
        imported_incidents,
        str(kb_file)
    )
    
    print(f"✓ Added to KB: {count_added} incidents")
    if kb_errors:
        print(f"❌ KB Errors: {len(kb_errors)}")
        for e in kb_errors:
            print(f"  • {e}")
    
    # Display summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total incidents imported: {len(imported_incidents)}")
    print(f"Incidents added to KB: {count_added}")
    print(f"Ready for RAG suggestions: {count_added}")
    print("\nNext steps:")
    print("1. Run web_app.py to start the application")
    print("2. Go to 'CSV Import' tab")
    print("3. Download template and fill with your data")
    print("4. Upload CSV to import incidents")
    print("5. Use 'Batch Resolve' to suggest resolutions using RAG")
    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    test_csv_import()
