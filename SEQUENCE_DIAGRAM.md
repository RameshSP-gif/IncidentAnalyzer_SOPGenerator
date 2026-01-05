# Incident Analyzer & SOP Generator - Sequence Diagrams

## 1. AI-Powered Resolution Prediction Sequence

```
Actor: User
Frontend: Browser (JavaScript)
Backend: Flask Server
RAG: Resolution Finder
SBERT: Sentence-BERT Model
KB: Knowledge Base (JSON)

┌──────┐          ┌──────────┐         ┌─────────┐        ┌─────┐      ┌──────┐      ┌────┐
│ User │          │ Frontend │         │ Backend │        │ RAG │      │SBERT │      │ KB │
└──┬───┘          └────┬─────┘         └────┬────┘        └──┬──┘      └──┬───┘      └─┬──┘
   │                   │                    │                │            │            │
   │ 1. Enter incident │                    │                │            │            │
   │   description     │                    │                │            │            │
   ├──────────────────>│                    │                │            │            │
   │                   │                    │                │            │            │
   │ 2. Click "AI      │                    │                │            │            │
   │    Suggest        │                    │                │            │            │
   │    Resolution"    │                    │                │            │            │
   ├──────────────────>│                    │                │            │            │
   │                   │                    │                │            │            │
   │                   │ 3. POST /suggest_resolution         │            │            │
   │                   │    Body: {description, category}    │            │            │
   │                   ├───────────────────>│                │            │            │
   │                   │                    │                │            │            │
   │                   │                    │ 4. Validate    │            │            │
   │                   │                    │    request     │            │            │
   │                   │                    ├───────────┐    │            │            │
   │                   │                    │           │    │            │            │
   │                   │                    │<──────────┘    │            │            │
   │                   │                    │                │            │            │
   │                   │                    │ 5. Get/Load Resolution Finder            │
   │                   │                    │    (lazy load if first time)             │
   │                   │                    ├───────────────>│            │            │
   │                   │                    │                │            │            │
   │                   │                    │                │ 6. Load model if needed │
   │                   │                    │                ├───────────>│            │
   │                   │                    │                │            │            │
   │                   │                    │                │ 7. Model ready          │
   │                   │                    │                │<───────────┤            │
   │                   │                    │                │            │            │
   │                   │                    │ 8. suggest_resolution()     │            │
   │                   │                    │    ("Email not working")    │            │
   │                   │                    ├───────────────>│            │            │
   │                   │                    │                │            │            │
   │                   │                    │                │ 9. Encode text          │
   │                   │                    │                ├───────────>│            │
   │                   │                    │                │            │            │
   │                   │                    │                │ 10. Return embedding    │
   │                   │                    │                │    [0.23,-0.45,...,0.89]│
   │                   │                    │                │<───────────┤            │
   │                   │                    │                │   (384-dim, ~200ms)     │
   │                   │                    │                │            │            │
   │                   │                    │                │ 11. Load KB embeddings  │
   │                   │                    │                ├───────────────────────>│
   │                   │                    │                │            │            │
   │                   │                    │                │ 12. Return 464 incidents│
   │                   │                    │                │     with embeddings     │
   │                   │                    │                │<───────────────────────┤
   │                   │                    │                │   (~50ms from cache)    │
   │                   │                    │                │            │            │
   │                   │                    │                │ 13. Calculate cosine    │
   │                   │                    │                │     similarity for each │
   │                   │                    │                │     incident (464 comp) │
   │                   │                    │                ├─────────────┐           │
   │                   │                    │                │             │           │
   │                   │                    │                │ cos(θ) = A·B/(||A||·||B||)│
   │                   │                    │                │             │           │
   │                   │                    │                │<────────────┘           │
   │                   │                    │                │   (~300ms)              │
   │                   │                    │                │            │            │
   │                   │                    │                │ 14. Rank by score       │
   │                   │                    │                │     [0.92, 0.87, 0.74, │
   │                   │                    │                │      0.62, 0.45, ...]  │
   │                   │                    │                ├─────────────┐           │
   │                   │                    │                │             │           │
   │                   │                    │                │<────────────┘           │
   │                   │                    │                │            │            │
   │                   │                    │                │ 15. Apply threshold     │
   │                   │                    │                │     (>0.60)             │
   │                   │                    │                ├─────────────┐           │
   │                   │                    │                │ Best: 0.92  │           │
   │                   │                    │                │ Pass: ✓     │           │
   │                   │                    │                │<────────────┘           │
   │                   │                    │                │            │            │
   │                   │                    │ 16. Return result           │            │
   │                   │                    │     {resolution, confidence}│            │
   │                   │                    │<───────────────┤            │            │
   │                   │                    │                │            │            │
   │                   │ 17. JSON Response  │                │            │            │
   │                   │     200 OK         │                │            │            │
   │                   │     {success: true,│                │            │            │
   │                   │      resolution: "Reset password...",            │            │
   │                   │      confidence: 0.92,              │            │            │
   │                   │      similar_incident: "INC0003"}   │            │            │
   │                   │<───────────────────┤                │            │            │
   │                   │  (~560ms total)    │                │            │            │
   │                   │                    │                │            │            │
   │ 18. Auto-fill     │                    │                │            │            │
   │     resolution    │                    │                │            │            │
   │     field         │                    │                │            │            │
   │<──────────────────┤                    │                │            │            │
   │                   │                    │                │            │            │
   │ 19. Show toast:   │                    │                │            │            │
   │     "AI Suggestion│                    │                │            │            │
   │      92% match!"  │                    │                │            │            │
   │<──────────────────┤                    │                │            │            │
   │                   │                    │                │            │            │
   │ 20. Review/Edit   │                    │                │            │            │
   │     resolution    │                    │                │            │            │
   ├───────────────┐   │                    │                │            │            │
   │               │   │                    │                │            │            │
   │<──────────────┘   │                    │                │            │            │
   │                   │                    │                │            │            │
```

**Timeline:**
- Step 1-3: User interaction (~1s)
- Step 4-5: Validation & loading (~50ms or 2s first time)
- Step 6-10: Text encoding (~200ms)
- Step 11-12: Load KB (~50ms)
- Step 13-15: Similarity calculation (~300ms)
- Step 16-19: Response & UI update (~10ms)
- **Total: ~560ms** (or ~2.5s if first request)

---

## 2. SOP Generation & Knowledge Base Update Sequence

```
Actor: User
Frontend: Browser
Backend: Flask Server
SOP: SOP Generator
RAG: Resolution Finder
KB: Knowledge Base

┌──────┐      ┌──────────┐      ┌─────────┐      ┌─────┐      ┌─────┐      ┌────┐
│ User │      │ Frontend │      │ Backend │      │ SOP │      │ RAG │      │ KB │
└──┬───┘      └────┬─────┘      └────┬────┘      └──┬──┘      └──┬──┘      └─┬──┘
   │               │                 │               │            │            │
   │ 1. Fill form  │                 │               │            │            │
   │    (incident, │                 │               │            │            │
   │     resolution│                 │               │            │            │
   │     filled)   │                 │               │            │            │
   ├──────────────>│                 │               │            │            │
   │               │                 │               │            │            │
   │ 2. Click      │                 │               │            │            │
   │    "Generate  │                 │               │            │            │
   │     SOP"      │                 │               │            │            │
   ├──────────────>│                 │               │            │            │
   │               │                 │               │            │            │
   │               │ 3. Validate form│               │            │            │
   │               ├─────────┐       │               │            │            │
   │               │         │       │               │            │            │
   │               │<────────┘       │               │            │            │
   │               │                 │               │            │            │
   │               │ 4. POST /generate_sop           │            │            │
   │               │    Body: {number, description,  │            │            │
   │               │           category, priority,   │            │            │
   │               │           resolution_notes}     │            │            │
   │               ├────────────────>│               │            │            │
   │               │                 │               │            │            │
   │               │                 │ 5. Validate   │            │            │
   │               │                 │    required   │            │            │
   │               │                 │    fields     │            │            │
   │               │                 ├───────┐       │            │            │
   │               │                 │       │       │            │            │
   │               │                 │<──────┘       │            │            │
   │               │                 │               │            │            │
   │               │                 │ 6. generate_sop()          │            │
   │               │                 ├──────────────>│            │            │
   │               │                 │               │            │            │
   │               │                 │               │ 7. Extract components   │
   │               │                 │               │    • Problem statement  │
   │               │                 │               │    • Symptoms           │
   │               │                 │               │    • Resolution steps   │
   │               │                 │               ├──────────┐ │            │
   │               │                 │               │          │ │            │
   │               │                 │               │<─────────┘ │            │
   │               │                 │               │            │            │
   │               │                 │               │ 8. Apply template       │
   │               │                 │               │    (category-specific)  │
   │               │                 │               ├──────────┐ │            │
   │               │                 │               │          │ │            │
   │               │                 │               │<─────────┘ │            │
   │               │                 │               │            │            │
   │               │                 │               │ 9. Format markdown      │
   │               │                 │               │    # SOP               │
   │               │                 │               │    ## Problem          │
   │               │                 │               │    ### Steps...        │
   │               │                 │               ├──────────┐ │            │
   │               │                 │               │          │ │            │
   │               │                 │               │<─────────┘ │            │
   │               │                 │               │   (~100ms) │            │
   │               │                 │               │            │            │
   │               │                 │ 10. Return SOP│            │            │
   │               │                 │     (markdown)│            │            │
   │               │                 │<──────────────┤            │            │
   │               │                 │               │            │            │
   │               │                 │ 11. Check if resolution exists         │
   │               │                 ├───────────────────────────>│            │
   │               │                 │               │            │            │
   │               │                 │ 12. add_to_knowledge_base()│            │
   │               │                 │     (if resolution provided)│            │
   │               │                 ├───────────────────────────>│            │
   │               │                 │               │            │            │
   │               │                 │               │            │ 13. Load current KB
   │               │                 │               │            ├───────────>│
   │               │                 │               │            │            │
   │               │                 │               │            │ 14. Return KB data
   │               │                 │               │            │<───────────┤
   │               │                 │               │            │            │
   │               │                 │               │            │ 15. Generate embedding
   │               │                 │               │            │     (SBERT)│
   │               │                 │               │            ├──────┐     │
   │               │                 │               │            │      │     │
   │               │                 │               │            │<─────┘     │
   │               │                 │               │            │ (~200ms)   │
   │               │                 │               │            │            │
   │               │                 │               │            │ 16. Check duplicate
   │               │                 │               │            │     (>95% similar)
   │               │                 │               │            ├──────┐     │
   │               │                 │               │            │      │     │
   │               │                 │               │            │<─────┘     │
   │               │                 │               │            │ (unique ✓) │
   │               │                 │               │            │            │
   │               │                 │               │            │ 17. Append to KB
   │               │                 │               │            │     incidents[]
   │               │                 │               │            ├───────────>│
   │               │                 │               │            │            │
   │               │                 │               │            │ 18. Save to file
   │               │                 │               │            │     knowledge_base.json
   │               │                 │               │            │<───────────┤
   │               │                 │               │            │            │
   │               │                 │               │            │ 19. Update cache
   │               │                 │               │            ├───────────>│
   │               │                 │               │            │            │
   │               │                 │               │            │ 20. Increment version
   │               │                 │               │            │     1.5 → 1.6
   │               │                 │               │            │<───────────┤
   │               │                 │               │            │   (~50ms)  │
   │               │                 │               │            │            │
   │               │                 │ 21. KB update │            │            │
   │               │                 │     successful│            │            │
   │               │                 │<───────────────────────────┤            │
   │               │                 │               │            │            │
   │               │                 │ 22. Log update│            │            │
   │               │                 │     [INFO] Added INC0020 to KB         │
   │               │                 ├───────┐       │            │            │
   │               │                 │       │       │            │            │
   │               │                 │<──────┘       │            │            │
   │               │                 │               │            │            │
   │               │ 23. JSON Response               │            │            │
   │               │     200 OK      │               │            │            │
   │               │     {success: true,             │            │            │
   │               │      sop: "# SOP...",           │            │            │
   │               │      kb_updated: true}          │            │            │
   │               │<────────────────┤               │            │            │
   │               │  (~350ms total) │               │            │            │
   │               │                 │               │            │            │
   │ 24. Render SOP│                 │               │            │            │
   │     in browser│                 │               │            │            │
   │<──────────────┤                 │               │            │            │
   │               │                 │               │            │            │
   │ 25. Show      │                 │               │            │            │
   │     "Download │                 │               │            │            │
   │      PDF"     │                 │               │            │            │
   │     button    │                 │               │            │            │
   │<──────────────┤                 │               │            │            │
   │               │                 │               │            │            │
```

**Timeline:**
- Step 1-4: User interaction & form submission (~1s)
- Step 5-10: SOP generation (~100ms)
- Step 11-21: Knowledge base update (~250ms)
- Step 22-25: Response & rendering (~50ms)
- **Total: ~350ms** (excluding user interaction)

---

## 3. ServiceNow Scheduled Sync Sequence

```
Cron: Scheduler
ServiceNow: External API
Client: ServiceNow Client
Backend: Flask Server
Validator: Data Validator
Analyzer: Incident Analyzer
SBERT: Sentence-BERT
KB: Knowledge Base

┌──────┐  ┌────────────┐  ┌────────┐  ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌──────┐  ┌────┐
│ Cron │  │ ServiceNow │  │ Client │  │ Backend │  │Validator │  │ Analyzer│  │SBERT │  │ KB │
└──┬───┘  └─────┬──────┘  └───┬────┘  └────┬────┘  └────┬─────┘  └────┬────┘  └──┬───┘  └─┬──┘
   │            │              │            │             │             │           │        │
   │ 1. Trigger │              │            │             │             │           │        │
   │    every 6 │              │            │             │             │           │        │
   │    hours   │              │            │             │             │           │        │
   ├───────────────────────────────────────>│             │             │           │        │
   │            │              │            │             │             │           │        │
   │            │              │            │ 2. sync_servicenow()      │           │        │
   │            │              │            │    scheduled task         │           │        │
   │            │              │            ├────────┐    │             │           │        │
   │            │              │            │        │    │             │           │        │
   │            │              │            │<───────┘    │             │           │        │
   │            │              │            │             │             │           │        │
   │            │              │ 3. get_last_sync_time() │             │           │        │
   │            │              │            │             │             │           │        │
   │            │              │            │ Returns: "2025-12-29T00:00:00Z"       │        │
   │            │              │            │             │             │           │        │
   │            │              │ 4. fetch_incidents()    │             │           │        │
   │            │              │    query="state=6^resolved_at>=..."   │           │        │
   │            │              │<───────────┤             │             │           │        │
   │            │              │            │             │             │           │        │
   │            │ 5. GET /api/now/table/incident         │             │           │        │
   │            │    ?sysparm_query=state=6^resolved_at>=2025-12-29   │           │        │
   │            │    &sysparm_fields=number,description,close_notes... │           │        │
   │            │    &sysparm_limit=500                   │             │           │        │
   │            │<─────────────┤            │             │             │           │        │
   │            │              │            │             │             │           │        │
   │            │ 6. Authenticate          │             │             │           │        │
   │            │    (OAuth 2.0)           │             │             │           │        │
   │            ├───────┐      │            │             │             │           │        │
   │            │       │      │            │             │             │           │        │
   │            │<──────┘      │            │             │             │           │        │
   │            │              │            │             │             │           │        │
   │            │ 7. Execute query         │             │             │           │        │
   │            │    on incident table     │             │             │           │        │
   │            ├───────┐      │            │             │             │           │        │
   │            │       │      │            │             │             │           │        │
   │            │<──────┘      │            │             │             │           │        │
   │            │  (~2s)       │            │             │             │           │        │
   │            │              │            │             │             │           │        │
   │            │ 8. JSON Response (500 incidents)       │             │           │        │
   │            │    [{number: "INC0012345", ...}, ...]  │             │           │        │
   │            ├─────────────>│            │             │             │           │        │
   │            │              │            │             │             │           │        │
   │            │              │ 9. Return incidents     │             │           │        │
   │            │              ├───────────>│             │             │           │        │
   │            │              │            │             │             │           │        │
   │            │              │            │ 10. For each incident (500)          │        │
   │            │              │            │     transform & validate  │           │        │
   │            │              │            ├──────────────────────────>│           │        │
   │            │              │            │             │             │           │        │
   │            │              │            │             │ 11. Check required fields      │
   │            │              │            │             │     (number, description, etc) │
   │            │              │            │             ├─────┐       │           │        │
   │            │              │            │             │     │       │           │        │
   │            │              │            │             │<────┘       │           │        │
   │            │              │            │             │             │           │        │
   │            │              │            │             │ 12. Clean HTML tags     │        │
   │            │              │            │             ├─────┐       │           │        │
   │            │              │            │             │     │       │           │        │
   │            │              │            │             │<────┘       │           │        │
   │            │              │            │             │             │           │        │
   │            │              │            │             │ 13. Normalize category  │        │
   │            │              │            │             │     "Email/Messaging"→"Email"   │
   │            │              │            │             ├─────┐       │           │        │
   │            │              │            │             │     │       │           │        │
   │            │              │            │             │<────┘       │           │        │
   │            │              │            │             │             │           │        │
   │            │              │            │ 14. Valid: 485            │           │        │
   │            │              │            │     Invalid: 15           │           │        │
   │            │              │            │<──────────────────────────┤           │        │
   │            │              │            │             │             │           │        │
   │            │              │            │ 15. Encode descriptions   │           │        │
   │            │              │            │     (batch: 485)          │           │        │
   │            │              │            ├──────────────────────────────────────>│        │
   │            │              │            │             │             │           │        │
   │            │              │            │             │             │           │ 16. Batch encode
   │            │              │            │             │             │           │     485 texts
   │            │              │            │             │             │           ├────┐   │
   │            │              │            │             │             │           │    │   │
   │            │              │            │             │             │           │<───┘   │
   │            │              │            │             │             │           │ (~97s) │
   │            │              │            │             │             │           │        │
   │            │              │            │ 17. Return 485 embeddings │           │        │
   │            │              │            │<──────────────────────────────────────┤        │
   │            │              │            │             │             │           │        │
   │            │              │            │ 18. Check duplicates (each)          │        │
   │            │              │            ├─────────────────────────────────────────────>│
   │            │              │            │             │             │           │        │
   │            │              │            │             │             │           │ 19. Load existing KB
   │            │              │            │             │             │           │     (464 incidents)
   │            │              │            │             │             │           │<───┐   │
   │            │              │            │             │             │           │    │   │
   │            │              │            │             │             │           │<───┘   │
   │            │              │            │             │             │           │        │
   │            │              │            │             │             │           │ 20. Compare each new
   │            │              │            │             │             │           │     with existing
   │            │              │            │             │             │           │     (cosine sim >0.95)
   │            │              │            │             │             │           │<───┐   │
   │            │              │            │             │             │           │    │   │
   │            │              │            │             │             │           │<───┘   │
   │            │              │            │             │             │           │ (~3s)  │
   │            │              │            │             │             │           │        │
   │            │              │            │ 21. Duplicates: 47        │           │        │
   │            │              │            │     Unique: 438           │           │        │
   │            │              │            │<─────────────────────────────────────────────┤
   │            │              │            │             │             │           │        │
   │            │              │            │ 22. Add 438 to KB         │           │        │
   │            │              │            ├─────────────────────────────────────────────>│
   │            │              │            │             │             │           │        │
   │            │              │            │             │             │           │ 23. Append to incidents[]
   │            │              │            │             │             │           │<───┐   │
   │            │              │            │             │             │           │    │   │
   │            │              │            │             │             │           │<───┘   │
   │            │              │            │             │             │           │        │
   │            │              │            │             │             │           │ 24. Save to file
   │            │              │            │             │             │           │     knowledge_base.json
   │            │              │            │             │             │           │<───┐   │
   │            │              │            │             │             │           │    │   │
   │            │              │            │             │             │           │<───┘   │
   │            │              │            │             │             │           │ (~1s)  │
   │            │              │            │             │             │           │        │
   │            │              │            │             │             │           │ 25. Update version
   │            │              │            │             │             │           │     1.5 → 2.0
   │            │              │            │             │             │           │     incident_count: 902
   │            │              │            │             │             │           │<───┐   │
   │            │              │            │             │             │           │    │   │
   │            │              │            │             │             │           │<───┘   │
   │            │              │            │             │             │           │        │
   │            │              │            │ 26. KB updated            │           │        │
   │            │              │            │<─────────────────────────────────────────────┤
   │            │              │            │             │             │           │        │
   │            │              │ 27. update_last_sync_time()           │           │        │
   │            │              │     "2025-12-29T06:00:00Z"            │           │        │
   │            │              │            ├────┐        │             │           │        │
   │            │              │            │    │        │             │           │        │
   │            │              │            │<───┘        │             │           │        │
   │            │              │            │             │             │           │        │
   │            │              │            │ 28. Log summary          │           │        │
   │            │              │            │     [SUCCESS] Sync completed         │        │
   │            │              │            │     Fetched: 500                     │        │
   │            │              │            │     Validated: 485                   │        │
   │            │              │            │     Added: 438                       │        │
   │            │              │            │     Duplicates: 47                   │        │
   │            │              │            │     KB Total: 902                    │        │
   │            │              │            │     Time: 103 seconds                │        │
   │            │              │            ├────┐        │             │           │        │
   │            │              │            │    │        │             │           │        │
   │            │              │            │<───┘        │             │           │        │
   │            │              │            │             │             │           │        │
```

**Timeline:**
- Step 1-4: Trigger & initialization (~100ms)
- Step 5-9: ServiceNow API call (~2s)
- Step 10-14: Data validation (~3s for 500 incidents)
- Step 15-17: Batch encoding (~97s for 485 texts)
- Step 18-21: Duplicate detection (~3s)
- Step 22-26: KB update & save (~1s)
- Step 27-28: Logging (~10ms)
- **Total: ~106 seconds**

---

## 4. Batch Analysis with Clustering Sequence

```
Actor: User
Frontend: Browser
Backend: Flask Server
Categorizer: Incident Categorizer
SBERT: Sentence-BERT
HDBSCAN: Clustering Algorithm
KB: Knowledge Base

┌──────┐    ┌──────────┐    ┌─────────┐    ┌─────────────┐    ┌──────┐    ┌─────────┐    ┌────┐
│ User │    │ Frontend │    │ Backend │    │Categorizer  │    │SBERT │    │ HDBSCAN │    │ KB │
└──┬───┘    └────┬─────┘    └────┬────┘    └──────┬──────┘    └──┬───┘    └────┬────┘    └─┬──┘
   │             │               │                 │              │             │            │
   │ 1. Switch to│               │                 │              │             │            │
   │    Batch    │               │                 │              │             │            │
   │    Analysis │               │                 │              │             │            │
   │    tab      │               │                 │              │             │            │
   ├────────────>│               │                 │              │             │            │
   │             │               │                 │              │             │            │
   │ 2. Paste 50 │               │                 │              │             │            │
   │    incident │               │                 │              │             │            │
   │    descriptions             │                 │              │             │            │
   ├────────────>│               │                 │              │             │            │
   │             │               │                 │              │             │            │
   │ 3. Click    │               │                 │              │             │            │
   │    "Analyze │               │                 │              │             │            │
   │     Batch"  │               │                 │              │             │            │
   ├────────────>│               │                 │              │             │            │
   │             │               │                 │              │             │            │
   │             │ 4. Validate   │                 │              │             │            │
   │             │    (max 100)  │                 │              │             │            │
   │             ├───────┐       │                 │              │             │            │
   │             │       │       │                 │              │             │            │
   │             │<──────┘       │                 │              │             │            │
   │             │               │                 │              │             │            │
   │             │ 5. POST /analyze_batch          │              │             │            │
   │             │    Body: {incidents: [...]}     │              │             │            │
   │             ├──────────────>│                 │              │             │            │
   │             │               │                 │              │             │            │
   │             │               │ 6. Parse incidents (50)        │             │            │
   │             │               ├───────┐         │              │             │            │
   │             │               │       │         │              │             │            │
   │             │               │<──────┘         │              │             │            │
   │             │               │                 │              │             │            │
   │             │               │ 7. Get/Load Categorizer        │             │            │
   │             │               │    (lazy load)  │              │             │            │
   │             │               ├────────────────>│              │             │            │
   │             │               │                 │              │             │            │
   │             │               │                 │ 8. Load SBERT model        │            │
   │             │               │                 │    if needed │             │            │
   │             │               │                 ├─────────────>│             │            │
   │             │               │                 │              │             │            │
   │             │               │                 │ 9. Model ready             │            │
   │             │               │                 │<─────────────┤             │            │
   │             │               │                 │              │             │            │
   │             │               │ 10. analyze_batch()            │             │            │
   │             │               │     (50 incidents)             │             │            │
   │             │               ├────────────────>│              │             │            │
   │             │               │                 │              │             │            │
   │             │               │                 │ 11. Encode all 50 texts    │            │
   │             │               │                 ├─────────────>│             │            │
   │             │               │                 │              │             │            │
   │             │               │                 │              │ 12. Batch encoding       │
   │             │               │                 │              │     (50 × 200ms)         │
   │             │               │                 │              ├────────┐    │            │
   │             │               │                 │              │        │    │            │
   │             │               │                 │              │<───────┘    │            │
   │             │               │                 │              │ (~10s)      │            │
   │             │               │                 │              │             │            │
   │             │               │                 │ 13. Return 50 embeddings   │            │
   │             │               │                 │     (50 × 384-dim)         │            │
   │             │               │                 │<─────────────┤             │            │
   │             │               │                 │              │             │            │
   │             │               │                 │ 14. Run HDBSCAN clustering │            │
   │             │               │                 ├──────────────────────────>│            │
   │             │               │                 │              │             │            │
   │             │               │                 │              │             │ 15. Build density graph
   │             │               │                 │              │             │     (mutual reachability)
   │             │               │                 │              │             ├────────┐   │
   │             │               │                 │              │             │        │   │
   │             │               │                 │              │             │<───────┘   │
   │             │               │                 │              │             │            │
   │             │               │                 │              │             │ 16. Extract clusters
   │             │               │                 │              │             │     (condensed tree)
   │             │               │                 │              │             ├────────┐   │
   │             │               │                 │              │             │        │   │
   │             │               │                 │              │             │<───────┘   │
   │             │               │                 │              │             │            │
   │             │               │                 │              │             │ 17. Assign labels
   │             │               │                 │              │             │     [0,0,1,1,2,-1,0,...]
   │             │               │                 │              │             ├────────┐   │
   │             │               │                 │              │             │        │   │
   │             │               │                 │              │             │<───────┘   │
   │             │               │                 │              │             │ (~1s)      │
   │             │               │                 │              │             │            │
   │             │               │                 │ 18. Return cluster labels  │            │
   │             │               │                 │<──────────────────────────┤            │
   │             │               │                 │              │             │            │
   │             │               │                 │ 19. Analyze patterns       │            │
   │             │               │                 │     • Cluster 0: Keywords  │            │
   │             │               │                 │       ["email","password"] │            │
   │             │               │                 │     • Cluster 1: Keywords  │            │
   │             │               │                 │       ["vpn","connection"] │            │
   │             │               │                 │     • Cluster 2: Keywords  │            │
   │             │               │                 │       ["printer","queue"]  │            │
   │             │               │                 ├────────┐     │             │            │
   │             │               │                 │        │     │             │            │
   │             │               │                 │<───────┘     │             │            │
   │             │               │                 │ (~500ms)     │             │            │
   │             │               │                 │              │             │            │
   │             │               │                 │ 20. Calculate statistics   │            │
   │             │               │                 │     • Total clusters: 3     │            │
   │             │               │                 │     • Cluster 0: 20 items   │            │
   │             │               │                 │     • Cluster 1: 15 items   │            │
   │             │               │                 │     • Cluster 2: 10 items   │            │
   │             │               │                 │     • Noise: 5 items        │            │
   │             │               │                 ├────────┐     │             │            │
   │             │               │                 │        │     │             │            │
   │             │               │                 │<───────┘     │             │            │
   │             │               │                 │              │             │            │
   │             │               │ 21. Check for resolved incidents             │            │
   │             │               │     with resolutions            │             │            │
   │             │               │<────────────────┤              │             │            │
   │             │               │                 │              │             │            │
   │             │               │ 22. If found, add to KB (batch)│             │            │
   │             │               ├────────────────────────────────────────────────────────>│
   │             │               │                 │              │             │            │
   │             │               │                 │              │             │ 23. Bulk insert
   │             │               │                 │              │             │     (skip duplicates)
   │             │               │                 │              │             │<───────┐   │
   │             │               │                 │              │             │        │   │
   │             │               │                 │              │             │<───────┘   │
   │             │               │                 │              │             │ (~200ms)   │
   │             │               │                 │              │             │            │
   │             │               │ 24. KB updated  │              │             │            │
   │             │               │<────────────────────────────────────────────────────────┤
   │             │               │                 │              │             │            │
   │             │               │ 25. Return results             │             │            │
   │             │               │<────────────────┤              │             │            │
   │             │               │                 │              │             │            │
   │             │ 26. JSON Response               │              │             │            │
   │             │     {clusters: [                │              │             │            │
   │             │       {id: 0, count: 20,        │              │             │            │
   │             │        category: "Email",       │              │             │            │
   │             │        keywords: [...], ...},   │              │             │            │
   │             │       {id: 1, count: 15, ...},  │              │             │            │
   │             │       {id: 2, count: 10, ...}   │              │             │            │
   │             │     ]}          │              │             │            │
   │             │<────────────────┤              │             │            │
   │             │  (~12s total)   │              │             │            │
   │             │                 │              │             │            │
   │ 27. Display │                 │              │             │            │
   │     cluster │                 │              │             │            │
   │     results │                 │              │             │            │
   │<────────────┤                 │              │             │            │
   │             │                 │              │             │            │
   │ • Cluster 0:│                 │              │             │            │
   │   Email (20)│                 │              │             │            │
   │ • Cluster 1:│                 │              │             │            │
   │   Network(15)                │              │             │            │
   │ • Cluster 2:│                 │              │             │            │
   │   Hardware(10)               │              │             │            │
   │ • Noise: 5  │                 │              │             │            │
   │             │                 │              │             │            │
```

**Timeline:**
- Step 1-5: User interaction (~2s)
- Step 6-10: Initialization & loading (~100ms or 2s if first time)
- Step 11-13: Batch encoding (~10s for 50 texts)
- Step 14-18: HDBSCAN clustering (~1s)
- Step 19-20: Pattern analysis (~500ms)
- Step 21-24: KB update (~200ms)
- Step 25-27: Response & display (~100ms)
- **Total: ~12 seconds** (excluding user interaction)

---

## 5. PDF Export Sequence

```
Actor: User
Frontend: Browser
html2pdf: html2pdf.js Library
Browser: Browser APIs

┌──────┐         ┌──────────┐         ┌──────────┐         ┌─────────┐
│ User │         │ Frontend │         │ html2pdf │         │ Browser │
└──┬───┘         └────┬─────┘         └────┬─────┘         └────┬────┘
   │                  │                    │                    │
   │ 1. SOP displayed │                    │                    │
   │    in browser    │                    │                    │
   │<─────────────────┤                    │                    │
   │                  │                    │                    │
   │ 2. Click         │                    │                    │
   │    "Download     │                    │                    │
   │     PDF"         │                    │                    │
   ├─────────────────>│                    │                    │
   │                  │                    │                    │
   │                  │ 3. Get SOP HTML element                │
   │                  │    const element = document.getElementById('sop-output')
   │                  ├──────────┐         │                    │
   │                  │          │         │                    │
   │                  │<─────────┘         │                    │
   │                  │                    │                    │
   │                  │ 4. Configure PDF options               │
   │                  │    {margin: 10,    │                    │
   │                  │     filename: 'SOP_INC0020_20251229.pdf',
   │                  │     image: {type: 'jpeg', quality: 0.98},
   │                  │     html2canvas: {scale: 2},            │
   │                  │     jsPDF: {unit: 'mm', format: 'a4'}}  │
   │                  ├──────────┐         │                    │
   │                  │          │         │                    │
   │                  │<─────────┘         │                    │
   │                  │                    │                    │
   │                  │ 5. Call html2pdf() │                    │
   │                  ├───────────────────>│                    │
   │                  │                    │                    │
   │                  │                    │ 6. Clone HTML element
   │                  │                    │    (preserve original)
   │                  │                    ├──────────┐         │
   │                  │                    │          │         │
   │                  │                    │<─────────┘         │
   │                  │                    │                    │
   │                  │                    │ 7. Convert HTML to Canvas
   │                  │                    │    (html2canvas)   │
   │                  │                    ├───────────────────>│
   │                  │                    │                    │
   │                  │                    │                    │ 8. Render HTML to image
   │                  │                    │                    │    • Apply CSS styles
   │                  │                    │                    │    • Scale 2x for quality
   │                  │                    │                    │    • Capture colors
   │                  │                    │                    ├────────┐
   │                  │                    │                    │        │
   │                  │                    │                    │<───────┘
   │                  │                    │                    │ (~1-2s)
   │                  │                    │                    │
   │                  │                    │ 9. Return canvas   │
   │                  │                    │<───────────────────┤
   │                  │                    │                    │
   │                  │                    │ 10. Convert canvas to JPEG
   │                  │                    │     (98% quality)  │
   │                  │                    ├──────────┐         │
   │                  │                    │          │         │
   │                  │                    │<─────────┘         │
   │                  │                    │ (~500ms)           │
   │                  │                    │                    │
   │                  │                    │ 11. Create PDF (jsPDF)
   │                  │                    │     • A4 format    │
   │                  │                    │     • Add image to PDF
   │                  │                    │     • Set margins  │
   │                  │                    ├──────────┐         │
   │                  │                    │          │         │
   │                  │                    │<─────────┘         │
   │                  │                    │ (~300ms)           │
   │                  │                    │                    │
   │                  │                    │ 12. Trigger browser download
   │                  │                    ├───────────────────>│
   │                  │                    │                    │
   │                  │                    │                    │ 13. Save file dialog
   │                  │                    │                    │     "SOP_INC0020_20251229.pdf"
   │                  │                    │                    ├────────┐
   │                  │                    │                    │        │
   │                  │                    │                    │<───────┘
   │                  │                    │                    │
   │                  │ 14. Download complete                  │
   │                  │<───────────────────┤                    │
   │                  │                    │                    │
   │ 15. Show toast:  │                    │                    │
   │     "PDF         │                    │                    │
   │      downloaded" │                    │                    │
   │<─────────────────┤                    │                    │
   │                  │                    │                    │
```

**Timeline:**
- Step 1-5: User interaction & initialization (~100ms)
- Step 6-7: HTML cloning & preparation (~100ms)
- Step 8-9: HTML to Canvas conversion (~1-2s)
- Step 10: Canvas to JPEG (~500ms)
- Step 11: PDF creation (~300ms)
- Step 12-15: Browser download (~100ms)
- **Total: ~2-3 seconds**

---

## 6. Error Handling Sequence

```
Actor: User
Frontend: Browser
Backend: Flask Server
ErrorHandler: Error Handler

┌──────┐         ┌──────────┐         ┌─────────┐         ┌──────────────┐
│ User │         │ Frontend │         │ Backend │         │ErrorHandler  │
└──┬───┘         └────┬─────┘         └────┬────┘         └──────┬───────┘
   │                  │                    │                      │
   │ 1. Submit form   │                    │                      │
   │    (invalid data)│                    │                      │
   ├─────────────────>│                    │                      │
   │                  │                    │                      │
   │                  │ 2. Client-side validation                │
   │                  ├──────────┐         │                      │
   │                  │          │         │                      │
   │                  │<─────────┘         │                      │
   │                  │                    │                      │
   │                  │ 3. If valid, POST request                │
   │                  ├───────────────────>│                      │
   │                  │                    │                      │
   │                  │                    │ 4. Server validation │
   │                  │                    │    (required fields) │
   │                  │                    ├──────────┐           │
   │                  │                    │          │           │
   │                  │                    │<─────────┘           │
   │                  │                    │                      │
   │                  │                    │ 5. Validation failed │
   │                  │                    │    (missing field)   │
   │                  │                    ├─────────────────────>│
   │                  │                    │                      │
   │                  │                    │                      │ 6. Log error
   │                  │                    │                      │    [ERROR] Missing field: description
   │                  │                    │                      ├────────┐
   │                  │                    │                      │        │
   │                  │                    │                      │<───────┘
   │                  │                    │                      │
   │                  │                    │                      │ 7. Format error response
   │                  │                    │                      │    {success: false,
   │                  │                    │                      │     error: "Missing field",
   │                  │                    │                      │     field: "description"}
   │                  │                    │                      ├────────┐
   │                  │                    │                      │        │
   │                  │                    │                      │<───────┘
   │                  │                    │                      │
   │                  │                    │ 8. Return error      │
   │                  │                    │<─────────────────────┤
   │                  │                    │                      │
   │                  │ 9. HTTP 400 Bad Request                  │
   │                  │    JSON: {success: false, error: "..."}  │
   │                  │<───────────────────┤                      │
   │                  │                    │                      │
   │                  │ 10. Parse error    │                      │
   │                  ├──────────┐         │                      │
   │                  │          │         │                      │
   │                  │<─────────┘         │                      │
   │                  │                    │                      │
   │ 11. Show error   │                    │                      │
   │     toast:       │                    │                      │
   │     "Missing     │                    │                      │
   │      field:      │                    │                      │
   │      description"│                    │                      │
   │<─────────────────┤                    │                      │
   │                  │                    │                      │
   │ 12. Highlight    │                    │                      │
   │     field in red │                    │                      │
   │<─────────────────┤                    │                      │
   │                  │                    │                      │
   │ 13. Fix data &   │                    │                      │
   │     resubmit     │                    │                      │
   ├─────────────────>│                    │                      │
   │                  │                    │                      │
   │                  │ 14. POST (valid)   │                      │
   │                  ├───────────────────>│                      │
   │                  │                    │                      │
   │                  │                    │ 15. Success          │
   │                  │                    │<─────────────────────┤
   │                  │                    │                      │
   │                  │ 16. HTTP 200 OK    │                      │
   │                  │<───────────────────┤                      │
   │                  │                    │                      │
   │ 17. Show success │                    │                      │
   │<─────────────────┤                    │                      │
   │                  │                    │                      │
```

---

## Legend

```
Actor: External entity (user, cron, system)
Component: Internal module/service
│ : Vertical timeline
├─>: Action/request flow
<─┤: Response/return flow
┌─┐
│ │: Processing box
└─┘
(~Xms): Processing time
```

## Notes

1. **Timing Estimates:** All timing values are approximate and based on:
   - Intel Core i5 or equivalent CPU
   - 8GB RAM
   - Standard network latency (50-100ms)
   - Local deployment (not cloud)

2. **Error Handling:** All sequences include implicit error handling with try-catch blocks and proper HTTP status codes

3. **Caching:** ML models and embeddings are cached after first load for performance

4. **Concurrency:** Backend can handle multiple requests simultaneously with proper thread safety

5. **Optimization:** Lazy loading reduces initial startup time from 15s to ~2s
