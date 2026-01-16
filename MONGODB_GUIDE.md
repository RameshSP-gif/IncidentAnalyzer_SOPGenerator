# MongoDB Integration Guide

## Overview

The Incident Analyzer SOP Creator now includes full MongoDB integration for persistent incident storage, CSV import, and complete CRUD operations.

## Features

### 1. MongoDB Database Backend
- **Persistent Storage**: All incidents are stored in MongoDB
- **Automatic Indexing**: Optimized queries with indexes on key fields
- **Full Text Search**: Search incidents by description, resolution, etc.
- **Category & Priority Filtering**: Filter incidents by category and priority

### 2. CSV Import/Export
- **Bulk Import**: Import thousands of incidents from CSV files
- **Duplicate Detection**: Automatically skips duplicate incidents
- **Export Functionality**: Export all incidents to CSV format
- **Field Mapping**: Flexible field mapping for different CSV formats

### 3. CRUD Operations
- **Create**: Add new incidents via web UI or API
- **Read**: View all incidents with pagination
- **Update**: Edit existing incident details
- **Delete**: Remove incidents from database
- **Search**: Advanced search with filters

### 4. Incident Analysis
- **Always Uses MongoDB**: Analyzer reads directly from MongoDB
- **Real-time Analysis**: Analyze all stored incidents
- **SOP Generation**: Generate SOPs from MongoDB incidents
- **RAG Integration**: Knowledge base populated from MongoDB

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `pymongo>=4.6.0` - MongoDB driver
- `motor>=3.3.0` - Async MongoDB driver

### 2. Setup MongoDB

#### Option A: Local MongoDB
```bash
# Install MongoDB (Windows)
choco install mongodb

# Start MongoDB service
net start MongoDB
```

#### Option B: MongoDB Atlas (Cloud)
1. Create account at https://www.mongodb.com/atlas
2. Create a free cluster
3. Get connection string
4. Update `.env` file:

```bash
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
```

### 3. Configure Database

Edit `config.yaml`:

```yaml
database:
  mongodb:
    connection_string: "mongodb://localhost:27017/"
    database_name: "incident_analyzer"
    collection_name: "incidents"
```

Or use environment variable:
```bash
MONGODB_URI=mongodb://localhost:27017/
```

## Usage

### Web Interface

#### 1. Start the Web Application

```bash
python web_app.py
```

Access at: http://127.0.0.1:5000

#### 2. MongoDB Manager Interface

Navigate to: http://127.0.0.1:5000/mongodb

Features:
- 📊 **Dashboard**: View statistics (total incidents, categories, recent)
- 📤 **Import CSV**: Upload CSV files with incident data
- 📥 **Export CSV**: Download all incidents as CSV
- ➕ **Add Incident**: Create new incident manually
- ✏️ **Edit**: Update existing incidents
- 🗑️ **Delete**: Remove incidents
- 🔍 **Search**: Filter by text, category, priority
- 📄 **Pagination**: Navigate large datasets

### Command Line Interface

#### 1. Import CSV File

```bash
python import_csv.py incidents.csv
```

With custom connection:
```bash
python import_csv.py incidents.csv --connection-string "mongodb://localhost:27017/"
```

#### 2. Analyze MongoDB Incidents

```bash
# Analyze all incidents from MongoDB
python main.py --from-mongodb

# Analyze with limit
python main.py --from-mongodb --limit 1000
```

#### 3. Fetch from ServiceNow and Store in MongoDB

```bash
# Fetch incidents and save to MongoDB
python main.py --fetch --days 90 --limit 500
```

### Python API

```python
from src.database import get_db_client

# Initialize database client
db_client = get_db_client()

# Add incident
incident = {
    "number": "INC0001",
    "short_description": "Email not working",
    "description": "User cannot send emails",
    "category": "Email",
    "priority": "2",
    "resolution_notes": "Reset email client settings"
}
db_client.insert_incident(incident)

# Get all incidents
incidents = db_client.get_all_incidents(limit=100)

# Search incidents
results = db_client.search_incidents(
    query="email",
    category="Email",
    priority="2"
)

# Update incident
db_client.update_incident("INC0001", {
    "resolution_notes": "Updated resolution"
})

# Delete incident
db_client.delete_incident("INC0001")

# Get statistics
total = db_client.get_incident_count()
categories = db_client.get_categories()
```

## CSV Import Format

### Required Columns

| Column | Description | Required |
|--------|-------------|----------|
| `number` | Incident number (unique) | Yes |
| `short_description` | Brief summary | Yes |
| `description` | Detailed description | Yes |
| `category` | Incident category | Yes |

### Optional Columns

| Column | Description | Default |
|--------|-------------|---------|
| `priority` | Priority (1-4) | 3 |
| `subcategory` | Sub-category | "" |
| `state` | Incident state | "Closed" |
| `resolution_notes` | Resolution details | "" |
| `close_notes` | Closing notes | "" |
| `work_notes` | Work notes | "" |
| `assignment_group` | Assigned group | "" |
| `assigned_to` | Assigned person | "" |
| `sys_created_on` | Creation date | Now |
| `sys_updated_on` | Update date | Now |

### Example CSV

```csv
number,short_description,description,category,priority,resolution_notes
INC0001,Email not working,User cannot send emails,Email,2,Reset email client
INC0002,Slow network,Network is very slow,Network,3,Restarted network switch
INC0003,Computer won't boot,Desktop computer won't start,Hardware,1,Replaced power supply
```

## API Endpoints

### Incident Management

#### Get All Incidents
```
GET /get_incidents?page=1&per_page=100
```

Response:
```json
{
  "success": true,
  "incidents": [...],
  "count": 100,
  "total": 5000,
  "page": 1,
  "per_page": 100
}
```

#### Add Incident
```
POST /add_incident
Content-Type: application/json

{
  "incident_number": "INC0001",
  "short_description": "Issue summary",
  "description": "Detailed description",
  "category": "Email",
  "priority": "3",
  "resolution_notes": "Resolution"
}
```

#### Update Incident
```
PUT /update_incident/INC0001
Content-Type: application/json

{
  "short_description": "Updated summary",
  "resolution_notes": "Updated resolution"
}
```

#### Delete Incident
```
DELETE /delete_incident/INC0001
```

#### Search Incidents
```
POST /search_incidents
Content-Type: application/json

{
  "query": "email",
  "category": "Email",
  "priority": "2"
}
```

#### Import CSV
```
POST /import_csv
Content-Type: multipart/form-data

file: <CSV file>
```

#### Export CSV
```
GET /export_csv
```

#### Get Statistics
```
GET /get_stats
```

Response:
```json
{
  "success": true,
  "total_incidents": 5000,
  "categories": ["Email", "Network", "Hardware"],
  "category_count": 3,
  "recent_incidents": [...]
}
```

### Analysis & SOP Generation

#### Generate SOPs from MongoDB
```
POST /generate_sop
```

Response:
```json
{
  "success": true,
  "total_incidents": 5000,
  "clusters": 12,
  "sops": [
    {
      "cluster_id": 0,
      "category": "Email",
      "incident_count": 450,
      "content": "# SOP...",
      "analysis": {...}
    }
  ]
}
```

## Database Schema

### Incident Collection

```javascript
{
  _id: ObjectId("..."),
  number: "INC0001",                    // Unique incident number (indexed)
  short_description: "Email not working",
  description: "User cannot send emails",
  category: "Email",                    // Indexed
  subcategory: "Outlook",
  priority: "2",                        // Indexed
  state: "Closed",
  resolution_notes: "Reset email client settings",
  close_notes: "",
  work_notes: "",
  assignment_group: "IT Support",
  assigned_to: "John Doe",
  sys_created_on: "2026-01-12T10:00:00",  // Indexed (desc)
  sys_updated_on: "2026-01-12T11:00:00",
  resolved_at: "2026-01-12T11:00:00"
}
```

### Indexes

1. **Unique Index**: `number` (unique constraint)
2. **Category Index**: `category` (filtering)
3. **Priority Index**: `priority` (filtering)
4. **Date Index**: `sys_created_on` (descending, for sorting)
5. **Text Index**: `short_description`, `description`, `resolution_notes` (full-text search)

## Workflow

### 1. Import Historical Data

```bash
# Import CSV with historical incidents
python import_csv.py historical_incidents.csv

# Verify import
python -c "from src.database import get_db_client; print(get_db_client().get_incident_count())"
```

### 2. Analyze and Generate SOPs

```bash
# Analyze incidents from MongoDB
python main.py --from-mongodb

# This will:
# 1. Load all incidents from MongoDB
# 2. Validate incident data
# 3. Categorize using ML clustering
# 4. Generate SOPs for each cluster
```

### 3. Ongoing Management

```bash
# Start web application
python web_app.py

# Navigate to http://127.0.0.1:5000/mongodb
# - View all incidents
# - Add/Edit/Delete incidents
# - Import new CSV files
# - Export data
# - Generate SOPs
```

### 4. Continuous Updates

```bash
# Fetch new incidents from ServiceNow
python main.py --fetch --days 7

# Incidents are automatically saved to MongoDB
# Then analyze and generate SOPs
python main.py --from-mongodb
```

## Troubleshooting

### MongoDB Connection Issues

**Error**: `Connection refused`

**Solution**:
```bash
# Check if MongoDB is running
net start MongoDB

# Or check service status
sc query MongoDB
```

**Error**: `Authentication failed`

**Solution**: Update connection string in `.env`:
```bash
MONGODB_URI=mongodb://username:password@localhost:27017/
```

### Import Issues

**Error**: `Duplicate key error`

**Solution**: Incident numbers must be unique. The import will skip duplicates automatically.

**Error**: `CSV parsing error`

**Solution**: Ensure CSV has proper formatting:
- UTF-8 encoding
- Headers in first row
- Required columns present

### Performance Issues

**Slow queries**: Ensure indexes are created (automatic on first run)

**Large datasets**: Use pagination:
```python
incidents = db_client.get_all_incidents(skip=0, limit=100)
```

## Best Practices

1. **Regular Backups**: Export CSV regularly
   ```bash
   curl http://localhost:5000/export_csv -o backup_$(date +%Y%m%d).csv
   ```

2. **Validate Data**: Use the validator before importing
   ```python
   from src.data_validation import DataValidator
   validator = DataValidator(...)
   valid, invalid = validator.validate_incidents(incidents)
   ```

3. **Monitor Database Size**: Check collection size periodically
   ```python
   db_client.collection.count_documents({})
   ```

4. **Clean Old Data**: Archive old incidents
   ```python
   # Delete incidents older than 2 years
   from datetime import datetime, timedelta
   two_years_ago = datetime.now() - timedelta(days=730)
   db_client.collection.delete_many({
       "sys_created_on": {"$lt": two_years_ago.isoformat()}
   })
   ```

5. **Use Categories**: Standardize category names for better clustering

## Advanced Features

### Custom Queries

```python
# Get high-priority unresolved incidents
high_priority = list(db_client.collection.find({
    "priority": {"$in": ["1", "2"]},
    "resolution_notes": {"$exists": False}
}))

# Get incidents by date range
from datetime import datetime, timedelta
last_week = datetime.now() - timedelta(days=7)
recent = list(db_client.collection.find({
    "sys_created_on": {"$gte": last_week.isoformat()}
}))

# Aggregation pipeline
category_counts = list(db_client.collection.aggregate([
    {"$group": {"_id": "$category", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
]))
```

### Batch Operations

```python
# Batch update
from pymongo import UpdateMany
db_client.collection.bulk_write([
    UpdateMany(
        {"category": "Email"},
        {"$set": {"assignment_group": "Email Team"}}
    )
])
```

## Migration from File-Based Storage

If you have existing JSON files:

```python
import json
from src.database import get_db_client

db_client = get_db_client()

# Load from JSON file
with open('data/incidents/incidents_20260112.json', 'r') as f:
    incidents = json.load(f)

# Import to MongoDB
count = db_client.insert_many_incidents(incidents)
print(f"Migrated {count} incidents")
```

## Support

For issues or questions:
1. Check logs: `logs/app.log`
2. Verify MongoDB connection: `python -c "from src.database import get_db_client; get_db_client()"`
3. Review configuration: `config.yaml`

## License

Same as main project
