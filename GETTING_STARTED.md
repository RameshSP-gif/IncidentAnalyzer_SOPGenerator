# Getting Started with SOP Creator

## 📋 Prerequisites

Before you begin, ensure you have:

- ✅ Python 3.8 or higher installed
- ✅ Access to a ServiceNow instance
- ✅ ServiceNow credentials with incident read permissions
- ✅ 2GB RAM minimum (4GB recommended)
- ✅ Internet connection for downloading ML models

## 🎯 Installation Steps

### Step 1: Clone or Download the Project

```bash
cd c:\Incident_Analyser_SOP_Creator
```

### Step 2: Create Virtual Environment (Recommended)

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

This will install:
- ServiceNow API clients
- Machine learning libraries
- NLP models
- Data processing tools

**Note**: First installation may take 5-10 minutes as it downloads ML models (~200MB).

### Step 4: Configure Environment

```powershell
# Copy the example environment file
copy .env.example .env

# Edit .env file with your ServiceNow credentials
notepad .env
```

Update these values in `.env`:
```env
SERVICENOW_INSTANCE=your-instance.service-now.com
SERVICENOW_USERNAME=your-username
SERVICENOW_PASSWORD=your-password
```

**Important**: 
- Don't include `https://` in the instance URL
- Use your actual ServiceNow credentials
- Keep this file secure and never commit it

### Step 5: Verify Setup

```powershell
python setup.py
```

This checks:
- ✓ Python version
- ✓ Dependencies installed
- ✓ Configuration files
- ✓ Directory structure
- ✓ ServiceNow connection

## 🚀 Your First Run

### Test with Limited Data

For your first run, test with a small dataset:

```powershell
python main.py --days 7 --limit 100
```

This will:
1. Fetch the last 7 days of closed incidents (max 100)
2. Validate data quality
3. Categorize incidents
4. Generate SOPs

**Expected time**: 1-2 minutes

### Check the Results

```powershell
# View generated SOPs
dir output\sops\

# View summary report
notepad output\reports\sop_summary_*.md

# Check quality metrics
notepad output\reports\quality_report_*.json
```

## 📊 Understanding the Output

### Directory Structure After First Run

```
Incident_Analyser_SOP_Creator/
├── data/
│   ├── incidents/
│   │   └── incidents_20251120_120000.json    # Raw data
│   ├── validated/
│   │   ├── valid_20251120_120000.json        # Valid incidents
│   │   └── invalid_20251120_120000.json      # Invalid incidents
│   └── clusters/
│       └── clusters_20251120_120000.json     # Categorized groups
│
├── output/
│   ├── sops/
│   │   ├── SOP-0001_20251120_120000.md       # Generated SOPs
│   │   ├── SOP-0002_20251120_120000.md
│   │   └── ...
│   └── reports/
│       ├── quality_report_20251120_120000.json
│       ├── cluster_analyses_20251120_120000.json
│       └── sop_summary_20251120_120000.md
│
└── logs/
    └── app.log                                # Application logs
```

### Sample SOP Output

Open any SOP file (e.g., `output/sops/SOP-0001_*.md`) to see:

```markdown
# Standard Operating Procedure

## SOP Information
- **SOP ID**: SOP-0001
- **Category**: Email
- **Based on**: 15 incidents
- **Average Resolution Time**: 2.3 hours

## Problem Statement
Common problems addressed:
1. Unable to access email
2. Email not syncing
...

## Resolution Steps
### Step 1
Reset user password...

### Step 2
Clear browser cache...
```

## ⚙️ Configuration

### Adjust for Your Environment

Edit `config.yaml` to customize:

```yaml
# Fetch more/fewer incidents
servicenow:
  query:
    days_back: 90  # Change from 90 to 30 or 180

# Adjust clustering sensitivity
categorization:
  min_cluster_size: 5  # Lower = more clusters
  similarity_threshold: 0.75  # Lower = looser grouping

# Require more/fewer incidents per SOP
sop_generation:
  min_incidents_for_sop: 3  # Higher = higher quality
```

## 🎓 Common Use Cases

### Use Case 1: Generate SOPs for Specific Category

```yaml
# In config.yaml, add category filter
servicenow:
  query:
    state: closed
    category: "Network"  # Only network incidents
```

```powershell
python main.py
```

### Use Case 2: High-Priority Incidents Only

```yaml
servicenow:
  query:
    state: closed
    priority: "1,2"  # Only P1 and P2
```

### Use Case 3: Recent Incidents (Last Month)

```powershell
python main.py --days 30
```

### Use Case 4: Large Dataset Analysis

```powershell
# Process in batches
python main.py --days 90 --limit 5000
```

## 🔍 Troubleshooting First Run

### Problem: "Failed to connect to ServiceNow"

**Solutions**:
1. Check `.env` file has correct credentials
2. Verify instance URL format: `instance.service-now.com` (no https://)
3. Test connectivity: `ping your-instance.service-now.com`
4. Check firewall settings

### Problem: "No incidents fetched"

**Solutions**:
1. Increase time range: `--days 180`
2. Check ServiceNow has closed incidents
3. Remove filters in `config.yaml`
4. Verify account has read permissions

### Problem: "No clusters created"

**Solutions**:
1. Lower `min_cluster_size` in `config.yaml` to 3
2. Fetch more incidents: increase `--days`
3. Lower `similarity_threshold` to 0.65

### Problem: "No SOPs generated"

**Solutions**:
1. Lower `min_incidents_for_sop` to 2 in `config.yaml`
2. Check if clusters were created (see previous issue)
3. Review cluster analyses in `output/reports/`

## 📈 Next Steps

### 1. Review Generated SOPs
- Open SOPs in `output/sops/`
- Check if they make sense
- Customize as needed

### 2. Tune Parameters
- Adjust `config.yaml` based on results
- Run again with optimized settings

### 3. Schedule Regular Runs
- Run monthly or quarterly
- Keep SOPs up-to-date

### 4. Integrate with Your Process
- Export SOPs to your knowledge base
- Share with support teams
- Track SOP usage

## 💡 Tips for Success

1. **Start Small**: Test with 100-500 incidents first
2. **Review Quality**: Check validation reports
3. **Iterate**: Refine configuration based on results
4. **Document**: Customize SOPs for your environment
5. **Feedback**: Gather feedback from users

## 📚 Learn More

- **[Configuration Guide](docs/CONFIGURATION.md)** - Detailed settings
- **[Examples](examples/)** - Code examples
- **[API Documentation](docs/API.md)** - Programmatic usage
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues

## 🆘 Need Help?

1. Check logs: `logs/app.log`
2. Enable debug mode in `.env`: `LOG_LEVEL=DEBUG`
3. Review troubleshooting guide
4. Check example scripts
5. Review configuration

## ✅ Checklist

Before moving to production, ensure:

- [ ] Python 3.8+ installed
- [ ] All dependencies installed
- [ ] `.env` configured with credentials
- [ ] `config.yaml` reviewed
- [ ] Test run completed successfully
- [ ] Output reviewed and validated
- [ ] Parameters tuned for your data
- [ ] Documentation reviewed
- [ ] Team trained on usage

## 🎉 You're Ready!

You now have a working SOP creation system. Run it regularly to:
- Save hours of manual documentation
- Keep SOPs current
- Identify patterns
- Improve support efficiency

**Happy automating!** 🚀
