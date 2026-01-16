# CSV Import & Knowledge Base Update Guide

## Overview

The CSV Import feature allows you to bulk import incidents from a CSV file and automatically update the knowledge base. This is perfect for migrating historical incident data or bootstrapping your knowledge base with resolved incidents.

## Features

✅ **Bulk Import** - Import hundreds of incidents at once
✅ **Automatic Knowledge Base Update** - Incidents with resolutions are added to the knowledge base automatically  
✅ **RAG-Powered Resolution Suggestions** - Get AI-suggested resolutions for incidents without them
✅ **Flexible Field Mapping** - Auto-detects CSV column names or accepts custom mapping
✅ **Data Validation** - Validates incidents before import, provides detailed error reports
✅ **Batch Resolution** - Resolve multiple unresolved incidents at once using RAG

## Getting Started

### Step 1: Download Template

1. Go to the **CSV Import** tab in the web application
2. Click **Download CSV Template** button
3. This gives you a sample CSV with the correct format

### Step 2: Prepare Your Data

Fill in the CSV file with your incident data. Required fields:

| Field | Example | Description |
|-------|---------|-------------|
| **Incident Number** | INC0001234 | Unique identifier (auto-generated if missing) |
| **Short Description** | Database connection timeout | Brief summary (required) |
| **Description** | Application unable to connect... | Detailed problem description |
| **Category** | Database | Incident category (required) |
| **Priority** | 1 | Priority level (1-4) |
| **Status** | Closed | Incident status |
| **Resolution Notes** | Restarted database service... | How the issue was resolved |
| **Created Date** | 2024-01-15 | When incident was created |
| **Resolved Date** | 2024-01-15 | When incident was resolved |

### Step 3: Upload CSV File

1. In the **CSV Import** tab, click on the file input area
2. Select your CSV file
3. Optionally check "Use RAG for unresolved incidents" to auto-suggest resolutions
4. Click **Import Incidents**

### Step 4: Review Results

The import will show:
- ✅ Total incidents imported
- ✅ Incidents added to knowledge base
- ⚠️ Any warnings or errors
- 📊 Final database count

## CSV Format

### Column Names (Auto-Detected)

The system automatically recognizes these column variations:

```
Incident Number / Ticket / ID / Number
Short Description / Summary / Title / Subject
Description / Details / Problem / Problem Statement
Category / Type / Incident Type
Priority / Severity / Impact
Resolution / Resolution Notes / Solution / Fix
Assignment Group / Assigned Group / Team
Assigned To / Assignee / Owner
Status / State / Incident State
Created Date / Created On / Date Created / sys_created_on
Resolved Date / Resolved At / Date Resolved
```

### Example CSV Content

```csv
Incident Number,Short Description,Description,Category,Priority,Status,Assignment Group,Assigned To,Resolution Notes,Created Date,Resolved Date
INC0001234,Database connection timeout,Application unable to connect to primary database server. Users cannot access the system.,Database,1,Closed,Database Team,John Doe,Restarted database service and verified connectivity. Implemented connection pooling to prevent future issues.,2024-01-15,2024-01-15
INC0001235,Email delivery failure,System unable to send email notifications. Queue is stuck with 500+ pending emails.,Email,2,Closed,Application Team,Jane Smith,Cleared stuck email queue and restarted mail service. Updated DNS MX records.,2024-01-16,2024-01-17
INC0001236,Login page not responding,Users report that login page fails to load.,Authentication,2,Closed,Web Team,Mike Johnson,Cleared web server cache and restarted nginx. Updated SSL certificates.,2024-01-17,2024-01-18
```

## Knowledge Base Updates

### What Gets Added?

Only incidents **with resolution notes** (30+ characters) are added to the knowledge base:

- ✅ Incidents with `Resolution Notes` field (30+ chars) → Added to KB
- ⚠️ Incidents without resolutions → Added to database, marked for later resolution

### Using RAG for Resolution Suggestions

1. Check "Use RAG for unresolved incidents" during import
2. System will analyze unresolved incidents and suggest resolutions from similar past incidents
3. Suggested resolutions are automatically added to the knowledge base

## Batch Resolution

After import, you can automatically resolve unresolved incidents:

1. Go to **CSV Import** tab → **Knowledge Base Summary** section
2. View statistics:
   - Total incidents in KB
   - With resolutions
   - Without resolutions
3. Click **Resolve Unresolved (Using RAG)**
4. System finds similar past incidents and suggests resolutions

## Advanced: Custom Field Mapping

For non-standard CSV formats, you can specify custom field mapping:

```json
{
  "Your Column Name": "incident_field",
  "Ticket ID": "number",
  "Problem": "short_description",
  "Full Description": "description",
  "Type": "category",
  "Solution": "resolution_notes"
}
```

## Error Handling

### Common Errors

| Error | Solution |
|-------|----------|
| "No file selected" | Select a CSV file before clicking import |
| "Only CSV files supported" | Make sure file has .csv extension |
| "No valid incidents found" | Check that required fields are present and data is valid |
| "Incident already exists" | The incident number already exists in knowledge base (skip or delete first) |

### Validation Rules

Imported incidents are validated for:
- ✅ Required fields (number, short_description)
- ✅ Minimum description length (20+ characters)
- ✅ Unique incident numbers
- ✅ Proper data format

## Performance Tips

1. **Batch Size** - Import 100-1000 incidents at a time for best performance
2. **Resolution Field** - Include resolution notes for better RAG knowledge base
3. **Categories** - Use consistent category names for better AI suggestions
4. **Quality Over Quantity** - 50 well-documented incidents are better than 500 incomplete ones

## API Endpoints

### Import CSV
```
POST /import_csv
```
Form data:
- `file`: CSV file (multipart)
- `field_mapping`: Optional JSON field mapping

### Get Knowledge Base
```
GET /get_knowledge_base
```

### Batch Resolve
```
POST /batch_resolve_incidents
```
JSON body:
```json
{
  "incident_numbers": ["INC001", "INC002"],
  "use_rag_suggestions": true
}
```

### Export Template
```
GET /export_template
```

## Workflow Examples

### Example 1: Bootstrap from ServiceNow

1. Export closed incidents from ServiceNow to CSV
2. Use our template or map your columns
3. Import all incidents at once
4. System automatically adds resolved incidents to KB
5. Unresolved incidents can be resolved using RAG suggestions

### Example 2: Update Knowledge Base

1. Resolve incidents over time
2. Export resolved incidents monthly
3. Import them using CSV import
4. Knowledge base automatically grows with proven solutions
5. Future incidents benefit from larger resolution dataset

### Example 3: Merge Multiple Systems

1. Export incidents from multiple ticketing systems
2. Combine into single CSV
3. Standardize column names
4. Import to unified knowledge base
5. Use RAG across all historical data

## FAQ

**Q: Can I import duplicate incident numbers?**  
A: No, duplicates are skipped with a warning. Delete or update existing incidents first.

**Q: What if my CSV has extra columns?**  
A: Extra columns are ignored. Only mapped columns are processed.

**Q: Can I import without resolution notes?**  
A: Yes, but they won't be added to the knowledge base. You can resolve them later using RAG suggestions.

**Q: How does RAG suggestion work during import?**  
A: For each unresolved incident, RAG finds similar resolved incidents from the knowledge base and suggests the best matching resolution.

**Q: Can I re-import the same data?**  
A: Not with duplicate numbers. You'd need to update or delete existing incidents first.

**Q: How do I handle date formats?**  
A: The system auto-detects common date formats (YYYY-MM-DD, MM/DD/YYYY, etc.). Include dates in a standard format.

## Troubleshooting

### Issue: Import seems slow
- **Solution**: Large files (1000+ rows) may take time. Patient for the processing to complete.

### Issue: Some incidents didn't import
- **Check**: Error/warning messages in import results. Missing required fields are common causes.

### Issue: Knowledge base not updated
- **Check**: Ensure incidents have resolution notes with 30+ characters.

### Issue: RAG suggestions not working
- **Check**: Knowledge base must have some resolved incidents first. Import those first, then use RAG.

## Next Steps

After importing incidents:

1. ✅ Review imported incidents in Knowledge Base
2. ✅ Resolve unresolved incidents using RAG
3. ✅ Use incidents for single incident SOP generation
4. ✅ Generate batch SOPs from similar incidents
5. ✅ Share SOPs with your team

For more information, see:
- [README.md](README.md) - Main documentation
- [QUICK_TEST.html](QUICK_TEST.html) - Quick test interface
- [API.md](docs/API.md) - API documentation
