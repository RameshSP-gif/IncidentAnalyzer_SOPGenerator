"""
Demo run with sample data (no ServiceNow connection needed)
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_validation import DataValidator
from categorization import IncidentCategorizer
from sop_generation import SOPGenerator

# Sample incident data
sample_incidents = [
    {
        "number": "INC0001",
        "short_description": "Unable to access email",
        "description": "User reports unable to login to Outlook. Password reset attempted but issue persists.",
        "category": "Email",
        "resolution_notes": "Reset password and cleared Outlook cache. Verified mailbox connectivity. User can now access email successfully.",
        "priority": "3",
        "sys_created_on": "2025-11-15T10:00:00Z",
        "resolved_at": "2025-11-15T11:30:00Z"
    },
    {
        "number": "INC0002",
        "short_description": "Email access problem",
        "description": "Cannot receive emails in Outlook. Sent emails are working fine.",
        "category": "Email",
        "resolution_notes": "Checked mailbox quota - it was full. Increased mailbox limit to 50GB. Emails are now flowing normally.",
        "priority": "2",
        "sys_created_on": "2025-11-14T09:00:00Z",
        "resolved_at": "2025-11-14T10:00:00Z"
    },
    {
        "number": "INC0003",
        "short_description": "Outlook not syncing",
        "description": "Outlook application not syncing with Exchange server. Calendar and contacts missing.",
        "category": "Email",
        "resolution_notes": "Recreated Outlook profile. Configured Exchange server settings. All items syncing correctly now.",
        "priority": "2",
        "sys_created_on": "2025-11-13T14:00:00Z",
        "resolved_at": "2025-11-13T15:30:00Z"
    },
    {
        "number": "INC0004",
        "short_description": "Email sending issues",
        "description": "User cannot send emails. Receiving emails works fine. Error message about SMTP server.",
        "category": "Email",
        "resolution_notes": "Updated SMTP server settings in Outlook. Verified port 587 is open. User can send emails now.",
        "priority": "3",
        "sys_created_on": "2025-11-12T11:00:00Z",
        "resolved_at": "2025-11-12T12:00:00Z"
    },
    {
        "number": "INC0005",
        "short_description": "Password reset request",
        "description": "User forgot password and cannot login to email account.",
        "category": "Email",
        "resolution_notes": "Reset user password through Active Directory. Sent temporary password via SMS. User logged in successfully.",
        "priority": "3",
        "sys_created_on": "2025-11-11T08:00:00Z",
        "resolved_at": "2025-11-11T08:30:00Z"
    },
    {
        "number": "INC0006",
        "short_description": "Network connectivity issue",
        "description": "Intermittent network disconnections. WiFi keeps dropping every few minutes.",
        "category": "Network",
        "resolution_notes": "Replaced faulty network cable. Updated network adapter drivers. Connection is now stable.",
        "priority": "1",
        "sys_created_on": "2025-11-10T13:00:00Z",
        "resolved_at": "2025-11-10T14:30:00Z"
    },
    {
        "number": "INC0007",
        "short_description": "Cannot connect to VPN",
        "description": "VPN client shows error when trying to connect. Authentication fails.",
        "category": "Network",
        "resolution_notes": "Reset VPN credentials. Updated VPN client to latest version. User can connect successfully now.",
        "priority": "2",
        "sys_created_on": "2025-11-09T10:00:00Z",
        "resolved_at": "2025-11-09T11:00:00Z"
    },
    {
        "number": "INC0008",
        "short_description": "Slow network speed",
        "description": "Network is extremely slow. Web pages take forever to load.",
        "category": "Network",
        "resolution_notes": "Identified bandwidth saturation. Implemented QoS policies. Network speed improved significantly.",
        "priority": "2",
        "sys_created_on": "2025-11-08T15:00:00Z",
        "resolved_at": "2025-11-08T16:30:00Z"
    },
]

def main():
    print("="*70)
    print("DEMO RUN - SOP Creation System")
    print("Using sample incident data (no ServiceNow connection required)")
    print("="*70)
    
    # Step 1: Validate incidents
    print("\n[STEP 1] Validating incident data...")
    validator = DataValidator(
        required_fields=["number", "short_description", "resolution_notes"],
        min_description_length=20,
        min_resolution_length=30
    )
    
    valid, invalid = validator.validate_incidents(sample_incidents)
    print(f"  ✓ Valid incidents: {len(valid)}")
    print(f"  ✓ Invalid incidents: {len(invalid)}")
    
    if not valid:
        print("\n✗ No valid incidents to process!")
        return
    
    # Save valid incidents
    Path("data/incidents").mkdir(parents=True, exist_ok=True)
    Path("data/validated").mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with open(f"data/incidents/demo_incidents_{timestamp}.json", 'w') as f:
        json.dump(sample_incidents, f, indent=2)
    
    with open(f"data/validated/valid_{timestamp}.json", 'w') as f:
        json.dump(valid, f, indent=2)
    
    # Step 2: Categorize incidents
    print("\n[STEP 2] Categorizing incidents using ML...")
    categorizer = IncidentCategorizer(
        embedding_model="all-MiniLM-L6-v2",
        min_cluster_size=2,  # Lower for demo
        min_samples=1
    )
    
    clusters = categorizer.categorize_incidents(valid)
    print(f"  ✓ Created {len(clusters)} clusters")
    
    # Save clusters
    Path("data/clusters").mkdir(parents=True, exist_ok=True)
    clusters_serializable = {
        str(cluster_id): cluster_incidents
        for cluster_id, cluster_incidents in clusters.items()
    }
    
    with open(f"data/clusters/clusters_{timestamp}.json", 'w') as f:
        json.dump(clusters_serializable, f, indent=2)
    
    # Step 3: Generate SOPs
    print("\n[STEP 3] Generating SOPs...")
    generator = SOPGenerator(
        min_incidents=2,  # Lower for demo
        template_format="markdown"
    )
    
    Path("output/sops").mkdir(parents=True, exist_ok=True)
    Path("output/reports").mkdir(parents=True, exist_ok=True)
    
    sop_count = 0
    sop_files = []
    
    for cluster_id, cluster_incidents in clusters.items():
        print(f"  Processing cluster {cluster_id} ({len(cluster_incidents)} incidents)...")
        
        # Analyze cluster
        analysis = categorizer.analyze_cluster(cluster_id, cluster_incidents)
        
        # Generate SOP
        sop_content = generator.generate_sop(cluster_id, cluster_incidents, analysis)
        
        if sop_content:
            sop_file = f"output/sops/SOP-{cluster_id:04d}_demo_{timestamp}.md"
            with open(sop_file, 'w', encoding='utf-8') as f:
                f.write(sop_content)
            
            sop_files.append(sop_file)
            sop_count += 1
            print(f"    ✓ Generated: {sop_file}")
    
    # Summary
    print("\n" + "="*70)
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("="*70)
    print(f"Total Incidents: {len(sample_incidents)}")
    print(f"Valid Incidents: {len(valid)}")
    print(f"Clusters Created: {len(clusters)}")
    print(f"SOPs Generated: {sop_count}")
    
    print("\n📁 Output Files:")
    print(f"  • Sample data: data/incidents/demo_incidents_{timestamp}.json")
    print(f"  • Validated: data/validated/valid_{timestamp}.json")
    print(f"  • Clusters: data/clusters/clusters_{timestamp}.json")
    
    if sop_files:
        print("\n📄 Generated SOPs:")
        for sop_file in sop_files:
            print(f"  • {sop_file}")
        
        print("\n💡 Next Steps:")
        print("  1. Review the generated SOPs in output/sops/")
        print("  2. Configure ServiceNow credentials in .env for real data")
        print("  3. Run: python main.py (to process real ServiceNow data)")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
