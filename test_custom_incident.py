#!/usr/bin/env python3
"""
Test resolution and SOP generation with custom incident data
"""
from src.database.mongodb import MongoDBClient
from src.data_validation.validator import DataValidator
from src.categorization.categorizer import IncidentCategorizer
from src.sop_generation.generator import SOPGenerator
from datetime import datetime
import json

def test_custom_incident(short_description, description, priority, category="General"):
    """
    Test resolution and SOP generation with custom incident data
    
    Args:
        short_description: Brief summary of the issue
        description: Detailed description of the issue
        priority: Priority level (1-5)
        category: Category of the incident
    """
    print("\n" + "="*70)
    print("TESTING RESOLUTION AND SOP GENERATION")
    print("="*70)
    
    # Create test incident
    test_incident = {
        "number": f"TEST{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "short_description": short_description,
        "description": description,
        "priority": priority,
        "state": "New",
        "category": category,
        "assignment_group": "Test Group",
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat()
    }
    
    print(f"\n📋 Test Incident Created:")
    print(f"  Number: {test_incident['number']}")
    print(f"  Short Description: {short_description}")
    print(f"  Description: {description[:100]}...")
    print(f"  Priority: {priority}")
    print(f"  Category: {category}")
    
    # Now find similar incidents from MongoDB to generate resolution
    print("\n[STEP 1] Finding similar incidents in MongoDB...")
    client = MongoDBClient()
    
    # Search for similar incidents based on description
    similar_incidents = client.get_all_incidents(limit=200)
    
    # Filter incidents that might be similar (simple keyword matching)
    keywords = description.lower().split()[:5]  # Take first 5 words as keywords
    similar_found = []
    
    for incident in similar_incidents:
        incident_desc = incident.get('description', '').lower()
        incident_short = incident.get('short_description', '').lower()
        
        # Check if any keywords match
        matches = sum(1 for kw in keywords if kw in incident_desc or kw in incident_short)
        if matches >= 1:  # At least 1 keyword matches
            similar_found.append(incident)
            if len(similar_found) >= 50:  # Limit to 50 similar incidents
                break
    
    print(f"✓ Found {len(similar_found)} similar incidents in database")
    
    if similar_found:
        print("\n[STEP 2] Generating resolution based on similar incidents...")
        
        # Show sample resolutions from similar incidents
        print("\nSample resolutions from similar incidents:")
        for i, inc in enumerate(similar_found[:3], 1):
            res_notes = inc.get('resolution_notes', 'N/A')
            print(f"\n  {i}. Incident {inc.get('number')}:")
            print(f"     {res_notes[:150]}...")
        
        # Combine test incident with similar incidents for clustering
        test_incident['resolution_notes'] = f"Test incident - Similar to existing incidents. Expected resolution based on patterns."
        all_incidents = [test_incident] + similar_found[:49]  # Include test + 49 similar (total 50)
        
        print(f"\n[STEP 3] Creating cluster with {len(all_incidents)} incidents...")
        
        # Validate incidents
        required_fields = ['number', 'description', 'priority', 'state']
        validator = DataValidator(required_fields=required_fields)
        valid_incidents, invalid_incidents = validator.validate_incidents(all_incidents)
        
        print(f"✓ Valid incidents: {len(valid_incidents)}")
        
        if len(valid_incidents) >= 2:
            # Categorize incidents
            categorizer = IncidentCategorizer()
            result = categorizer.categorize_incidents(valid_incidents)
            
            print(f"✓ Clustering completed")
            
            # Generate SOP for the cluster containing our test incident
            clusters = result.get('clusters', result) if isinstance(result, dict) else result
            if clusters:
                # Find cluster containing test incident
                test_cluster = None
                test_cluster_id = None
                
                for cluster_id, cluster_incidents in clusters.items():
                    incident_numbers = [inc.get('number') for inc in cluster_incidents]
                    if test_incident['number'] in incident_numbers:
                        test_cluster = cluster_incidents
                        test_cluster_id = cluster_id
                        break
                
                if test_cluster:
                    print(f"\n[STEP 4] Test incident found in cluster {test_cluster_id} with {len(test_cluster)} incidents")
                    print(f"         Generating SOP...")
                    
                    # Analyze cluster
                    analysis = categorizer.analyze_cluster(test_cluster_id, test_cluster)
                    
                    # Generate SOP
                    generator = SOPGenerator()
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_file = f"output/sops/SOP-{test_cluster_id:04d}_custom_test_{timestamp}.md"
                    
                    generator.generate_sop(
                        cluster_id=test_cluster_id,
                        analysis=analysis,
                        output_file=output_file
                    )
                    
                    print(f"\n✓ SOP Generated: {output_file}")
                    
                    # Display preview
                    print("\n" + "="*70)
                    print("SOP PREVIEW")
                    print("="*70)
                    with open(output_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for line in lines[:50]:  # Show first 50 lines
                            print(line.rstrip())
                    print("\n... (truncated)")
                    
                else:
                    print("\n⚠️  Test incident was classified as noise (no similar cluster found)")
                    print("    This means the incident is unique and doesn't match existing patterns")
            else:
                print("\n⚠️  No clusters created - incidents may be too diverse")
        else:
            print("\n❌ Not enough valid incidents for clustering")
    else:
        print("\n⚠️  No similar incidents found in database")
        print("    Try different keywords or descriptions")
    
    print("\n" + "="*70)
    print("TEST COMPLETED")
    print("="*70)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Command line mode
        short_desc = sys.argv[1]
        description = sys.argv[2] if len(sys.argv) > 2 else short_desc
        priority = sys.argv[3] if len(sys.argv) > 3 else "3 - Medium"
        category = sys.argv[4] if len(sys.argv) > 4 else "General"
        
        test_custom_incident(short_desc, description, priority, category)
    else:
        # Interactive mode
        print("\n" + "="*70)
        print("CUSTOM INCIDENT TEST - Interactive Mode")
        print("="*70)
        print("\nEnter incident details to test resolution and SOP generation:\n")
        
        short_desc = input("Short Description: ").strip()
        if not short_desc:
            short_desc = "Test incident for invoice issue"
        
        description = input("Detailed Description: ").strip()
        if not description:
            description = short_desc
        
        priority = input("Priority (1-5 or '3 - Medium'): ").strip()
        if not priority:
            priority = "3 - Medium"
        
        category = input("Category [General]: ").strip()
        if not category:
            category = "General"
        
        test_custom_incident(short_desc, description, priority, category)
