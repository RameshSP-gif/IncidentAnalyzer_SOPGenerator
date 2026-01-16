# Quick Start Guide - MongoDB Integration

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Start MongoDB

**Windows (if MongoDB is installed locally):**
```bash
net start MongoDB
```

**Or use MongoDB Atlas** (cloud - free tier available):
- Sign up at https://www.mongodb.com/atlas
- Create free cluster
- Get connection string
- Set environment variable:
  ```bash
  set MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
  ```

### Step 3: Import Sample Data

```bash
python import_csv.py sample_incidents.csv
```

Expected output:
```
========================================================
CSV IMPORT RESULTS
========================================================
Total Records: 20
Successfully Imported: 20
Skipped (duplicates): 0
Errors: 0
========================================================

Total Incidents in Database: 20
Categories: Email, Network, Hardware, Access, Software, Database
```

### Step 4: Launch Web Application

```bash
python web_app.py
```

Expected output:
```
======================================================================
SOP Generator Web Application Starting with MongoDB Integration...
======================================================================

MongoDB Database: incident_analyzer
Total Incidents: 20
Categories: Email, Network, Hardware, Access, Software...

Access the application at: http://127.0.0.1:5000
```

### Step 5: Explore Features

#### Web Interface
Open browser: **http://127.0.0.1:5000**

Features available:
- ✅ Analyze single incidents
- ✅ Generate SOPs
- ✅ AI-powered resolution suggestions

#### MongoDB Manager
Navigate to: **http://127.0.0.1:5000/mongodb**

Features available:
- 📊 View all incidents in database
- ➕ Add new incidents
- ✏️ Edit existing incidents
- 🗑️ Delete incidents
- 🔍 Search and filter
- 📤 Import CSV files
- 📥 Export to CSV
- 🔍 Analyze and generate SOPs

### Step 6: Generate SOPs

```bash
# Analyze all incidents and generate SOPs
python main.py --from-mongodb
```

SOPs will be saved in: `output/sops/`

## 📋 Quick Commands Reference

### Import Data
```bash
# Import CSV file
python import_csv.py your_incidents.csv

# Import with custom connection
python import_csv.py incidents.csv --connection-string "mongodb://localhost:27017/"
```

### Analyze Incidents
```bash
# Analyze from MongoDB
python main.py --from-mongodb

# Analyze with limit
python main.py --from-mongodb --limit 1000

# Fetch from ServiceNow (if configured)
python main.py --fetch --days 30
```

### Web Application
```bash
# Start web server
python web_app.py

# Access at: http://127.0.0.1:5000
# MongoDB Manager: http://127.0.0.1:5000/mongodb
```

## 🎯 Common Tasks

### View All Incidents
1. Open http://127.0.0.1:5000/mongodb
2. Browse incidents with pagination
3. Use search/filter as needed

### Add New Incident
1. Click "➕ Add Incident" button
2. Fill in incident details
3. Click "💾 Save"
4. Incident is saved to MongoDB

### Import Historical Data
1. Prepare CSV file (see `sample_incidents.csv` for format)
2. Run: `python import_csv.py your_file.csv`
3. Or use web UI: Click "📤 Import CSV"

### Generate SOPs
1. Ensure you have enough incidents (10+ recommended)
2. Run: `python main.py --from-mongodb`
3. Or use web UI: Click "Analyze & Generate SOPs"
4. Check `output/sops/` for generated files

### Export Data
1. Open MongoDB Manager
2. Click "📥 Export CSV"
3. File downloads automatically

## 🔧 Configuration

### MongoDB Settings
Edit `config.yaml`:

```yaml
database:
  mongodb:
    connection_string: "mongodb://localhost:27017/"
    database_name: "incident_analyzer"
    collection_name: "incidents"
```

Or set environment variable:
```bash
set MONGODB_URI=mongodb://localhost:27017/
```

### Required CSV Columns
- `number` - Incident number (unique)
- `short_description` - Brief summary
- `description` - Detailed description
- `category` - Category (Email, Network, etc.)

### Optional CSV Columns
- `priority` (1-4)
- `resolution_notes`
- `subcategory`
- `state`
- `assignment_group`
- `assigned_to`

## ✅ Verify Installation

### Check MongoDB Connection
```python
python -c "from src.database import get_db_client; print('Connected:', get_db_client().get_incident_count(), 'incidents')"
```

### Check Web App
```bash
python web_app.py
# Open http://127.0.0.1:5000
# Should see main page without errors
```

### Check Imports
```python
python -c "from src.database import MongoDBClient; print('Import successful')"
```

## 🆘 Troubleshooting

### MongoDB Not Running
**Error**: `Connection refused`

**Fix**:
```bash
# Windows
net start MongoDB

# Check status
sc query MongoDB
```

### Import Fails
**Error**: `CSV parsing error`

**Fix**:
- Ensure CSV is UTF-8 encoded
- Check column names match required format
- Verify no special characters in data

### Web App Won't Start
**Error**: `Port already in use`

**Fix**:
```bash
# Kill process using port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or change port in web_app.py:
app.run(debug=True, host='127.0.0.1', port=5001)
```

## 📚 Next Steps

1. **Import Your Data**: Prepare CSV with your incident data
2. **Explore Features**: Try all CRUD operations
3. **Generate SOPs**: Run analysis on your data
4. **Customize**: Adjust categories, priorities, etc.
5. **Integrate**: Connect to ServiceNow for live data

## 📖 Full Documentation

See comprehensive guide: [MONGODB_GUIDE.md](MONGODB_GUIDE.md)

## 🎉 Success!

You now have:
- ✅ MongoDB database with incident storage
- ✅ Web interface for management
- ✅ CSV import/export functionality
- ✅ Incident analysis and SOP generation
- ✅ Full CRUD operations
- ✅ Search and filtering

Happy analyzing! 🚀
