"""
Example: Custom categorization and SOP generation
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from categorization import IncidentCategorizer
from sop_generation import SOPGenerator

# Sample incidents (normally fetched from ServiceNow)
sample_incidents = [
    {
        "number": "INC0001",
        "short_description": "Unable to access email",
        "description": "User cannot login to email client",
        "category": "Email",
        "resolution_notes": "Reset password and cleared browser cache. User can now access email.",
        "priority": "3"
    },
    {
        "number": "INC0002",
        "short_description": "Email access issue",
        "description": "Cannot receive emails",
        "category": "Email",
        "resolution_notes": "Checked mailbox quota. Increased limit. Emails flowing normally.",
        "priority": "2"
    },
    {
        "number": "INC0003",
        "short_description": "Network connectivity problem",
        "description": "Intermittent network disconnections",
        "category": "Network",
        "resolution_notes": "Replaced faulty network cable. Connection stable.",
        "priority": "1"
    },
    # Add more incidents...
]

def main():
    """Demonstrate custom categorization"""
    
    print("Categorizing incidents...")
    
    # Initialize categorizer with custom settings
    categorizer = IncidentCategorizer(
        embedding_model="all-MiniLM-L6-v2",
        min_cluster_size=2,  # Lower for demo
        min_samples=1,
        similarity_threshold=0.70
    )
    
    # Categorize incidents
    clusters = categorizer.categorize_incidents(sample_incidents)
    
    print(f"\nFound {len(clusters)} clusters:")
    
    # Initialize SOP generator
    generator = SOPGenerator(
        min_incidents=2,  # Lower for demo
        template_format="markdown"
    )
    
    # Generate SOPs for each cluster
    for cluster_id, cluster_incidents in clusters.items():
        print(f"\nCluster {cluster_id}: {len(cluster_incidents)} incidents")
        
        # Analyze cluster
        analysis = categorizer.analyze_cluster(cluster_id, cluster_incidents)
        print(f"  Common categories: {analysis['common_categories']}")
        
        # Generate SOP
        sop_content = generator.generate_sop(
            cluster_id,
            cluster_incidents,
            analysis
        )
        
        if sop_content:
            # Save SOP
            output_file = f"SOP-{cluster_id:04d}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(sop_content)
            print(f"  Generated: {output_file}")

if __name__ == "__main__":
    main()
