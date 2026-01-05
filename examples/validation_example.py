"""
Example: Data validation and quality checking
"""

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data_validation import DataValidator

# Sample incidents with various quality issues
sample_incidents = [
    {
        "number": "INC0001",
        "short_description": "Email issue",
        "description": "User cannot access email system",
        "category": "Email",
        "resolution_notes": "Reset password and cleared cache. Issue resolved.",
        "priority": "3"
    },
    {
        "number": "INC0002",
        "short_description": "",  # MISSING
        "description": "Test",    # TOO SHORT
        "category": "Unknown",     # INVALID CATEGORY
        "resolution_notes": "Fixed",  # TOO SHORT
        "priority": "3"
    },
    {
        "number": "INC0003",
        # Missing required fields
        "description": "Network problem",
        "priority": "2"
    },
]

def main():
    """Demonstrate data validation"""
    
    print("Data Validation Example")
    print("="*60)
    
    # Initialize validator
    validator = DataValidator(
        required_fields=["number", "short_description", "resolution_notes", "category"],
        min_description_length=20,
        min_resolution_length=30
    )
    
    # Validate incidents
    print(f"\nValidating {len(sample_incidents)} incidents...\n")
    valid, invalid = validator.validate_incidents(sample_incidents)
    
    # Display results
    print(f"Valid incidents: {len(valid)}")
    print(f"Invalid incidents: {len(invalid)}")
    
    # Show invalid incidents with errors
    if invalid:
        print("\nInvalid Incidents Details:")
        print("-"*60)
        for incident in invalid:
            print(f"\nIncident: {incident.get('number', 'UNKNOWN')}")
            errors = incident.get('_validation_errors', [])
            for error in errors:
                print(f"  [{error['severity']}] {error['type']}: {error.get('message', '')}")
                if 'fields' in error:
                    print(f"    Missing fields: {', '.join(error['fields'])}")
    
    # Generate quality report
    quality_report = validator.generate_quality_report(valid, invalid)
    
    print("\n" + "="*60)
    print("Quality Report")
    print("="*60)
    print(f"Total Incidents: {quality_report['total_incidents']}")
    print(f"Quality Score: {quality_report['quality_score']:.2f}%")
    print("\nError Summary:")
    for error_type, count in quality_report['error_summary'].items():
        print(f"  {error_type}: {count}")
    
    # Save results
    with open("validation_results.json", 'w') as f:
        json.dump(quality_report, f, indent=2)
    
    print("\nResults saved to validation_results.json")

if __name__ == "__main__":
    main()
