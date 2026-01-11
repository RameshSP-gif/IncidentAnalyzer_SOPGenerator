# MongoDB Integration Flow & Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Application (Flask)                   │
│                      (web_app.py)                            │
└────────────────────────────────────────────────────────────┘
                              │
                              ├──────────────────┬──────────────────┐
                              ▼                  ▼                  ▼
                    ┌──────────────────┐ ┌──────────────┐ ┌──────────────┐
                    │  CSV Importer    │ │ RAG Resolver │ │ API Handlers │
                    │                  │ │              │ │              │
                    │ Parses & Imports │ │ Suggests     │ │ CRUD + Search│
                    │ from CSV         │ │ Resolutions  │ │ Operations   │
                    └──────────────────┘ └──────────────┘ └──────────────┘
                              │                  │                  │
                              └──────────────────┴──────────────────┘
                                                 │
                              ┌──────────────────▼──────────────────┐
                              │   MongoDB Handler (Database Layer)   │
                              │     (src/db/mongodb_handler.py)      │
                              │                                      │
                              │  - Connection Management             │
                              │  - CRUD Operations                   │
                              │  - Index Management                  │
                              │  - Error Handling                    │
                              │  - Fallback Logic                    │
                              └──────────────────┬──────────────────┘
                                                 │
                         ┌───────────────────────┴───────────────────┐
                         ▼                                           ▼
                    ┌─────────────────┐                    ┌─────────────────┐
                    │  MongoDB        │                    │  JSON File      │
                    │  (Primary)      │                    │  (Fallback)     │
                    │                 │                    │                 │
                    │ incident_       │                    │ data/           │
                    │ analyzer.       │                    │ knowledge_      │
                    │ knowledge_base  │                    │ base.json       │
                    └─────────────────┘                    └─────────────────┘
```

## Data Flow Diagrams

### CSV Import Flow (MongoDB Path)

```
User uploads CSV
      │
      ▼
CSV Importer
  - Parse CSV
  - Validate incidents
  - Enrich with metadata
      │
      ▼
add_to_knowledge_base()
      │
      ├─ Has MongoDB URI? ───Yes──┐
      │                           │
      No ┌──────────────────────┘
      │  ▼
      │ MongoDB Handler
      │  - add_incident()
      │  - add_incidents_batch()
      │  - Create indexes
      │  - Log operation
      │
      ▼ (if MongoDB fails)
Fallback to JSON
  - Save to knowledge_base.json
  - Update incidents_db
      │
      ▼
Return response
  - count_added
  - errors
  - storage_type ("MongoDB" or "JSON")
```

### Resolution Finder Flow (RAG Path)

```
User requests resolution
      │
      ▼
get_resolution_finder()
      │
      ▼
ResolutionFinder.load_knowledge_base()
      │
      ├─ Has MongoDB handler? ───Yes──┐
      │                                │
      │ No ┌─────────────────────┘
      │    ▼
      │ MongoDB.get_resolved_incidents()
      │    │
      │    ├─ Query: resolution_notes exists
      │    ├─ Filter: length > 30 chars
      │    └─ Load embeddings
      │
      ▼ (if MongoDB unavailable)
Provided incidents list?
      │
      Yes ─────────┐
      No          │
      │           ▼
      └──> JSON file fallback
            - Load knowledge_base.json
            - Filter resolved incidents
            - Create embeddings
            │
            ▼
Load embeddings into cache
      │
      ▼
Ready for similarity search
```

### Search & Query Flow

```
Search Request
  - Query: "database error"
  - Category: "Database"
      │
      ▼
get_mongodb_handler()
      │
      ├─ Connected? ───Yes──┐
      │                     │
      No                    ▼
      │            MongoDB text search
      │            - Full-text index
      │            - Category filter
      │            - Return results
      │
      └──> JSON Fallback
           - Load knowledge_base.json
           - String matching
           - Category filter
           - Return results
      │
      ▼
Return results with:
  - incidents array
  - count
  - storage_type
```

## Detailed Component Interactions

### MongoDB Handler Class

**Initialization:**
```python
handler = MongoDBHandler(uri='mongodb://localhost:27017')
# ├─ Connect to MongoDB
# ├─ Select database: incident_analyzer
# ├─ Get collection: knowledge_base
# ├─ Create indexes (number, category, priority, text)
# └─ Set connected=True
```

**CRUD Operations:**
```
CREATE:
handler.add_incident(incident) → MongoDB insert
handler.add_incidents_batch(incidents) → MongoDB bulk insert

READ:
handler.get_all_incidents() → Query all
handler.get_incident_by_number('INC001') → Indexed lookup
handler.get_resolved_incidents() → Filter query

UPDATE:
handler.update_incident('INC001', {'status': 'resolved'})
  └─ Uses index for fast lookup
  └─ Partial update support

DELETE:
handler.delete_incident('INC001')
  └─ Indexed deletion
  └─ Verifies deletion
```

**Special Operations:**
```
SEARCH:
handler.search_incidents('database error')
  └─ Text index search
  └─ Returns sorted by relevance

STATISTICS:
handler.get_statistics()
  └─ Aggregation pipeline
  └─ Returns: count, categories, priorities, resolutions
```

### CSV Importer Integration

**Before (JSON only):**
```python
incidents = csv_importer.import_from_csv(filepath)
kb_file = Path('data/knowledge_base.json')
importer.add_to_knowledge_base(incidents, str(kb_file))
# ├─ Load JSON file
# ├─ Check for duplicates
# ├─ Append incidents
# ├─ Save JSON file
# └─ Return count
```

**After (MongoDB + JSON fallback):**
```python
incidents = csv_importer.import_from_csv(filepath)
importer.add_to_knowledge_base(
    incidents,
    mongodb_uri='mongodb://localhost:27017',
    kb_file_path=Path('data/knowledge_base.json')
)
# ├─ Check MongoDB URI provided
# ├─ Try MongoDB first (if available)
# │  ├─ Initialize handler if needed
# │  ├─ Batch insert incidents
# │  └─ Return count
# └─ Fallback to JSON (if MongoDB fails)
#    ├─ Load JSON file
#    ├─ Append incidents
#    ├─ Save JSON file
#    └─ Return count
```

### RAG Resolution Engine Integration

**Before (JSON only):**
```python
resolver = ResolutionFinder()
resolver.load_knowledge_base()
# ├─ Load from provided incidents
# └─ Or load JSON file
# └─ Create embeddings cache
```

**After (MongoDB + JSON fallback):**
```python
resolver = ResolutionFinder(mongodb_uri='mongodb://localhost:27017')
resolver.load_knowledge_base()
# ├─ Check MongoDB available
# ├─ Try MongoDB.get_resolved_incidents()
# │  └─ Filtered query: resolution_notes exists & length > 30
# ├─ Fallback: Use provided incidents list
# └─ Fallback: Load from JSON file
# └─ Create embeddings cache
```

## Web API Endpoint Integration

### Import CSV Endpoint

**Before:**
```
POST /import_csv
├─ Parse CSV file
├─ Save to local incidents_db
├─ Add to knowledge_base.json
└─ Response: {count_added, errors}
```

**After:**
```
POST /import_csv
├─ Parse CSV file
├─ Save to local incidents_db
├─ MongoDB Handler: add_to_knowledge_base()
│  ├─ Try MongoDB batch insert
│  └─ Fallback to JSON file write
└─ Response: {
    count_added,
    storage: "MongoDB" | "JSON",
    errors
   }
```

### Batch Resolve Endpoint

**Before:**
```
POST /batch_resolve_incidents
├─ Load knowledge_base.json
├─ Find incidents by number
├─ Use RAG to suggest resolutions
├─ Update JSON file
└─ Response: {updated_count}
```

**After:**
```
POST /batch_resolve_incidents
├─ MongoDB: get_all_incidents() or JSON fallback
├─ Find incidents by number
├─ Use RAG to suggest resolutions
├─ MongoDB: update_incident() for each
├─ Sync to JSON file (backup)
└─ Response: {
    updated_count,
    storage: "MongoDB" | "JSON",
    message
   }
```

### Get Knowledge Base Endpoint

**Before:**
```
GET /get_knowledge_base
├─ Load JSON file
└─ Response: {incidents, count}
```

**After:**
```
GET /get_knowledge_base
├─ MongoDB Handler: get_all_incidents()
├─ Fallback: Load JSON file
└─ Response: {
    incidents,
    count,
    storage: "MongoDB" | "JSON"
   }
```

## Error Handling & Recovery

### Connection Failure Scenario

```
Application Start
      │
      ▼
Initialize MongoDB Handler
      │
      ├─ Can connect to MongoDB? ───Yes──→ Set mongodb_handler ✓
      │
      No ─────────────────────────┐
      │                           │
      └────────────────────────────┤
                                   ▼
                        Print warning message
                        ⚠ "MongoDB connection failed"
                        ⚠ "Will use JSON fallback"
                        ▼
                    Set mongodb_handler = None
                    ▼
                Use JSON file for all operations
                    ✓ Application continues normally
```

### Operation Failure Recovery

```
User Action (e.g., CSV Import)
      │
      ▼
Try MongoDB Operation
      │
      ├─ Success ──────────────┐
      │                        │
      Fail                     ▼
      │                    Return result
      ▼                   storage: "MongoDB"
Try JSON Fallback
      │
      ├─ Success ──────────────┐
      │                        │
      Fail                     ▼
      │                    Return result
      └──────────────────>    storage: "JSON"
                              
                         Both fail:
                         Return error
                         Suggest troubleshoot
```

## Data Consistency

### Sync Strategy

```
Primary Operation (MongoDB)
      │
      ├─ Add incident ──────┐
      ├─ Update incident ───┤─── Success
      ├─ Delete incident ───┤
      └─ Search incident ───┤
                            ▼
                    Sync to JSON (backup)
                    ├─ Export from MongoDB
                    ├─ Save to knowledge_base.json
                    └─ Both sources consistent
```

### Conflict Resolution

```
User edits incident
      │
      ├─ MongoDB updated ✓
      ├─ JSON sync ✓
      └─ Source: MongoDB (primary authority)
      
If MongoDB fails:
      ├─ Fall back to JSON
      ├─ JSON updated ✓
      └─ Source: JSON (temporary)
      
When MongoDB returns:
      ├─ Sync missed updates from JSON
      ├─ MongoDB updated ✓
      └─ Source: MongoDB (restored authority)
```

## Performance Characteristics

### Operation Complexity

| Operation | MongoDB | JSON | Notes |
|-----------|---------|------|-------|
| Insert single | O(1) | O(n) | Indexed insert vs list append |
| Insert batch | O(n) | O(n) | Bulk operation vs loop |
| Find by ID | **O(1)** | O(n) | Index vs linear search |
| Search text | **O(indexed)** | O(n) | Text index vs string matching |
| Filter by category | **O(log n)** | O(n) | Index vs linear scan |
| Update incident | **O(1)** | O(n) | Indexed update vs rewrite |
| Delete incident | **O(1)** | O(n) | Indexed delete vs filter |
| Load all | O(n) | O(n) | Network transfer vs file I/O |

### Throughput

```
CSV Import (1000 incidents):
  MongoDB:  ~500-1000 incidents/sec (bulk insert)
  JSON:     ~100-200 incidents/sec (file I/O)
  
Search (10k incidents):
  MongoDB:  <50ms (indexed)
  JSON:     ~200-500ms (linear scan)
  
Concurrent imports:
  MongoDB:  Unlimited
  JSON:     Serialized (file lock)
```

## Security Considerations

### Authentication (Optional)

```python
# Default (no auth):
mongodb_uri = "mongodb://localhost:27017"

# With authentication:
mongodb_uri = "mongodb://user:password@host:27017"

# Atlas (cloud):
mongodb_uri = "mongodb+srv://user:password@cluster.mongodb.net/"

# All methods supported via environment variable
MONGODB_URI = os.environ.get('MONGODB_URI')
```

### Data Privacy

```
JSON File:
  └─ Plain text (human readable)
  └─ Keep in secure location
  └─ Consider encryption at rest

MongoDB:
  └─ Local: No encryption needed for development
  └─ Production: Use MongoDB encryption at rest
  └─ Network: Use MongoDB Atlas for TLS/SSL
  └─ Authentication: Enable user accounts
```

## Summary

✅ **Seamless integration** of MongoDB with JSON fallback
✅ **Zero downtime** if MongoDB unavailable
✅ **Automatic indexing** for performance
✅ **Batch operations** optimized
✅ **Error recovery** with graceful degradation
✅ **Data consistency** via sync strategy
✅ **Security** options for production

---

**Last Updated:** January 2024
**MongoDB Version:** 4.0+
**Python Driver:** PyMongo 4.0+
