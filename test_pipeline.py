"""
Test Pipeline - Generate SOPs from MongoDB Data

This script tests the full pipeline using actual MongoDB data.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database import get_db_client
from data_validation import DataValidator
from categorization import IncidentCategorizer
from sop_generation import SOPGenerator
from loguru import logger
import json
from datetime import datetime


def test_pipeline(limit: int = 50):
    """
    Test the full pipeline with MongoDB data
    
    Args:
        limit: Number of incidents to process (default: 50)
    """
    print("\n" + "="*70)
    print("TESTING SOP GENERATION PIPELINE")
    print("="*70)
    print(f"Processing {limit} incidents from MongoDB\n")
    
    # Step 1: Fetch incidents from MongoDB
    print("[STEP 1] Fetching incidents from MongoDB...")
    db_client = get_db_client()
    
    incidents = db_client.get_all_incidents(limit=limit)
    print(f"✓ Fetched {len(incidents)} incidents")
    
    # Show sample
    if incidents:
        sample = incidents[0]
        print(f"\nSample Incident:")
        print(f"  Number: {sample.get('number')}")
        print(f"  Description: {sample.get('short_description', '')[:60]}...")
        print(f"  Priority: {sample.get('priority')}")
        print(f"  State: {sample.get('state')}")
        resolution = sample.get('resolution_notes', '')
        if resolution:
            print(f"  Resolution: {resolution[:80]}...")
        print()
    
    # Step 2: Validate incidents
    print("[STEP 2] Validating incidents...")
    required_fields = ['number', 'short_description', 'description', 'resolution_notes']
    validator = DataValidator(required_fields=required_fields)
    
    valid_incidents = []
    invalid_incidents = []
    
    for incident in incidents:
        validation_result = validator.validate_incident(incident)
        if validation_result['is_valid']:
            valid_incidents.append(incident)
        else:
            invalid_incidents.append(incident)
    
    validated = {
        'valid': valid_incidents,
        'invalid': invalid_incidents
    }
    
    print(f"✓ Valid incidents: {len(validated['valid'])}")
    print(f"✓ Invalid incidents: {len(validated['invalid'])}")
    
    if not validated['valid']:
        print("\n❌ No valid incidents to process!")
        return
    
    # Save validated data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    validated_file = Path("data/validated") / f"valid_test_{timestamp}.json"
    validated_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(validated_file, 'w', encoding='utf-8') as f:
        json.dump(validated['valid'], f, indent=2, ensure_ascii=False)
    print(f"✓ Saved validated data to: {validated_file}")
    print()
    
    # Step 3: Categorize incidents
    print("[STEP 3] Categorizing incidents using ML...")
    categorizer = IncidentCategorizer()
    
    clusters = categorizer.categorize_incidents(validated['valid'])
    print(f"✓ Created {len(clusters)} clusters")
    
    # Show cluster summary
    for cluster_id, incidents_list in clusters.items():
        print(f"  - Cluster {cluster_id}: {len(incidents_list)} incidents")
    print()
    
    # Save clusters
    clusters_file = Path("data/clusters") / f"clusters_test_{timestamp}.json"
    clusters_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert numpy int64 keys to regular int
    clusters_serializable = {int(k): v for k, v in clusters.items()}
    
    with open(clusters_file, 'w', encoding='utf-8') as f:
        json.dump(clusters_serializable, f, indent=2, ensure_ascii=False, default=str)
    print(f"✓ Saved clusters to: {clusters_file}")
    print()
    
    # Step 4: Generate SOPs
    print("[STEP 4] Generating SOPs...")
    generator = SOPGenerator()
    
    sop_files = []
    for cluster_id, incidents_list in clusters.items():
        print(f"  Processing cluster {cluster_id} ({len(incidents_list)} incidents)...")
        
        # Analyze cluster (pass incidents directly)
        analysis = categorizer.analyze_cluster(cluster_id, incidents_list)
        
        # Generate SOP (correct parameter name is 'analysis')
        sop_content = generator.generate_sop(
            cluster_id=cluster_id,
            incidents=incidents_list,
            analysis=analysis
        )
        
        # Save SOP
        sop_file = Path("output/sops") / f"SOP-{cluster_id:04d}_test_{timestamp}.md"
        sop_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(sop_file, 'w', encoding='utf-8') as f:
            f.write(sop_content)
        
        sop_files.append(sop_file)
        print(f"    ✓ Generated: {sop_file}")
    
    print()
    print("="*70)
    print("✅ TEST COMPLETED SUCCESSFULLY!")
    print("="*70)
    print(f"Total Incidents Processed: {len(validated['valid'])}")
    print(f"Clusters Created: {len(clusters)}")
    print(f"SOPs Generated: {len(sop_files)}")
    print()
    print("📄 Generated SOPs:")
    for sop_file in sop_files:
        print(f"  • {sop_file}")
    print()
    
    # Show first SOP preview
    if sop_files:
        print("="*70)
        print("PREVIEW OF FIRST SOP")
        print("="*70)
        with open(sop_files[0], 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:30]):
                print(line.rstrip())
                if i == 29:
                    print("\n... (truncated)")
        print("="*70)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test SOP generation pipeline with MongoDB data"
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=50,
        help="Number of incidents to process (default: 50)"
    )
    
    args = parser.parse_args()
    
    try:
        test_pipeline(limit=args.limit)
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
