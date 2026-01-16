#!/usr/bin/env python3
"""Check available categories in MongoDB"""
import sys
sys.path.insert(0, 'C:/Incident_Analyser_SOP_Creator')

from src.database.mongodb_client import MongoDBClient

client = MongoDBClient()
incidents = client.get_all_incidents(limit=100)

categories = set(i.get('category', '') for i in incidents if i.get('category'))

print("\nAvailable Categories in MongoDB:")
print("="*50)
for cat in sorted(categories):
    count = sum(1 for i in incidents if i.get('category') == cat)
    print(f"  ✓ {cat:<20} ({count} incidents)")
print("="*50)
print(f"\nTotal: {len(categories)} unique categories")
print(f"Total incidents: {len(incidents)}")
