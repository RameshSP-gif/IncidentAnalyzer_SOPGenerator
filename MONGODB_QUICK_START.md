# MongoDB Quick Start Guide

## 5-Minute Setup

### Step 1: Install MongoDB (Choose Your OS)

**Windows:**
1. Download from [MongoDB Community Edition](https://www.mongodb.com/download-center/community)
2. Run installer, follow prompts
3. MongoDB will auto-start

**macOS:**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y mongodb
sudo systemctl start mongod
```

### Step 2: Verify MongoDB is Running

```bash
mongosh
# Should open MongoDB shell
# Type: exit  to close
```

### Step 3: Start the Application

```bash
cd /path/to/IncidentAnalyzer_SOPGenerator
python web_app.py
```

**Expected Output:**
```
✓ MongoDB connected successfully
SOP Generator Web Application Starting...
Access the application at: http://127.0.0.1:5000
```

### Step 4: Test MongoDB Integration

1. Open http://127.0.0.1:5000
2. Go to **CSV Import** tab
3. Upload a CSV file with incidents
4. Check response - should show:
   - ✅ `"storage": "MongoDB"`
   - ✅ `"added_to_kb": X incidents`

5. Go to **Knowledge Base** section
6. Verify incidents are stored and searchable

## Understanding the Hybrid Storage

### MongoDB (Primary)
- **Automatic:** Used when available
- **Benefits:** Fast, scalable, concurrent access
- **Configuration:** `mongodb://localhost:27017` (default)

### JSON File (Fallback)
- **Automatic:** Kicks in if MongoDB unavailable
- **Location:** `data/knowledge_base.json`
- **Benefits:** Backward compatible, human-readable

### Example Scenario

**Scenario 1: MongoDB Running**
```
CSV Import → MongoDB ✓ (faster, scalable)
                ↓
              Response includes "storage": "MongoDB"
```

**Scenario 2: MongoDB Down**
```
CSV Import → MongoDB ✗ → Fallback to JSON ✓
                              ↓
                   Response includes "storage": "JSON"
                   Application continues working!
```

## Configuration

### Default Configuration
```
MongoDB URI: mongodb://localhost:27017
Database: incident_analyzer
Collection: knowledge_base
```

### Custom MongoDB URI (Optional)

**Windows:**
```powershell
$env:MONGODB_URI = "mongodb://username:password@host:27017"
python web_app.py
```

**macOS/Linux:**
```bash
export MONGODB_URI="mongodb://username:password@host:27017"
python web_app.py
```

**Examples:**
```
# Local
mongodb://localhost:27017

# Remote server
mongodb://db-server.example.com:27017

# With authentication
mongodb://user:password@db-server.example.com:27017

# Atlas cloud
mongodb+srv://user:password@cluster.mongodb.net/
```

## Commands to Know

### Check MongoDB Status
```bash
# Check if running
mongosh --eval "db.version()"

# View all databases
mongosh --eval "show dbs"

# View incident analyzer database
mongosh
> use incident_analyzer
> db.knowledge_base.countDocuments()
> db.knowledge_base.find().limit(3)
```

### View Incident Data
```bash
mongosh
> use incident_analyzer
> db.knowledge_base.find({number: "INC001"})
```

### Clear Knowledge Base (if needed)
```bash
mongosh
> use incident_analyzer
> db.knowledge_base.deleteMany({})  # ⚠ Deletes all!
```

### View Indexes
```bash
mongosh
> use incident_analyzer
> db.knowledge_base.getIndexes()
```

## Troubleshooting

### Error: "Connection refused"

**Problem:** MongoDB not running

**Solution:**
```bash
# Windows: Check Services
#   Look for "MongoDB" service

# macOS:
brew services start mongodb-community

# Linux:
sudo systemctl start mongod
sudo systemctl status mongod
```

### Error: "Already in use on port 27017"

**Problem:** Another MongoDB instance is running

**Solution:**
```bash
# Linux:
sudo lsof -i :27017
sudo kill -9 <PID>

# macOS:
lsof -i :27017
kill -9 <PID>

# Windows: Use Task Manager
#   End mongod.exe process
```

### Application Using JSON Instead of MongoDB

**Problem:** Seeing `"storage": "JSON"` in responses

**Solutions:**
1. Check MongoDB is running: `mongosh`
2. Check logs for connection error message
3. Verify MONGODB_URI environment variable (if custom)
4. Restart application after MongoDB starts

### MongoDB Taking Space

**View database size:**
```bash
mongosh
> use incident_analyzer
> db.stats()
```

**Backup and cleanup:**
```bash
# Backup (safe)
mongodump --db incident_analyzer --out ./backup/

# Delete old data
mongosh
> use incident_analyzer
> db.knowledge_base.deleteMany({created_at: {$lt: new Date('2024-01-01')}})
```

## Performance Tips

### Enable Proper Indexing
MongoDB handler creates indexes automatically:
- Incident number lookup: **O(1) instant**
- Category search: **O(log n) indexed**
- Full-text search: **O(indexed) fast**

### Optimize Batch Imports
```python
# CSV importer uses batch insert
# Uploads 1000s of incidents efficiently
# No need to optimize - it's built-in
```

### Monitor Performance
```bash
# Check current connections
mongosh
> use admin
> db.currentOp()

# View operation times
# (for optimization analysis)
```

## Common Questions

### Q: Will my existing JSON files be deleted?
**A:** No! They're kept as backup. New imports go to MongoDB.

### Q: Can I use only JSON and skip MongoDB?
**A:** Yes! Don't install MongoDB. JSON fallback works automatically.

### Q: How do I migrate from JSON to MongoDB?
**A:** Just import your incidents CSV again. MongoDB will be used automatically.

### Q: Is my data safe in MongoDB?
**A:** Yes! Incidents are auto-indexed and backed up to JSON file.

### Q: Can I use MongoDB Atlas (cloud)?
**A:** Yes! Set `MONGODB_URI` to your Atlas connection string.

### Q: What about data size limits?
**A:** MongoDB free tier supports unlimited documents. No limits for your use case.

## Next Steps

1. ✅ MongoDB running
2. ✅ Application started
3. 👉 Import some CSV incidents
4. 👉 Test batch resolution
5. 👉 Generate SOPs from MongoDB KB

**Ready? Start using the application at http://127.0.0.1:5000**

## Support

For issues or questions:
1. Check `MONGODB_MIGRATION.md` for detailed docs
2. Look for error messages in application logs
3. Verify MongoDB with `mongosh` command
4. Check environment variables: `echo $MONGODB_URI`

---

**Last Updated:** January 2024
**Status:** Production Ready
