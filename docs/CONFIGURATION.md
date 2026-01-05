# Configuration Guide

## Overview

The system is configured through two main files:
- `.env` - Environment variables and credentials
- `config.yaml` - Application settings and parameters

## Environment Variables (.env)

### ServiceNow Connection

```env
# ServiceNow instance URL (without https://)
SERVICENOW_INSTANCE=your-instance.service-now.com

# Basic Authentication
SERVICENOW_USERNAME=your-username
SERVICENOW_PASSWORD=your-password

# Alternative: OAuth (if using OAuth instead of basic auth)
# SERVICENOW_CLIENT_ID=your-client-id
# SERVICENOW_CLIENT_SECRET=your-client-secret
```

### Application Settings

```env
# Logging level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO

# Output directory for SOPs and reports
OUTPUT_DIR=./output

# Data directory for intermediate files
DATA_DIR=./data
```

### ML Configuration

```env
# Minimum incidents to form a cluster
MIN_CLUSTER_SIZE=5

# Similarity threshold (0.0 to 1.0)
SIMILARITY_THRESHOLD=0.75

# Sentence transformer model
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

## Application Configuration (config.yaml)

### ServiceNow Settings

```yaml
servicenow:
  # Fields to retrieve from incidents
  fields:
    - number
    - short_description
    - description
    - priority
    - category
    - subcategory
    - assignment_group
    - state
    - resolution_notes
    - close_notes
    - sys_created_on
    - resolved_at
  
  # Query filters
  query:
    state: closed          # Only closed incidents
    min_priority: 3        # Priority 3 or higher
    days_back: 90          # Last 90 days
```

### Data Validation

```yaml
data_validation:
  # Required fields for valid incidents
  required_fields:
    - number
    - short_description
    - resolution_notes
    - category
  
  # Minimum content length (characters)
  min_description_length: 20
  min_resolution_length: 30
  
  # Quality checks to perform
  checks:
    - missing_data
    - duplicate_detection
    - inconsistent_categorization
    - insufficient_detail
```

### Categorization (ML Settings)

```yaml
categorization:
  # Model for generating text embeddings
  embedding_model: all-MiniLM-L6-v2
  
  # Clustering algorithm
  clustering_algorithm: hdbscan
  
  # Minimum incidents to form a cluster
  min_cluster_size: 5
  
  # Minimum samples for core points
  min_samples: 3
  
  # Similarity threshold for grouping
  similarity_threshold: 0.75
  
  # Features to use for clustering
  features:
    - description
    - resolution_notes
    - category
```

### SOP Generation

```yaml
sop_generation:
  # Output format
  template_format: markdown
  
  # Sections to include in SOPs
  include_sections:
    - overview
    - problem_statement
    - symptoms
    - prerequisites
    - resolution_steps
    - verification
    - related_incidents
    - metadata
  
  # Quality requirements
  min_incidents_for_sop: 3      # Minimum incidents needed
  max_incidents_in_cluster: 100 # Maximum to include
  
  # Output settings
  output_format: markdown
  include_diagrams: false
```

### Logging

```yaml
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: logs/app.log
```

## Tuning Guidelines

### For Higher Quality SOPs

- Increase `min_cluster_size` to 7-10
- Increase `min_incidents_for_sop` to 5+
- Raise `min_resolution_length` to 50+

### For More SOPs (Lower Threshold)

- Decrease `min_cluster_size` to 3-4
- Decrease `min_incidents_for_sop` to 2
- Lower `similarity_threshold` to 0.65

### For Better Categorization

- Use a larger embedding model (e.g., `all-mpnet-base-v2`)
- Adjust `min_samples` to control noise sensitivity
- Increase `similarity_threshold` for tighter clusters

### For Specific Incident Types

Add filters to `servicenow.query`:

```yaml
query:
  state: closed
  category: "Network"              # Specific category
  assignment_group: "L2 Support"   # Specific team
  priority: 1,2                    # High priority only
```

## Performance Considerations

### Large Datasets (10,000+ incidents)

```yaml
categorization:
  embedding_model: all-MiniLM-L6-v2  # Faster, smaller model
  min_cluster_size: 10                # Larger clusters
```

### Small Datasets (< 1,000 incidents)

```yaml
categorization:
  embedding_model: all-mpnet-base-v2  # Better quality
  min_cluster_size: 3                  # Smaller clusters
  similarity_threshold: 0.65           # More inclusive
```

## Example Configurations

### High-Volume Production Environment

```yaml
servicenow:
  query:
    days_back: 30  # Recent incidents only

data_validation:
  min_description_length: 50
  min_resolution_length: 100

categorization:
  min_cluster_size: 10
  min_samples: 5

sop_generation:
  min_incidents_for_sop: 10
```

### Development/Testing

```yaml
servicenow:
  query:
    days_back: 180  # More historical data

categorization:
  min_cluster_size: 3
  min_samples: 2

sop_generation:
  min_incidents_for_sop: 2
```
