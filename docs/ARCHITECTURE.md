# Architecture Overview

## System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    SOP Creation System                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Orchestrator                           │
│  (Coordinates all components and manages workflow)          │
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌──────────────────┐ ┌─────────────────┐ ┌────────────────┐
│   ServiceNow     │ │ Data Validation │ │ Categorization │
│   Integration    │ │                 │ │   (ML Engine)  │
└──────────────────┘ └─────────────────┘ └────────────────┘
          │                   │                   │
          │                   │                   │
          ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    SOP Generation                           │
│          (Creates SOPs from analyzed clusters)              │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Incident Retrieval

```
ServiceNow API
     │
     │ Fetch incidents (last N days)
     ▼
Raw Incident Data
     │
     │ JSON format
     ▼
data/incidents/incidents_[timestamp].json
```

### 2. Data Validation

```
Raw Incidents
     │
     │ Validate quality
     ▼
┌────────────────────┐
│  Data Validator    │
│  • Check required  │
│  • Check length    │
│  • Detect dupes    │
│  • Find issues     │
└────────────────────┘
     │
     ├─────────────────┐
     │                 │
     ▼                 ▼
Valid Incidents   Invalid Incidents
     │                 │
     │                 └──> data/validated/invalid_*.json
     │
     ▼
data/validated/valid_[timestamp].json
```

### 3. Categorization (ML Pipeline)

```
Valid Incidents
     │
     ▼
┌─────────────────────────────────────┐
│     Feature Extraction              │
│  Combine: description + resolution  │
│           + category + symptoms     │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│     Sentence Embeddings             │
│  Model: all-MiniLM-L6-v2            │
│  Output: 384-dim vectors            │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│     Clustering (HDBSCAN)            │
│  • Min cluster size: 5              │
│  • Metric: cosine similarity        │
│  • Auto-detect cluster count        │
└─────────────────────────────────────┘
     │
     ▼
Incident Clusters
     │
     ├──> Cluster 0: Network issues
     ├──> Cluster 1: Password resets
     ├──> Cluster 2: Email problems
     └──> Cluster N: ...
     │
     ▼
data/clusters/clusters_[timestamp].json
```

### 4. SOP Generation

```
For Each Cluster:
     │
     ▼
┌─────────────────────────────────────┐
│     Cluster Analysis                │
│  • Extract common patterns          │
│  • Identify resolution steps        │
│  • Find representative incident     │
│  • Calculate statistics             │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│     SOP Template Filling            │
│  Sections:                          │
│  • Overview                         │
│  • Problem Statement                │
│  • Symptoms                         │
│  • Resolution Steps                 │
│  • Verification                     │
│  • Related Incidents                │
└─────────────────────────────────────┘
     │
     ▼
SOP Document (Markdown)
     │
     ▼
output/sops/SOP-[id]_[timestamp].md
```

## Key Technologies

### Backend Framework
- **Python 3.8+**: Core language
- **asyncio**: Asynchronous operations (future enhancement)

### ServiceNow Integration
- **requests**: HTTP client
- **pysnow**: ServiceNow API wrapper

### Data Processing
- **pandas**: Data manipulation
- **numpy**: Numerical operations

### Machine Learning
- **sentence-transformers**: Text embeddings
- **scikit-learn**: ML utilities
- **HDBSCAN**: Density-based clustering

### NLP
- **Sentence Transformers**: Semantic text understanding
- Model: `all-MiniLM-L6-v2` (384 dimensions, fast)

### Configuration & Logging
- **python-dotenv**: Environment variables
- **PyYAML**: Configuration files
- **loguru**: Advanced logging

## Design Patterns

### 1. Factory Pattern
Used for creating components from configuration:
```python
create_validator_from_config(config)
create_categorizer_from_config(config)
create_generator_from_config(config)
```

### 2. Pipeline Pattern
Sequential processing with data transformation:
```python
fetch → validate → categorize → generate
```

### 3. Strategy Pattern
Different validation and generation strategies:
- Validation rules
- Clustering algorithms
- Template formats

## Scalability Considerations

### Current Limitations
- Single-threaded processing
- In-memory data structures
- Local file storage

### Future Enhancements
- **Distributed Processing**: Process large datasets in parallel
- **Database Integration**: PostgreSQL/MongoDB for data storage
- **Caching**: Redis for embeddings cache
- **API Service**: REST API for integration
- **Streaming**: Process incidents in real-time

## Security

### Current Implementation
- Environment variables for credentials
- HTTPS for ServiceNow API
- No data storage of credentials

### Recommendations
- Use OAuth instead of basic auth
- Implement credential rotation
- Add encryption for stored data
- Audit logging for compliance

## Monitoring & Observability

### Logging Levels
- **DEBUG**: Detailed diagnostic information
- **INFO**: General operational information
- **WARNING**: Warning messages
- **ERROR**: Error events

### Metrics Tracked
- Total incidents fetched
- Validation success rate
- Number of clusters formed
- SOPs generated
- Processing time

### Output Artifacts
1. **Raw Data**: `data/incidents/`
2. **Validation Results**: `data/validated/`
3. **Clusters**: `data/clusters/`
4. **SOPs**: `output/sops/`
5. **Reports**: `output/reports/`
6. **Logs**: `logs/`
