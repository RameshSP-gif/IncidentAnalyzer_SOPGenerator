"""
Example: Basic usage of the SOP creation system
"""

import os
from dotenv import load_dotenv
from main import SOPOrchestrator

# Load environment variables
load_dotenv()

def main():
    """Run basic SOP generation"""
    
    # Initialize orchestrator
    print("Initializing SOP Orchestrator...")
    orchestrator = SOPOrchestrator(config_path="config.yaml")
    
    # Run full pipeline
    print("\nRunning full pipeline...")
    result = orchestrator.run_full_pipeline(
        days_back=30,  # Last 30 days
        limit=500      # Max 500 incidents
    )
    
    # Print results
    if result["status"] == "success":
        print("\n" + "="*60)
        print("SUCCESS!")
        print("="*60)
        print(f"Total Incidents Analyzed: {result['total_incidents']}")
        print(f"Valid Incidents: {result['valid_incidents']}")
        print(f"Clusters Created: {result['clusters']}")
        print(f"SOPs Generated: {result['sops_generated']}")
        print(f"Processing Time: {result['duration_seconds']:.2f} seconds")
        print("\nGenerated SOPs:")
        for sop_file in result['sop_files']:
            print(f"  - {sop_file}")
    else:
        print(f"\nERROR: {result.get('message', 'Unknown error')}")

if __name__ == "__main__":
    main()
