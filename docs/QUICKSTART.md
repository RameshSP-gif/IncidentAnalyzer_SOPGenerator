# Quick Start Guide

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Incident_Analyser_SOP_Creator
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLP models** (first-time setup)
   ```bash
   python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
   ```

## Configuration

1. **Create environment file**
   ```bash
   copy .env.example .env
   ```

2. **Edit `.env` with your ServiceNow credentials**
   ```env
   SERVICENOW_INSTANCE=your-instance.service-now.com
   SERVICENOW_USERNAME=your-username
   SERVICENOW_PASSWORD=your-password
   ```

3. **Review `config.yaml`** and adjust settings as needed

## Usage

### Basic Usage - Generate SOPs from Last 90 Days

```bash
python main.py
```

This will:
1. Fetch closed incidents from the last 90 days
2. Validate data quality
3. Categorize incidents using ML
4. Generate SOPs for each category

### Fetch Incidents Only

```bash
python main.py --fetch --days 30
```

### Limit Number of Incidents

```bash
python main.py --limit 500
```

### Custom Time Range

```bash
python main.py --days 180
```

## Output

After running, you'll find:

- **`data/incidents/`** - Raw incident data from ServiceNow
- **`data/validated/`** - Validated incidents (valid and invalid)
- **`data/clusters/`** - Categorized incident groups
- **`output/sops/`** - Generated SOP documents (Markdown)
- **`output/reports/`** - Quality and analysis reports
- **`logs/`** - Application logs

## Viewing Results

1. **Check the summary report**
   ```
   output/reports/sop_summary_[timestamp].md
   ```

2. **Open individual SOPs**
   ```
   output/sops/SOP-0001_[timestamp].md
   ```

3. **Review quality metrics**
   ```
   output/reports/quality_report_[timestamp].json
   ```

## Troubleshooting

### Connection Issues

If you get connection errors:
```bash
# Test ServiceNow connection
python -c "from src.servicenow import create_client_from_env; client = create_client_from_env(); print('Connected!' if client.test_connection() else 'Failed')"
```

### Memory Issues

For large datasets, process in batches:
```bash
python main.py --limit 1000
```

### Missing Dependencies

Reinstall requirements:
```bash
pip install -r requirements.txt --force-reinstall
```

## Next Steps

1. Review and customize generated SOPs
2. Adjust `config.yaml` for better results
3. Fine-tune clustering parameters
4. Add custom templates for SOP generation

## Support

For issues and questions, check:
- Application logs in `logs/app.log`
- Validation errors in `data/validated/invalid_*.json`
- Configuration in `config.yaml`
