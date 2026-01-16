"""
Reimport all incidents from CSV
"""
from src.database import get_db_client

client = get_db_client()

# Clear all existing incidents
print("=" * 80)
print("CLEARING ALL EXISTING INCIDENTS")
print("=" * 80)
result = client.collection.delete_many({})
print(f"Deleted {result.deleted_count} incidents\n")

# Import from CSV with proper encoding
print("=" * 80)
print("IMPORTING FROM CSV: incidents.csv")
print("=" * 80)
import_result = client.import_from_csv(r'incidents.csv')

print("\nIMPORT RESULTS:")
print(f"  Imported: {import_result['imported']}")
print(f"  Skipped: {import_result['skipped']}")
print(f"  Errors: {import_result['errors']}")
print(f"  Total: {import_result['total']}")

# Verify resolution notes
print("\n" + "=" * 80)
print("VERIFYING IMPORTED DATA")
print("=" * 80)
incidents = client.get_all_incidents(limit=10000)
null_res = [i for i in incidents if not i.get('resolution_notes') or i.get('resolution_notes').strip() == '']
with_res = [i for i in incidents if i.get('resolution_notes') and i.get('resolution_notes').strip() != '']

print(f"\nTotal incidents in DB: {len(incidents)}")
print(f"Incidents WITH resolution_notes: {len(with_res)} ({len(with_res)/len(incidents)*100:.1f}%)")
print(f"Incidents WITHOUT resolution_notes: {len(null_res)} ({len(null_res)/len(incidents)*100:.1f}%)")

if with_res:
    print(f"\nSample incidents WITH resolution (first 3):")
    for sample in with_res[:3]:
        print(f"\n  Number: {sample.get('number')}")
        print(f"  Short description: {sample.get('short_description', '')[:60]}")
        print(f"  Resolution: {sample.get('resolution_notes', '')[:80]}...")

print("\n" + "=" * 80)
print("REIMPORT COMPLETE!")
print("=" * 80)
print("\nNow restart the web application to refresh the cache.")
