#!/usr/bin/env python3
"""
Generate 100 test incidents for knowledge base
"""

import csv
from datetime import datetime, timedelta
import random
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database import get_db_client
from loguru import logger

# Categories and subcategories
CATEGORIES = {
    "Hardware": ["Desktop", "Laptop", "Monitor", "Printer", "Keyboard", "Mouse", "Server", "Peripherals"],
    "Software": ["Office", "Database Client", "Adobe", "Installation", "Update", "License", "Browser"],
    "Network": ["LAN", "VPN", "WiFi", "Internet", "DNS", "Web Access", "Email Server", "Firewall"],
    "Email": ["Outlook", "Gmail", "Spam Filter", "Sync", "Storage"],
    "Access": ["Password Reset", "Network Drive", "Application Access", "VPN Access", "Permission"],
    "Database": ["Connection", "Performance", "Backup", "Recovery", "Replication"],
    "Security": ["Antivirus", "Malware", "Password", "Encryption", "Compliance"],
}

# Common issues for each category
ISSUE_TEMPLATES = {
    "Hardware": [
        "{device} not working",
        "{device} malfunctioning",
        "{device} displaying errors",
        "{device} no response",
        "{device} not detected",
        "{device} overheating",
        "{device} making noise",
        "{device} connection lost",
    ],
    "Software": [
        "{app} crashing",
        "{app} not launching",
        "{app} slow performance",
        "{app} license expired",
        "{app} update failed",
        "{app} compatibility issue",
        "{app} corrupted files",
    ],
    "Network": [
        "Network connection {issue}",
        "Internet {issue}",
        "VPN {issue}",
        "WiFi {issue}",
        "Connectivity {issue}",
        "Speed {issue}",
        "DNS {issue}",
    ],
    "Email": [
        "Email not {action}",
        "Emails not {action}",
        "Mailbox {action}",
        "Spam {action}",
        "Attachment {action}",
    ],
    "Access": [
        "Cannot access {resource}",
        "Permission denied for {resource}",
        "Unauthorized access to {resource}",
        "Cannot connect to {resource}",
    ],
    "Database": [
        "Database {issue}",
        "Query {issue}",
        "Connection {issue}",
        "Data {issue}",
    ],
    "Security": [
        "Security alert: {issue}",
        "Account locked: {issue}",
        "Suspicious activity: {issue}",
    ],
}

# Resolution templates
RESOLUTIONS = [
    "Restarted service. Verified configuration. Issue resolved.",
    "Updated drivers/software to latest version. Tested and confirmed working.",
    "Cleared cache and temporary files. Reinitiated connection. Working now.",
    "Reset user account permissions. Verified access. Issue resolved.",
    "Replaced hardware component. Tested functionality. Operational.",
    "Optimized configuration settings. Performance improved.",
    "Reinstalled application. Verified compatibility. Working properly.",
    "Patched vulnerability. Updated security settings. System secured.",
    "Recovered from backup. Restored data integrity. Operational.",
    "Reconfigured network settings. Verified connectivity. Restored.",
]

ASSIGNMENT_GROUPS = ["IT Support", "Network Team", "Hardware Team", "Database Team", "Security Team", "Infrastructure"]
ASSIGNEES = ["John Doe", "Jane Smith", "Bob Johnson", "Alice Brown", "Mike Wilson", "Sarah Davis"]

def generate_incidents_csv(filename, count=100):
    """Generate CSV file with test incidents"""
    
    base_date = datetime(2025, 1, 1)
    incidents = []
    
    for i in range(1, count + 1):
        category = random.choice(list(CATEGORIES.keys()))
        subcategory = random.choice(CATEGORIES[category])
        
        # Generate description
        template = random.choice(ISSUE_TEMPLATES.get(category, ["Issue with {item}"]))
        devices = ["Computer", "Printer", "Network", "Server", "Monitor", "Email Server", "Database", "VPN"]
        apps = ["Outlook", "Excel", "Teams", "Photoshop", "Chrome", "Slack"]
        resources = ["shared drive", "intranet", "database", "application", "network share"]
        issues = ["failing", "down", "slow", "not responding", "unavailable", "disconnected"]
        actions = ["sending", "receiving", "syncing", "loading", "opening"]
        items = devices + apps + resources
        
        short_desc = template.format(
            device=random.choice(devices),
            app=random.choice(apps),
            resource=random.choice(resources),
            issue=random.choice(issues),
            action=random.choice(actions),
            item=random.choice(items),
        )
        
        # Generate timestamps
        days_offset = random.randint(1, 300)
        created = base_date + timedelta(days=days_offset)
        updated = created + timedelta(hours=random.randint(1, 24))
        resolved = updated + timedelta(hours=random.randint(1, 12))
        
        # Priority (1=Urgent, 2=High, 3=Medium, 4=Low)
        priority = random.choice([1, 2, 2, 3, 3, 3, 4, 4])
        
        incident = {
            "number": f"INC{i:04d}",
            "short_description": short_desc,
            "description": f"{short_desc}. User reported issue affecting productivity.",
            "category": category,
            "subcategory": subcategory,
            "priority": priority,
            "state": "Closed",
            "resolution_notes": random.choice(RESOLUTIONS),
            "close_notes": "Incident successfully resolved and closed.",
            "assignment_group": random.choice(ASSIGNMENT_GROUPS),
            "assigned_to": random.choice(ASSIGNEES),
            "sys_created_on": created.strftime("%Y-%m-%d %H:%M:%S"),
            "sys_updated_on": updated.strftime("%Y-%m-%d %H:%M:%S"),
            "resolved_at": resolved.strftime("%Y-%m-%d %H:%M:%S"),
        }
        incidents.append(incident)
    
    # Write to CSV
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            "number", "short_description", "description", "category", "subcategory",
            "priority", "state", "resolution_notes", "close_notes", "assignment_group",
            "assigned_to", "sys_created_on", "sys_updated_on", "resolved_at"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(incidents)
    
    logger.info(f"Generated {count} incidents in {filename}")
    return filename

def import_to_mongodb(csv_file):
    """Import CSV to MongoDB"""
    logger.info(f"Starting import from {csv_file}")
    
    db_client = get_db_client()
    result = db_client.import_from_csv(csv_file)
    
    print("\n" + "="*60)
    print("TEST INCIDENTS IMPORT RESULTS")
    print("="*60)
    print(f"Total Records: {result.get('total', 0)}")
    print(f"Successfully Imported: {result.get('imported', 0)}")
    print(f"Skipped (duplicates): {result.get('skipped', 0)}")
    print(f"Errors: {result.get('errors', 0)}")
    
    if 'error_message' in result:
        print(f"Error Message: {result['error_message']}")
    
    print("="*60)
    
    # Show final count
    total_count = db_client.get_incident_count()
    print(f"\nTotal Incidents in Database: {total_count}")
    
    # Show category breakdown
    try:
        categories = db_client.get_categories()
        print(f"\nCategories in Database: {len(categories)}")
        for cat in categories[:5]:
            print(f"  - {cat}")
    except Exception as e:
        logger.warning(f"Could not fetch categories: {e}")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    # Generate CSV file
    csv_file = Path(__file__).parent / "test_incidents_100.csv"
    generate_incidents_csv(str(csv_file), count=100)
    
    # Import to MongoDB
    import_to_mongodb(str(csv_file))
    
    logger.info("Demo data import complete!")
    print("\n✓ Knowledge base updated with 100 test incidents!")
    print(f"✓ Data is ready for testing and demo")
