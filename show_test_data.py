"""
Quick script to show test data from MongoDB for testing AI resolution suggestions
"""
import sys
sys.path.insert(0, 'C:/Incident_Analyser_SOP_Creator/src')

from database.mongodb import MongoDBClient

db = MongoDBClient()
incidents = list(db.collection.find().limit(15))

print('=' * 80)
print('TEST DATA - Copy any description below and test in the web form')
print('=' * 80)
print()

for i, inc in enumerate(incidents[:10], 1):
    print(f'TEST {i}:')
    print(f'  Incident: {inc.get("number", "N/A")}')
    print(f'  Category: {inc.get("category", "General")}')
    desc = inc.get("description", "N/A")
    print(f'  Description: {desc[:150]}...' if len(desc) > 150 else f'  Description: {desc}')
    print()

print('=' * 80)
print('HOW TO TEST:')
print('1. Go to http://127.0.0.1:5000')
print('2. Copy any description above')
print('3. Paste in "Incident Description" field')
print('4. Select "General" category')
print('5. Click "AI Suggest Resolution" button')
print('=' * 80)
