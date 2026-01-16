#!/usr/bin/env python3
"""
Simple test to show how resolution and SOP generation works
"""
from src.database.mongodb import MongoDBClient
from src.data_validation.validator import DataValidator
from src.categorization.categorizer import IncidentCategorizer
from src.sop_generation.generator import SOPGenerator
from datetime import datetime

def show_example_resolution_and_sop():
    """
    Demonstrate resolution and SOP generation with actual MongoDB data
    """
    print("\n" + "="*70)
    print("DEMONSTRATION: RESOLUTION & SOP GENERATION")
    print("="*70)
    
    # Connect to MongoDB
    client = MongoDBClient()
    
    print("\n[STEP 1] Fetching sample incidents from MongoDB...")
    # Get 100 incidents to work with
    incidents = client.get_all_incidents(limit=100)
    print(f"[OK] Fetched {len(incidents)} incidents")
    
    # Show some sample incident details
    print("\n" + "="*70)
    print("SAMPLE INCIDENTS WITH RESOLUTION NOTES")
    print("="*70)
    
    for i, inc in enumerate(incidents[:5], 1):
        print(f"\n{i}. Incident: {inc.get('number')}")
        print(f"   Short Description: {inc.get('short_description', 'N/A')[:70]}")
        print(f"   Priority: {inc.get('priority')}")
        print(f"   Category: {inc.get('category', 'General')}")
        print(f"   Resolution Notes:")
        res_notes = inc.get('resolution_notes', 'N/A')
        # Show first 200 chars of resolution
        print(f"   {res_notes[:200]}...")
    
    print("\n" + "="*70)
    print("[STEP 2] Validating and preparing incidents...")
    print("="*70)
    
    # Validate incidents
    required_fields = ['number', 'description', 'priority', 'state']
    validator = DataValidator(required_fields=required_fields)
    valid_incidents, invalid_incidents = validator.validate_incidents(incidents)
    
    print(f"[OK] Valid incidents: {len(valid_incidents)}")
    print(f"[OK] Invalid incidents: {len(invalid_incidents)}")
    
    if len(valid_incidents) < 10:
        print("\n❌ Not enough valid incidents for demonstration")
        return
    
    print("\n" + "="*70)
    print("[STEP 3] Categorizing incidents using ML clustering...")
    print("="*70)
    
    # Categorize incidents
    categorizer = IncidentCategorizer()
    clusters = categorizer.categorize_incidents(valid_incidents)
    
    if not clusters:
        print("\n⚠️  No clusters created")
        return
    
    print(f"\n[OK] Created {len(clusters)} clusters:")
    for cluster_id, cluster_incidents in clusters.items():
        print(f"   - Cluster {cluster_id}: {len(cluster_incidents)} incidents")
    
    # Pick the largest cluster for SOP generation
    largest_cluster_id = max(clusters.keys(), key=lambda k: len(clusters[k]))
    largest_cluster = clusters[largest_cluster_id]
    
    print(f"\n[OK] Selected cluster {largest_cluster_id} with {len(largest_cluster)} incidents for SOP")
    
    print("\n" + "="*70)
    print("[STEP 4] Analyzing cluster and generating SOP...")
    print("="*70)
    
    # Analyze cluster
    analysis = categorizer.analyze_cluster(largest_cluster_id, largest_cluster)
    
    print(f"\nCluster Analysis:")
    print(f"  Common Keywords: {', '.join(analysis.get('common_keywords', [])[:10])}")
    print(f"  Average Resolution Time: {analysis.get('avg_resolution_time', 0):.1f} hours")
    print(f"  Most Common Priority: {analysis.get('most_common_priority', 'N/A')}")
    
    # Generate SOP
    generator = SOPGenerator()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"output/sops/SOP-{largest_cluster_id:04d}_demo_{timestamp}.md"
    
    sop_content = generator.generate_sop(
        cluster_id=largest_cluster_id,
        incidents=largest_cluster,
        analysis=analysis
    )
    
    # Save SOP to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sop_content)
    
    print(f"\n[OK] SOP Generated: {output_file}")
    
    # Show SOP preview
    print("\n" + "="*70)
    print("GENERATED SOP PREVIEW")
    print("="*70)
    
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    for i, line in enumerate(lines[:80], 1):  # Show first 80 lines
        print(line)
    
    if len(lines) > 80:
        print(f"\n... ({len(lines) - 80} more lines)")
    
    print("\n" + "="*70)
    print("HOW IT WORKS")
    print("="*70)
    print("""
1. SHORT DESCRIPTION: Brief summary of the incident type
   Example: "Invoice amount incorrect"

2. DETAILED DESCRIPTION: Full explanation of the issue  
   Example: "The invoice 405025 shows wrong transport charges..."

3. CATEGORY: Type of incident (Financial, Technical, etc.)
   This helps group similar incidents together

4. PRIORITY: Urgency level (1-5 or "3 - Medium")
   Affects SOP prioritization and SLA

THE SYSTEM THEN:
- Finds similar incidents in MongoDB using ML embeddings
- Groups them into clusters using DBSCAN algorithm
- Extracts resolution steps from historical incidents
- Generates a Standard Operating Procedure (SOP)
- SOP includes: Problem statement, symptoms, resolution steps

YOUR TEST INCIDENT would follow the same process:
- Input: short_description, description, category, priority
- System finds similar resolved incidents
- Extracts common resolution patterns
- Creates SOP with step-by-step resolution guide
""")
    
    print("="*70)
    print("[SUCCESS] DEMONSTRATION COMPLETE")
    print("="*70)
    print(f"\nGenerated SOP saved to: {output_file}")
    print("This demonstrates how your custom incident would be processed.")


if __name__ == "__main__":
    show_example_resolution_and_sop()
