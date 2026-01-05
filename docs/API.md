# API Reference

## Main Orchestrator

### `SOPOrchestrator`

Main class that coordinates the entire SOP generation pipeline.

```python
from main import SOPOrchestrator

orchestrator = SOPOrchestrator(config_path="config.yaml")
```

#### Methods

##### `run_full_pipeline(days_back=90, limit=None)`

Run the complete SOP generation pipeline.

**Parameters:**
- `days_back` (int): Number of days to look back for incidents (default: 90)
- `limit` (int, optional): Maximum number of incidents to process

**Returns:**
- `dict`: Results dictionary with status and metrics

**Example:**
```python
result = orchestrator.run_full_pipeline(days_back=30, limit=1000)
print(f"Generated {result['sops_generated']} SOPs")
```

##### `fetch_incidents(days_back=90, limit=None)`

Fetch incidents from ServiceNow.

**Returns:**
- `list`: List of incident dictionaries

##### `validate_incidents(incidents)`

Validate incident data quality.

**Returns:**
- `tuple`: (valid_incidents, invalid_incidents)

##### `categorize_incidents(incidents)`

Categorize incidents into clusters using ML.

**Returns:**
- `dict`: Dictionary mapping cluster_id to incident list

##### `generate_sops(clusters)`

Generate SOP documents from clusters.

**Returns:**
- `list`: List of generated SOP file paths

---

## ServiceNow Client

### `ServiceNowClient`

Client for interacting with ServiceNow API.

```python
from src.servicenow import ServiceNowClient

client = ServiceNowClient(
    instance="instance.service-now.com",
    username="user",
    password="pass"
)
```

#### Methods

##### `test_connection()`

Test connection to ServiceNow.

**Returns:**
- `bool`: True if connection successful

##### `fetch_incidents(fields, days_back=90, state="closed", limit=None)`

Fetch incidents from ServiceNow.

**Parameters:**
- `fields` (list): List of field names to retrieve
- `days_back` (int): Number of days to look back
- `state` (str): Incident state filter
- `limit` (int, optional): Maximum records

**Returns:**
- `list`: List of incident records

**Example:**
```python
incidents = client.fetch_incidents(
    fields=["number", "description", "resolution_notes"],
    days_back=30,
    state="closed"
)
```

##### `get_incident_by_number(incident_number)`

Get specific incident by number.

**Parameters:**
- `incident_number` (str): Incident number (e.g., "INC0012345")

**Returns:**
- `dict` or `None`: Incident record

---

## Data Validator

### `DataValidator`

Validates incident data quality.

```python
from src.data_validation import DataValidator

validator = DataValidator(
    required_fields=["number", "description", "resolution_notes"],
    min_description_length=20,
    min_resolution_length=30
)
```

#### Methods

##### `validate_incidents(incidents)`

Validate all incidents.

**Parameters:**
- `incidents` (list): List of incident dictionaries

**Returns:**
- `tuple`: (valid_incidents, invalid_incidents)

**Example:**
```python
valid, invalid = validator.validate_incidents(incidents)
print(f"Valid: {len(valid)}, Invalid: {len(invalid)}")
```

##### `validate_incident(incident)`

Validate a single incident.

**Parameters:**
- `incident` (dict): Incident dictionary

**Returns:**
- `dict`: Validation result with errors

##### `detect_duplicates(incidents)`

Detect potential duplicate incidents.

**Returns:**
- `list`: List of duplicate groups

##### `generate_quality_report(valid, invalid)`

Generate data quality report.

**Returns:**
- `dict`: Quality metrics and error summary

---

## Incident Categorizer

### `IncidentCategorizer`

Categorizes incidents using machine learning.

```python
from src.categorization import IncidentCategorizer

categorizer = IncidentCategorizer(
    embedding_model="all-MiniLM-L6-v2",
    min_cluster_size=5,
    min_samples=3,
    similarity_threshold=0.75
)
```

#### Methods

##### `categorize_incidents(incidents)`

Categorize incidents into clusters.

**Parameters:**
- `incidents` (list): List of validated incidents

**Returns:**
- `dict`: Dictionary mapping cluster_id to incidents

**Example:**
```python
clusters = categorizer.categorize_incidents(valid_incidents)
for cluster_id, cluster_incidents in clusters.items():
    print(f"Cluster {cluster_id}: {len(cluster_incidents)} incidents")
```

##### `analyze_cluster(cluster_id, incidents)`

Analyze a cluster to extract patterns.

**Parameters:**
- `cluster_id` (int): Cluster identifier
- `incidents` (list): Incidents in cluster

**Returns:**
- `dict`: Analysis with common patterns and statistics

**Example:**
```python
analysis = categorizer.analyze_cluster(0, cluster_incidents)
print(f"Common categories: {analysis['common_categories']}")
print(f"Avg resolution time: {analysis['avg_resolution_time']} hours")
```

---

## SOP Generator

### `SOPGenerator`

Generates SOP documents from incident clusters.

```python
from src.sop_generation import SOPGenerator

generator = SOPGenerator(
    min_incidents=3,
    template_format="markdown"
)
```

#### Methods

##### `generate_sop(cluster_id, incidents, analysis)`

Generate SOP from incident cluster.

**Parameters:**
- `cluster_id` (int): Cluster identifier
- `incidents` (list): Incidents in cluster
- `analysis` (dict): Cluster analysis data

**Returns:**
- `str` or `None`: Generated SOP content

**Example:**
```python
sop_content = generator.generate_sop(
    cluster_id=1,
    incidents=cluster_incidents,
    analysis=analysis
)

if sop_content:
    with open("SOP-0001.md", "w") as f:
        f.write(sop_content)
```

##### `generate_summary_report(all_sops)`

Generate summary report of all SOPs.

**Parameters:**
- `all_sops` (list): List of SOP data dictionaries

**Returns:**
- `str`: Summary report

---

## Helper Functions

### Configuration Helpers

#### `create_client_from_env()`

Create ServiceNow client from environment variables.

```python
from src.servicenow import create_client_from_env

client = create_client_from_env()
```

#### `create_validator_from_config(config)`

Create validator from configuration.

```python
from src.data_validation import create_validator_from_config

validator = create_validator_from_config(config)
```

#### `create_categorizer_from_config(config)`

Create categorizer from configuration.

```python
from src.categorization import create_categorizer_from_config

categorizer = create_categorizer_from_config(config)
```

#### `create_generator_from_config(config)`

Create SOP generator from configuration.

```python
from src.sop_generation import create_generator_from_config

generator = create_generator_from_config(config)
```

---

## Data Structures

### Incident Dictionary

```python
{
    "number": "INC0012345",
    "short_description": "Unable to access email",
    "description": "User reports unable to access email...",
    "priority": "3",
    "category": "Email",
    "subcategory": "Access Issue",
    "assignment_group": "L2 Support",
    "state": "7",  # Closed
    "resolution_notes": "Reset password and cleared cache...",
    "close_notes": "Issue resolved",
    "sys_created_on": "2025-01-15T10:30:00Z",
    "resolved_at": "2025-01-15T11:45:00Z",
    "closed_at": "2025-01-15T12:00:00Z"
}
```

### Validation Result

```python
{
    "is_valid": False,
    "errors": [
        {
            "type": "insufficient_resolution",
            "message": "Resolution notes too short (15 chars)",
            "severity": "high"
        }
    ],
    "incident_number": "INC0012345"
}
```

### Cluster Analysis

```python
{
    "cluster_id": 0,
    "incident_count": 25,
    "common_categories": {
        "Email": 20,
        "Access": 5
    },
    "common_patterns": ["password", "reset", "access", "email"],
    "representative_incident": "INC0012345",
    "priority_distribution": {
        "1": 2,
        "2": 8,
        "3": 15
    },
    "avg_resolution_time": 2.5
}
```

### Pipeline Result

```python
{
    "status": "success",
    "total_incidents": 1000,
    "valid_incidents": 850,
    "invalid_incidents": 150,
    "clusters": 15,
    "sops_generated": 12,
    "duration_seconds": 245.67,
    "sop_files": [
        "output/sops/SOP-0001_20250120_120000.md",
        "output/sops/SOP-0002_20250120_120000.md"
    ]
}
```
