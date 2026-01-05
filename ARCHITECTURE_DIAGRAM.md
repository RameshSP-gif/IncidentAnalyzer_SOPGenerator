# Incident Analyzer & SOP Generator - Architecture Diagrams

## 1. Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                    USER LAYER                                        │
│                                                                                      │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────────────────┐ │
│  │  IT Support      │    │  System Admin    │    │  ServiceNow Platform         │ │
│  │  Technician      │    │  (KB Manager)    │    │  (External System)           │ │
│  │                  │    │                  │    │                              │ │
│  │  • Create SOP    │    │  • Manage KB     │    │  • Incident Table            │ │
│  │  • Get AI help   │    │  • CRUD ops      │    │  • Resolved tickets          │ │
│  │  • Download PDF  │    │  • Import data   │    │  • REST API access           │ │
│  └────────┬─────────┘    └────────┬─────────┘    └──────────────┬───────────────┘ │
│           │                       │                               │                  │
└───────────┼───────────────────────┼───────────────────────────────┼──────────────────┘
            │                       │                               │
            │ HTTPS                 │ HTTPS                         │ REST API
            │                       │                               │
┌───────────▼───────────────────────▼───────────────────────────────▼──────────────────┐
│                           PRESENTATION LAYER                                          │
│                          (Frontend - Browser)                                         │
│                                                                                       │
│  ┌────────────────────────────────────────────────────────────────────────────────┐ │
│  │                        HTML5 + CSS3 + JavaScript                                │ │
│  │                                                                                 │ │
│  │  ┌───────────────────┐  ┌───────────────────┐  ┌──────────────────────────┐  │ │
│  │  │  Main Interface   │  │  Management UI    │  │  PDF Export Module       │  │ │
│  │  │  (index.html)     │  │  (manage.html)    │  │  (html2pdf.js)          │  │ │
│  │  │                   │  │                   │  │                          │  │ │
│  │  │  • Incident Form  │  │  • Data Table     │  │  • Client-side PDF gen  │  │ │
│  │  │  • AI Button      │  │  • Search/Filter  │  │  • A4 format            │  │ │
│  │  │  • SOP Display    │  │  • Edit Modal     │  │  • 98% quality          │  │ │
│  │  │  • Validation     │  │  • Delete Confirm │  │  • Filename pattern     │  │ │
│  │  └─────────┬─────────┘  └─────────┬─────────┘  └────────┬─────────────────┘  │ │
│  │            │                       │                      │                     │ │
│  │            └───────────────────────┼──────────────────────┘                     │ │
│  │                                    │ app.js (Frontend Logic)                    │ │
│  │                 ┌──────────────────┼──────────────────┐                        │ │
│  │                 │  • API Calls     │  • Form Handlers │                        │ │
│  │                 │  • Async/Await   │  • Toast Notify  │                        │ │
│  │                 │  • Error Handle  │  • Markdown→HTML │                        │ │
│  │                 └──────────────────┴──────────────────┘                        │ │
│  └────────────────────────────────────┬──────────────────────────────────────────┘ │
│                                        │                                             │
└────────────────────────────────────────┼─────────────────────────────────────────────┘
                                         │ RESTful API (JSON)
                                         │ POST /suggest_resolution
                                         │ POST /generate_sop
                                         │ POST /analyze_batch
                                         │ GET  /get_knowledge_base
                                         │ POST /add_to_knowledge_base
                                         │ PUT  /update_incident/:id
                                         │ DELETE /delete_incident/:id
                                         │
┌────────────────────────────────────────▼─────────────────────────────────────────────┐
│                          APPLICATION LAYER                                            │
│                     (Flask Web Server - web_app.py)                                   │
│                                                                                       │
│  ┌────────────────────────────────────────────────────────────────────────────────┐ │
│  │                        Flask Application Core                                   │ │
│  │                                                                                 │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │ │
│  │  │  Route       │  │  Request     │  │  Response    │  │  Error Handler   │  │ │
│  │  │  Handlers    │  │  Validation  │  │  Formatter   │  │  (Try/Except)    │  │ │
│  │  │              │  │              │  │              │  │                  │  │ │
│  │  │  • 14 routes │  │  • Required  │  │  • JSON      │  │  • 500 errors    │  │ │
│  │  │  • GET/POST  │  │    fields    │  │  • HTML      │  │  • Logging       │  │ │
│  │  │  • PUT/DEL   │  │  • Data type │  │  • Status    │  │  • Stack trace   │  │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────────┘  │ │
│  │                                                                                 │ │
│  │  ┌────────────────────────────────────────────────────────────────────────┐   │ │
│  │  │                    Lazy Loading Manager                                 │   │ │
│  │  │  • Loads ML models on first use (not at startup)                       │   │ │
│  │  │  • Categorizer: Loaded on /analyze_batch request                       │   │ │
│  │  │  • Resolution Finder: Loaded on /suggest_resolution request            │   │ │
│  │  │  • Startup time: 2s (instead of 15s)                                   │   │ │
│  │  └────────────────────────────────────────────────────────────────────────┘   │ │
│  └────────────────────────────────────────────────────────────────────────────────┘ │
│                                        │                                             │
└────────────────────────────────────────┼─────────────────────────────────────────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
┌───────────────────▼─────┐  ┌──────────▼─────────┐  ┌──────▼──────────────────────┐
│   BUSINESS LOGIC LAYER  │  │  BUSINESS LOGIC    │  │   BUSINESS LOGIC            │
│                         │  │       LAYER        │  │       LAYER                 │
│  ┌───────────────────┐  │  │  ┌──────────────┐  │  │  ┌────────────────────────┐ │
│  │  RAG Module       │  │  │  │  Incident    │  │  │  │  SOP Generator         │ │
│  │  (resolution_     │  │  │  │  Analyzer    │  │  │  │  Module                │ │
│  │   finder.py)      │  │  │  │  (categorizer│  │  │  │                        │ │
│  │                   │  │  │  │   .py)       │  │  │  │  • Template Engine     │ │
│  │  Class:           │  │  │  │              │  │  │  │  • Markdown Formatter  │ │
│  │  ResolutionFinder │  │  │  │  Class:      │  │  │  │  • Section Generator   │ │
│  │                   │  │  │  │  Incident    │  │  │  │  • Problem Statement   │ │
│  │  Methods:         │  │  │  │  Categorizer │  │  │  │  • Symptoms Extraction │ │
│  │  ├─ load_kb()    │  │  │  │              │  │  │  │  • Steps Formatting    │ │
│  │  ├─ encode()     │  │  │  │  Methods:    │  │  │  │  • Prevention Tips     │ │
│  │  ├─ search()     │  │  │  │  ├─ fit()    │  │  │  │  • Related Incidents   │ │
│  │  ├─ suggest()    │  │  │  │  ├─ cluster()│  │  │  │                        │ │
│  │  ├─ add_to_kb()  │  │  │  │  ├─ analyze()│  │  │  │  def generate_sop():   │ │
│  │  └─ save_kb()    │  │  │  │  └─ stats()  │  │  │  │    → Extract data      │ │
│  │                   │  │  │  │              │  │  │  │    → Apply template    │ │
│  │  Confidence:      │  │  │  │  Uses:       │  │  │  │    → Format markdown   │ │
│  │  Threshold: 60%   │  │  │  │  HDBSCAN     │  │  │  │    → Return HTML       │ │
│  └───────┬───────────┘  │  │  └──────┬───────┘  │  │  └────────────────────────┘ │
│          │              │  │         │          │  │                              │
└──────────┼──────────────┘  └─────────┼──────────┘  └──────────────────────────────┘
           │                           │
           │                           │
┌──────────▼───────────────────────────▼───────────────────────────────────────────────┐
│                          AI/ML PROCESSING LAYER                                       │
│                     (Deep Learning & Machine Learning)                                │
│                                                                                       │
│  ┌─────────────────────────────────────────────┐  ┌──────────────────────────────┐  │
│  │      Sentence-BERT (Deep Learning)          │  │   HDBSCAN (ML Clustering)    │  │
│  │      Model: all-MiniLM-L6-v2                │  │   Algorithm: Density-based   │  │
│  │                                             │  │                              │  │
│  │  Architecture:                              │  │  Configuration:              │  │
│  │  ┌─────────────────────────────────────┐   │  │  • min_cluster_size: 2       │  │
│  │  │  Input Layer                        │   │  │  • min_samples: 1            │  │
│  │  │  Text → Tokenizer                   │   │  │  • metric: cosine            │  │
│  │  │  "Email not working" → [101,2624...]│   │  │  • selection_method: eom     │  │
│  │  └────────────────┬────────────────────┘   │  │                              │  │
│  │                   │                         │  │  Process:                    │  │
│  │  ┌────────────────▼────────────────────┐   │  │  1. Receive 384-dim vectors  │  │
│  │  │  Transformer Layers (6 layers)      │   │  │  2. Calculate density        │  │
│  │  │  • Self-attention mechanism         │   │  │  3. Form clusters            │  │
│  │  │  • Multi-head attention (12 heads)  │   │  │  4. Label outliers as -1     │  │
│  │  │  • Feed-forward networks            │   │  │  5. Return cluster labels    │  │
│  │  │  • Layer normalization              │   │  │                              │  │
│  │  │  • Residual connections             │   │  │  Output:                     │  │
│  │  └────────────────┬────────────────────┘   │  │  [0, 0, 1, 1, 2, -1, 0, ...]│  │
│  │                   │                         │  │  (Cluster assignments)       │  │
│  │  ┌────────────────▼────────────────────┐   │  │                              │  │
│  │  │  Pooling Layer                      │   │  │  Stats:                      │  │
│  │  │  Mean pooling across tokens         │   │  │  • Auto cluster count        │  │
│  │  └────────────────┬────────────────────┘   │  │  • Noise detection           │  │
│  │                   │                         │  │  • 78% accuracy              │  │
│  │  ┌────────────────▼────────────────────┐   │  │  • <1s for 100 incidents     │  │
│  │  │  Output Layer                       │   │  └──────────────────────────────┘  │
│  │  │  384-dimensional embedding          │   │                                     │
│  │  │  [0.23, -0.45, 0.67, ..., 0.89]    │   │                                     │
│  │  └─────────────────────────────────────┘   │                                     │
│  │                                             │                                     │
│  │  Specifications:                            │                                     │
│  │  • Parameters: 22,713,984                   │                                     │
│  │  • Embedding Size: 384 dimensions           │                                     │
│  │  • Max Sequence Length: 256 tokens          │                                     │
│  │  • Vocabulary Size: 30,522                  │                                     │
│  │  • Processing: ~200ms per text              │                                     │
│  │  • Memory: ~90 MB loaded                    │                                     │
│  │  • Framework: PyTorch                       │                                     │
│  └─────────────────────────────────────────────┘                                     │
│                                                                                       │
│  ┌────────────────────────────────────────────────────────────────────────────────┐ │
│  │                    Cosine Similarity Calculator                                 │ │
│  │                                                                                 │ │
│  │    Formula:  similarity = cos(θ) = (A · B) / (||A|| × ||B||)                  │ │
│  │                                                                                 │ │
│  │    Where:                                                                       │ │
│  │      A, B = 384-dimensional vectors (query vs knowledge base)                  │ │
│  │      A · B = dot product (sum of element-wise multiplication)                  │ │
│  │      ||A|| = magnitude of vector A (Euclidean norm)                            │ │
│  │      ||B|| = magnitude of vector B (Euclidean norm)                            │ │
│  │                                                                                 │ │
│  │    Range: -1.0 to 1.0                                                          │ │
│  │      1.0  = Identical vectors (perfect match)                                  │ │
│  │      0.8+ = Very similar (high confidence)                                     │ │
│  │      0.6+ = Similar (threshold for suggestions)                                │ │
│  │      0.0  = Orthogonal (no similarity)                                         │ │
│  │     -1.0  = Opposite direction (rare in text)                                  │ │
│  │                                                                                 │ │
│  │    Implementation: scikit-learn cosine_similarity()                            │ │
│  │    Performance: ~300ms for 464 comparisons                                     │ │
│  └────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                       │
└───────────────────────────────────────┬───────────────────────────────────────────────┘
                                        │
                                        │ Read/Write
                                        │
┌───────────────────────────────────────▼───────────────────────────────────────────────┐
│                              DATA LAYER                                               │
│                      (Persistence & Storage)                                          │
│                                                                                       │
│  ┌──────────────────────────────────────┐  ┌──────────────────────────────────────┐ │
│  │   Knowledge Base (Persistent)        │  │   Runtime Memory (Volatile)          │ │
│  │   File: knowledge_base.json          │  │   Python Objects & Cache             │ │
│  │   Location: data/                    │  │                                      │ │
│  │                                      │  │                                      │ │
│  │   Structure:                         │  │   Contents:                          │ │
│  │   {                                  │  │   • Batch incidents (temp)           │ │
│  │     "version": "1.5",                │  │   • Analysis results (cache)         │ │
│  │     "last_updated": "2025-12-28...", │  │   • Session data                     │ │
│  │     "incident_count": 464,           │  │   • Loaded embeddings                │ │
│  │     "incidents": [                   │  │   • ServiceNow sync status           │ │
│  │       {                              │  │   • Processing queue                 │ │
│  │         "number": "INC0001",         │  │                                      │ │
│  │         "description": "...",        │  │   Lifetime:                          │ │
│  │         "category": "Email",         │  │   • Cleared on server restart        │ │
│  │         "priority": "High",          │  │   • No persistence                   │ │
│  │         "resolution_notes": "...",   │  │   • Fast access (RAM)                │ │
│  │         "embedding": [0.23, ...],    │  │                                      │ │
│  │         "sys_created_on": "...",     │  │                                      │ │
│  │         "resolved_at": "..."         │  │                                      │ │
│  │       },                             │  │                                      │ │
│  │       // ... 463 more incidents      │  │                                      │ │
│  │     ]                                │  │                                      │ │
│  │   }                                  │  │                                      │ │
│  │                                      │  │                                      │ │
│  │   Operations:                        │  │                                      │ │
│  │   • Auto-save on KB update           │  │                                      │ │
│  │   • Version control                  │  │                                      │ │
│  │   • Duplicate prevention (>95%)      │  │                                      │ │
│  │   • Embedding cache                  │  │                                      │ │
│  │   • Incremental updates              │  │                                      │ │
│  │                                      │  │                                      │ │
│  │   Size: ~15.8 MB (464 incidents)     │  │                                      │ │
│  │   Growth: +34 KB per incident        │  │                                      │ │
│  └──────────────────────────────────────┘  └──────────────────────────────────────┘ │
│                                                                                       │
└───────────────────────────────────────┬───────────────────────────────────────────────┘
                                        │
┌───────────────────────────────────────▼───────────────────────────────────────────────┐
│                        INTEGRATION LAYER                                              │
│                   (External System Connectors)                                        │
│                                                                                       │
│  ┌────────────────────────────────────────────────────────────────────────────────┐ │
│  │                    ServiceNow REST API Client                                   │ │
│  │                    Module: src/servicenow/client.py                             │ │
│  │                                                                                 │ │
│  │  Class: ServiceNowClient                                                        │ │
│  │                                                                                 │ │
│  │  Configuration:                                                                 │ │
│  │    • Instance URL: {company}.service-now.com                                   │ │
│  │    • Authentication: Basic Auth / OAuth 2.0                                    │ │
│  │    • API Version: REST API v2                                                  │ │
│  │    • Timeout: 30 seconds                                                       │ │
│  │    • Retry: 3 attempts with exponential backoff                                │ │
│  │                                                                                 │ │
│  │  Methods:                                                                       │ │
│  │  ┌──────────────────────────────────────────────────────────────────────┐     │ │
│  │  │  fetch_incidents(query, limit, offset)                               │     │ │
│  │  │    → GET /api/now/table/incident                                     │     │ │
│  │  │    → Returns: List of incident dictionaries                          │     │ │
│  │  │    → Example: fetch_incidents("state=6", limit=500)                  │     │ │
│  │  └──────────────────────────────────────────────────────────────────────┘     │ │
│  │  ┌──────────────────────────────────────────────────────────────────────┐     │ │
│  │  │  get_incident(sys_id)                                                │     │ │
│  │  │    → GET /api/now/table/incident/{sys_id}                            │     │ │
│  │  │    → Returns: Single incident details                                │     │ │
│  │  └──────────────────────────────────────────────────────────────────────┘     │ │
│  │  ┌──────────────────────────────────────────────────────────────────────┐     │ │
│  │  │  update_incident(sys_id, data)                                       │     │ │
│  │  │    → PUT /api/now/table/incident/{sys_id}                            │     │ │
│  │  │    → Updates: resolution_notes, state, etc.                          │     │ │
│  │  └──────────────────────────────────────────────────────────────────────┘     │ │
│  │  ┌──────────────────────────────────────────────────────────────────────┐     │ │
│  │  │  sync_resolved_incidents(since_timestamp)                            │     │ │
│  │  │    → Batch fetch resolved incidents since last sync                  │     │ │
│  │  │    → Transforms ServiceNow format → internal format                  │     │ │
│  │  │    → Triggers knowledge base auto-update                             │     │ │
│  │  │    → Returns: (added_count, duplicate_count, error_count)            │     │ │
│  │  └──────────────────────────────────────────────────────────────────────┘     │ │
│  │                                                                                 │ │
│  │  Data Mapping:                                                                  │ │
│  │    ServiceNow Field        →  Internal Field                                   │ │
│  │    ------------------          ---------------                                 │ │
│  │    number                  →  incident_number                                  │ │
│  │    short_description       →  short_description                                │ │
│  │    description             →  description (HTML cleaned)                       │ │
│  │    category                →  category (normalized)                            │ │
│  │    priority                →  priority (1-4)                                   │ │
│  │    close_notes             →  resolution_notes                                 │ │
│  │    sys_created_on          →  created_date (ISO format)                        │ │
│  │    resolved_at             →  resolved_date (ISO format)                       │ │
│  │    assigned_to.name        →  assigned_to                                      │ │
│  │    impact                  →  impact                                           │ │
│  │                                                                                 │ │
│  │  Sync Schedule:                                                                 │ │
│  │    • Frequency: Every 6 hours (configurable)                                   │ │
│  │    • Method: Cron job / Task Scheduler                                         │ │
│  │    • Query: state=6^resolved_at>=LAST_SYNC_TIME                                │ │
│  │    • Batch Size: 500 incidents per request                                     │ │
│  │    • Error Handling: Retry with exponential backoff                            │ │
│  │    • Logging: Detailed sync logs with timestamps                               │ │
│  │                                                                                 │ │
│  │  Status: Framework complete, requires .env configuration                       │ │
│  └────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                       │
│  ┌────────────────────────────────────────────────────────────────────────────────┐ │
│  │                      Future Integrations (Planned)                              │ │
│  │                                                                                 │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │ │
│  │  │   Jira       │  │  Azure       │  │    Slack     │  │  Microsoft       │  │ │
│  │  │   (Q2 2026)  │  │  DevOps      │  │  (Q3 2026)   │  │  Teams           │  │ │
│  │  │              │  │  (Q2 2026)   │  │              │  │  (Q3 2026)       │  │ │
│  │  │  • Ticket    │  │  • Work      │  │  • Notify on │  │  • Notify on     │  │ │
│  │  │    import    │  │    items     │  │    SOP gen   │  │    SOP creation  │  │ │
│  │  │  • Status    │  │  • Boards    │  │  • AI alerts │  │  • Bot commands  │  │ │
│  │  │    sync      │  │  • Repos     │  │  • Search KB │  │  • Collaboration │  │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────────┘  │ │
│  └────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                       │
└───────────────────────────────────────────────────────────────────────────────────────┘


                                ┌──────────────────┐
                                │  ServiceNow      │
                                │  Instance        │
                                │                  │
                                │  • Incident DB   │
                                │  • CMDB          │
                                │  • Config Items  │
                                └────────┬─────────┘
                                         │
                                         │ REST API
                                         │ HTTPS
                                         │
                                    Data Source
```

---

## 2. Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            INCIDENT LIFECYCLE FLOW                                   │
└─────────────────────────────────────────────────────────────────────────────────────┘

[1] INCIDENT CREATION
    ┌──────────────────┐
    │  ServiceNow      │
    │  New Incident    │
    │  Status: New     │
    └────────┬─────────┘
             │
             ▼
    ┌─────────────────────────────────────┐
    │  Manual Entry or API Import         │
    │  • User enters details in UI        │
    │  • Or auto-import from ServiceNow   │
    └────────┬────────────────────────────┘
             │
             ▼

[2] AI RESOLUTION PREDICTION
    ┌─────────────────────────────────────┐
    │  User Clicks "AI Suggest"           │
    └────────┬────────────────────────────┘
             │
             ▼
    ┌─────────────────────────────────────┐
    │  Sentence-BERT Encoding             │
    │  Input: "Email not working"         │
    │  Output: [0.23, -0.45, ..., 0.89]  │
    │  Time: 200ms                        │
    └────────┬────────────────────────────┘
             │
             ▼
    ┌─────────────────────────────────────┐
    │  Semantic Search (RAG)              │
    │  • Load KB (464 incidents)          │
    │  • Calculate cosine similarity      │
    │  • Rank by score                    │
    │  • Apply 60% threshold              │
    │  Time: 300ms                        │
    └────────┬────────────────────────────┘
             │
             ▼
    ┌─────────────────────────────────────┐
    │  Return Best Match                  │
    │  • Resolution: "Reset password..."  │
    │  • Confidence: 87%                  │
    │  • Similar incident: INC0002        │
    └────────┬────────────────────────────┘
             │
             ▼
    ┌─────────────────────────────────────┐
    │  Auto-fill Resolution Field         │
    │  • JavaScript populates textarea    │
    │  • Show confidence badge            │
    │  • User can edit/refine             │
    └────────┬────────────────────────────┘
             │
             ▼

[3] SOP GENERATION
    ┌─────────────────────────────────────┐
    │  User Clicks "Generate SOP"         │
    └────────┬────────────────────────────┘
             │
             ▼
    ┌─────────────────────────────────────┐
    │  SOP Generator Module               │
    │  • Extract problem statement        │
    │  • Format symptoms                  │
    │  • Structure resolution steps       │
    │  • Add prevention measures          │
    │  • Include related incidents        │
    │  Time: 100ms                        │
    └────────┬────────────────────────────┘
             │
             ▼
    ┌─────────────────────────────────────┐
    │  Markdown → HTML Rendering          │
    │  • Professional formatting          │
    │  • Category-specific colors         │
    │  • Priority badges                  │
    └────────┬────────────────────────────┘
             │
             ▼
    ┌─────────────────────────────────────┐
    │  Display SOP + Download Option      │
    │  • Show formatted SOP in browser    │
    │  • "Download PDF" button enabled    │
    │  • Copy to clipboard available      │
    └────────┬────────────────────────────┘
             │
             ▼

[4] KNOWLEDGE BASE UPDATE
    ┌─────────────────────────────────────┐
    │  Automatic KB Addition              │
    │  IF resolution_notes exists:        │
    │    • Generate embedding             │
    │    • Check duplicate (>95%)         │
    │    • Add to knowledge_base.json     │
    │    • Update cache                   │
    │    • Increment version              │
    └────────┬────────────────────────────┘
             │
             ▼
    ┌─────────────────────────────────────┐
    │  KB Updated & System Improved       │
    │  • Incident count: +1               │
    │  • Prediction accuracy: ↑           │
    │  • Self-learning complete           │
    └─────────────────────────────────────┘


[PARALLEL FLOW: Batch Analysis]
    ┌─────────────────────────────────────┐
    │  User Submits 50 Incidents          │
    │  • Via Batch Analysis tab           │
    │  • Or ServiceNow bulk import        │
    └────────┬────────────────────────────┘
             │
             ▼
    ┌─────────────────────────────────────┐
    │  Text Encoding (Sentence-BERT)      │
    │  • Encode all 50 descriptions       │
    │  • Time: 50 × 200ms = 10s           │
    └────────┬────────────────────────────┘
             │
             ▼
    ┌─────────────────────────────────────┐
    │  HDBSCAN Clustering                 │
    │  • Density-based grouping           │
    │  • Auto detect cluster count        │
    │  • Identify outliers                │
    │  • Time: 1s                         │
    └────────┬────────────────────────────┘
             │
             ▼
    ┌─────────────────────────────────────┐
    │  Pattern Extraction                 │
    │  • Cluster 0: Email issues (20)     │
    │  • Cluster 1: Network (15)          │
    │  • Cluster 2: Hardware (10)         │
    │  • Noise: 5 outliers                │
    └────────┬────────────────────────────┘
             │
             ▼
    ┌─────────────────────────────────────┐
    │  Bulk KB Update                     │
    │  • Add resolved incidents (with res)│
    │  • Skip duplicates                  │
    │  • Update embeddings cache          │
    └─────────────────────────────────────┘
```

---

## 3. ServiceNow Integration Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                     SERVICENOW SYNC ARCHITECTURE                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────┐
│  ServiceNow Platform                 │
│  https://company.service-now.com     │
│                                      │
│  ┌────────────────────────────────┐  │
│  │  Incident Table                │  │
│  │  • 50,000+ total incidents     │  │
│  │  • 15,000 resolved (state=6)   │  │
│  │  • Contains resolution_notes   │  │
│  │  • Updated continuously        │  │
│  └────────────────────────────────┘  │
└────────────────┬─────────────────────┘
                 │
                 │ REST API Call
                 │ GET /api/now/table/incident
                 │ Query: state=6^resolved_at>=2025-12-28T00:00:00
                 │ Headers: Authorization: Basic {token}
                 │
                 ▼
┌──────────────────────────────────────┐
│  ServiceNow Client                   │
│  (src/servicenow/client.py)          │
│                                      │
│  Methods:                            │
│  • fetch_incidents()                 │
│  • sync_resolved_incidents()         │
│  • transform_data()                  │
│  • handle_errors()                   │
└────────────────┬─────────────────────┘
                 │
                 │ Returns JSON array
                 │ [
                 │   {
                 │     "number": "INC0012345",
                 │     "description": "...",
                 │     "close_notes": "...",
                 │     ...
                 │   },
                 │   // ... 499 more
                 │ ]
                 │
                 ▼
┌──────────────────────────────────────┐
│  Data Validation & Cleaning          │
│                                      │
│  For each incident:                  │
│  1. Check required fields            │
│  2. Remove HTML tags                 │
│  3. Normalize category               │
│  4. Validate priority (1-4)          │
│  5. Parse timestamps                 │
│                                      │
│  Pass: 485 incidents                 │
│  Fail: 15 incidents (missing data)   │
└────────────────┬─────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────┐
│  Incident Analyzer                   │
│                                      │
│  For each validated incident:        │
│  1. Encode description (SBERT)       │
│  2. Generate 384-dim embedding       │
│  3. Check duplicate (>95%)           │
│  4. Category prediction (optional)   │
│                                      │
│  Processing time: 485 × 200ms = 97s  │
└────────────────┬─────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────┐
│  Knowledge Base Manager              │
│                                      │
│  1. Load existing KB (464 incidents) │
│  2. Add new unique incidents         │
│  3. Skip 47 duplicates (>95% match)  │
│  4. Update embeddings cache          │
│  5. Increment version: 1.5 → 2.0     │
│  6. Save to knowledge_base.json      │
│                                      │
│  Result:                             │
│  • Added: 438 new incidents          │
│  • Duplicates: 47 skipped            │
│  • Total KB: 464 → 902 incidents     │
│  • File size: 15.8 MB → 30.7 MB      │
└────────────────┬─────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────┐
│  Logging & Notification              │
│                                      │
│  Log entries:                        │
│  [INFO] ServiceNow sync started      │
│  [INFO] Fetched 500 incidents        │
│  [INFO] Validated 485 incidents      │
│  [INFO] Generated 485 embeddings     │
│  [INFO] Added 438 to KB              │
│  [INFO] Skipped 47 duplicates        │
│  [SUCCESS] Sync completed            │
│                                      │
│  Update last_sync_time:              │
│  2025-12-28T10:30:00Z                │
└──────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           SYNC SCHEDULE                                              │
│                                                                                      │
│  Cron Expression: 0 */6 * * *  (Every 6 hours)                                      │
│                                                                                      │
│  Schedule:                                                                           │
│  • 00:00 (midnight) → Fetch last 6 hours of resolved incidents                      │
│  • 06:00 (6 AM)     → Fetch last 6 hours of resolved incidents                      │
│  • 12:00 (noon)     → Fetch last 6 hours of resolved incidents                      │
│  • 18:00 (6 PM)     → Fetch last 6 hours of resolved incidents                      │
│                                                                                      │
│  Error Handling:                                                                     │
│  • Retry: 3 attempts with exponential backoff (1s, 2s, 4s)                          │
│  • Timeout: 30 seconds per request                                                  │
│  • Alerting: Email admin on consecutive failures                                    │
│  • Fallback: Continue with last successful KB state                                 │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. AI/ML Processing Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    MACHINE LEARNING PIPELINE                                         │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────┐
│  Input: Incident Description         │
│  "User unable to access email"       │
└────────────────┬─────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                     SENTENCE-BERT ENCODER                                             │
│                                                                                       │
│  ┌────────────────────────────────────────────────────────────────────────────────┐ │
│  │  Stage 1: Tokenization                                                         │ │
│  │  Input:  "User unable to access email"                                        │ │
│  │  Output: [101, 2629, 4039, 2000, 3229, 6047, 102, 0, 0, ...]                 │ │
│  │          (Token IDs padded to 256)                                            │ │
│  └────────────────────────────────────────────────────────────────────────────────┘ │
│                 │                                                                     │
│                 ▼                                                                     │
│  ┌────────────────────────────────────────────────────────────────────────────────┐ │
│  │  Stage 2: Embedding Lookup                                                     │ │
│  │  Each token → 384-dim vector                                                   │ │
│  │  Token 2629 ("user")  → [0.12, -0.34, 0.56, ..., 0.78]                       │ │
│  │  Token 4039 ("unable") → [0.23, -0.45, 0.67, ..., 0.89]                      │ │
│  │  ...                                                                           │ │
│  └────────────────────────────────────────────────────────────────────────────────┘ │
│                 │                                                                     │
│                 ▼                                                                     │
│  ┌────────────────────────────────────────────────────────────────────────────────┐ │
│  │  Stage 3: Transformer Layers (6 layers)                                        │ │
│  │                                                                                 │ │
│  │  Layer 1:                                                                       │ │
│  │    Multi-Head Attention (12 heads) → Self-attention across tokens             │ │
│  │    Feed-Forward Network → 2 linear layers with GELU activation                │ │
│  │    Layer Normalization → Stabilize training                                   │ │
│  │    Residual Connection → Skip connection from input                           │ │
│  │                                                                                 │ │
│  │  Layer 2-6: [Same structure repeated]                                          │ │
│  │                                                                                 │ │
│  │  Output: Contextualized embeddings for each token                              │ │
│  └────────────────────────────────────────────────────────────────────────────────┘ │
│                 │                                                                     │
│                 ▼                                                                     │
│  ┌────────────────────────────────────────────────────────────────────────────────┐ │
│  │  Stage 4: Mean Pooling                                                         │ │
│  │  Average all token embeddings → Single 384-dim sentence embedding             │ │
│  │  Output: [0.23, -0.45, 0.67, 0.12, ..., 0.89]                                │ │
│  └────────────────────────────────────────────────────────────────────────────────┘ │
│                 │                                                                     │
│                 ▼                                                                     │
│  ┌────────────────────────────────────────────────────────────────────────────────┐ │
│  │  Stage 5: Normalization                                                        │ │
│  │  L2 normalization → Unit vector (magnitude = 1.0)                              │ │
│  │  Enables cosine similarity = dot product                                       │ │
│  └────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                       │
│  Processing Time: ~200ms                                                              │
│  Memory: ~90 MB (model loaded once, reused)                                           │
└───────────────────────────────────────┬───────────────────────────────────────────────┘
                                        │
                                        ▼
                          [0.23, -0.45, 0.67, ..., 0.89]
                          384-dimensional embedding
                                        │
                 ┌──────────────────────┴───────────────────────┐
                 │                                              │
                 ▼                                              ▼
    ┌────────────────────────┐                    ┌─────────────────────────┐
    │  RAG RESOLUTION FINDER │                    │  HDBSCAN CLUSTERING     │
    │                        │                    │                         │
    │  1. Load KB embeddings │                    │  1. Collect embeddings  │
    │     (464 incidents)    │                    │     (50 incidents)      │
    │                        │                    │                         │
    │  2. Cosine Similarity  │                    │  2. Build density graph │
    │     for each incident: │                    │     (mutual reachability│
    │                        │                    │      distance)          │
    │     sim = dot(A, B)    │                    │                         │
    │     (normalized)       │                    │  3. Extract clusters    │
    │                        │                    │     based on density    │
    │  3. Rank by score      │                    │                         │
    │     [0.92, 0.87, 0.74, │                    │  4. Assign labels       │
    │      0.62, 0.45, ...]  │                    │     [0, 0, 1, 1, 2,    │
    │                        │                    │      -1, 0, ...]       │
    │  4. Apply threshold    │                    │                         │
    │     (>0.60)            │                    │  5. Calculate stats     │
    │                        │                    │     • Cluster count: 3  │
    │  5. Return best match  │                    │     • Noise: 1 incident │
    │     if confidence>60%  │                    │     • Largest: 20       │
    │                        │                    │                         │
    │  Output:               │                    │  Output:                │
    │  • Resolution text     │                    │  • Cluster labels       │
    │  • Confidence: 92%     │                    │  • Pattern keywords     │
    │  • Similar: INC0003    │                    │  • Statistics           │
    └────────────────────────┘                    └─────────────────────────┘
```

---

## 5. Security Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           SECURITY LAYERS                                            │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────┐
│  Layer 1: Network Security           │
│                                      │
│  • HTTPS/TLS encryption              │
│  • Certificate validation            │
│  • Firewall rules                    │
│  • Rate limiting                     │
│  • DDoS protection                   │
└────────────────┬─────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────┐
│  Layer 2: Authentication             │
│                                      │
│  ServiceNow:                         │
│  • OAuth 2.0 (recommended)           │
│  • Basic Auth (dev only)             │
│  • API token rotation                │
│                                      │
│  Web Application:                    │
│  • Session management                │
│  • CSRF protection                   │
│  • Secure cookies                    │
└────────────────┬─────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────┐
│  Layer 3: Authorization              │
│                                      │
│  • Role-based access (future)        │
│  • Read-only vs admin                │
│  • API endpoint permissions          │
└────────────────┬─────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────┐
│  Layer 4: Data Protection            │
│                                      │
│  • Input validation                  │
│  • SQL injection prevention (N/A)    │
│  • XSS protection                    │
│  • Sensitive data masking            │
│  • Encryption at rest (future)       │
└────────────────┬─────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────┐
│  Layer 5: Logging & Monitoring       │
│                                      │
│  • Access logs                       │
│  • Error tracking                    │
│  • Audit trail                       │
│  • Anomaly detection                 │
└──────────────────────────────────────┘
```

---

## 6. Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                      DEPLOYMENT OPTIONS                                              │
└─────────────────────────────────────────────────────────────────────────────────────┘

OPTION 1: LOCAL DEVELOPMENT
┌──────────────────────────┐
│  Developer Machine       │
│  • Python 3.8+           │
│  • Flask dev server      │
│  • Port 5000             │
│  • Hot reload enabled    │
│  • Debug mode ON         │
└──────────────────────────┘

OPTION 2: PRODUCTION SERVER
┌────────────────────────────────────────────┐
│  Linux Server (Ubuntu/CentOS)              │
│  ┌──────────────────────────────────────┐  │
│  │  Nginx (Reverse Proxy)               │  │
│  │  • Port 80/443                       │  │
│  │  • SSL termination                   │  │
│  │  • Static file serving               │  │
│  │  • Load balancing                    │  │
│  └────────────┬─────────────────────────┘  │
│               │                             │
│  ┌────────────▼─────────────────────────┐  │
│  │  Gunicorn (WSGI Server)              │  │
│  │  • 4 worker processes                │  │
│  │  • Port 8000 (internal)              │  │
│  │  • Process management                │  │
│  └────────────┬─────────────────────────┘  │
│               │                             │
│  ┌────────────▼─────────────────────────┐  │
│  │  Flask Application                   │  │
│  │  • AI/ML models loaded               │  │
│  │  • Knowledge base in memory          │  │
│  └──────────────────────────────────────┘  │
└────────────────────────────────────────────┘

OPTION 3: DOCKER CONTAINER
┌────────────────────────────────────────────┐
│  Docker Host                               │
│  ┌──────────────────────────────────────┐  │
│  │  Container: sop-generator            │  │
│  │  ┌────────────────────────────────┐  │  │
│  │  │  Base: python:3.8-slim         │  │  │
│  │  │  App: /app                     │  │  │
│  │  │  Port: 5000 → 5000            │  │  │
│  │  │  Volume: ./data:/app/data      │  │  │
│  │  │  CMD: gunicorn web_app:app     │  │  │
│  │  └────────────────────────────────┘  │  │
│  └──────────────────────────────────────┘  │
└────────────────────────────────────────────┘

OPTION 4: CLOUD (AZURE)
┌─────────────────────────────────────────────────────────────┐
│  Azure Cloud                                                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Azure App Service                                    │  │
│  │  • Runtime: Python 3.8                                │  │
│  │  • Tier: Standard S1                                  │  │
│  │  • Auto-scale: 2-10 instances                         │  │
│  │  • Region: East US                                    │  │
│  └─────────────────┬─────────────────────────────────────┘  │
│                    │                                         │
│  ┌─────────────────▼─────────────────────────────────────┐  │
│  │  Azure Blob Storage (Optional)                        │  │
│  │  • knowledge_base.json backup                         │  │
│  │  • Model files caching                                │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Azure Monitor                                        │  │
│  │  • Application Insights                               │  │
│  │  • Performance metrics                                │  │
│  │  • Error tracking                                     │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. Complete Request-Response Flow

```
USER ACTION: Generate SOP with AI Resolution Suggestion

[1] User enters incident description in browser
    ↓
[2] JavaScript: Click "🤖 AI Suggest Resolution"
    ↓
[3] Frontend: POST /suggest_resolution
    Body: {"description": "Email not working", "category": "Email"}
    ↓
[4] Flask Route Handler: /suggest_resolution
    ↓
[5] Load Resolution Finder (lazy load if first request)
    Time: 2s (first time) or 0s (cached)
    ↓
[6] Encode description (Sentence-BERT)
    Input: "Email not working"
    Output: [0.23, -0.45, 0.67, ..., 0.89] (384-dim)
    Time: 200ms
    ↓
[7] Load Knowledge Base (464 incidents with embeddings)
    Source: knowledge_base.json (from cache)
    Time: 50ms
    ↓
[8] Calculate Cosine Similarity for all KB incidents
    Formula: cos(θ) = dot(query, kb_incident) / (norm(query) × norm(kb_incident))
    Comparisons: 464
    Time: 300ms
    ↓
[9] Rank by similarity score
    Results: [0.92, 0.87, 0.74, 0.62, 0.45, 0.23, ...]
    Best match: INC0003 (92% similarity)
    ↓
[10] Apply confidence threshold (>0.60)
     92% > 60% → PASS ✓
     ↓
[11] Return response
     JSON: {
       "success": true,
       "resolution": "Reset password using AD self-service portal...",
       "confidence": 0.92,
       "similar_incident": "INC0003",
       "match_count": 5
     }
     Time: 10ms
     ↓
[12] Frontend receives response
     Total API time: 560ms
     ↓
[13] JavaScript auto-fills resolution field
     document.getElementById('resolution').value = response.resolution
     ↓
[14] Show toast notification
     "✅ AI Suggestion: 92% match found!"
     ↓
[15] User reviews/edits resolution (optional)
     ↓
[16] User clicks "Generate SOP"
     ↓
[17] POST /generate_sop
     Body: {all incident data including resolution}
     ↓
[18] SOP Generator Module
     • Extract components
     • Apply template
     • Format markdown
     Time: 100ms
     ↓
[19] Auto-update Knowledge Base
     IF resolution_notes exists:
       • Generate embedding
       • Check duplicate (>95%)
       • Add to knowledge_base.json
       • Update cache
     Time: 250ms
     ↓
[20] Return SOP (HTML formatted)
     ↓
[21] Display SOP in browser
     • Professional formatting
     • Download PDF button enabled
     • Copy to clipboard available
     ↓
[22] User downloads PDF (optional)
     • html2pdf.js (client-side)
     • A4 format, 98% quality
     • Filename: SOP_INC0020_20251228.pdf

TOTAL TIME: <2 seconds (including AI processing)
```

---

## Legend

```
┌────┐
│    │  = Component/Module
└────┘

  │     = Data flow
  ▼     = Direction

[TEXT] = Process step

HTTPS  = Secure protocol
REST   = RESTful API
JSON   = Data format
```
