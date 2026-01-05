# Troubleshooting Guide

## Common Issues and Solutions

### Installation Issues

#### Issue: `pip install` fails with compilation errors

**Solution:**
```bash
# Upgrade pip and setuptools
python -m pip install --upgrade pip setuptools wheel

# Retry installation
pip install -r requirements.txt
```

#### Issue: `sentence-transformers` installation takes too long

**Solution:**
This is normal for first-time installation as it downloads models (~80MB). Subsequent runs will use cached models.

```bash
# Pre-download the model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

---

### Connection Issues

#### Issue: "Failed to connect to ServiceNow"

**Possible Causes & Solutions:**

1. **Incorrect credentials**
   ```bash
   # Verify .env file
   cat .env
   # or on Windows
   type .env
   ```
   - Check SERVICENOW_INSTANCE (no https://)
   - Verify username and password

2. **Network/Firewall blocking**
   ```bash
   # Test connectivity
   curl https://your-instance.service-now.com/api/now/table/incident?sysparm_limit=1
   ```

3. **Invalid instance URL**
   - Ensure format is: `instance.service-now.com`
   - NOT: `https://instance.service-now.com`

#### Issue: "401 Unauthorized"

**Solution:**
- Verify username and password in `.env`
- Check if account is active in ServiceNow
- Ensure account has proper read permissions for incident table

#### Issue: "403 Forbidden"

**Solution:**
- Your account lacks permissions to access incident data
- Contact ServiceNow administrator to grant incident read access

---

### Data Issues

#### Issue: "No incidents fetched"

**Possible Causes:**

1. **Date range too restrictive**
   ```bash
   # Try a longer time range
   python main.py --days 180
   ```

2. **Query filters too strict**
   - Check `config.yaml` servicenow.query section
   - Adjust state, priority filters

3. **No incidents in ServiceNow**
   ```bash
   # Test with unlimited query
   python main.py --days 365 --limit 100
   ```

#### Issue: "No valid incidents"

**Solution:**
Most incidents failed validation. Check validation report:
```bash
# View invalid incidents
cat data/validated/invalid_[timestamp].json

# View quality report
cat output/reports/quality_report_[timestamp].json
```

Common fixes:
- Lower validation thresholds in `config.yaml`
- Improve incident data quality in ServiceNow
- Adjust required_fields list

---

### Clustering Issues

#### Issue: "No clusters created"

**Possible Causes:**

1. **Not enough valid incidents**
   - Need at least `min_cluster_size` similar incidents
   - Solution: Lower `min_cluster_size` in config.yaml

2. **Incidents too dissimilar**
   ```yaml
   # In config.yaml
   categorization:
     similarity_threshold: 0.65  # Lower from 0.75
     min_cluster_size: 3         # Lower from 5
   ```

3. **Insufficient data**
   - Fetch more incidents: `--days 180`
   - Remove filters to get more data

#### Issue: "All incidents marked as noise"

**Solution:**
Clustering is too strict. Adjust parameters:
```yaml
categorization:
  min_cluster_size: 3     # Lower
  min_samples: 2          # Lower
  similarity_threshold: 0.70  # Lower
```

---

### SOP Generation Issues

#### Issue: "No SOPs generated"

**Cause:** Clusters don't meet minimum incident threshold

**Solution:**
```yaml
sop_generation:
  min_incidents_for_sop: 2  # Lower from 3
```

#### Issue: "SOPs have poor quality"

**Solutions:**

1. **Increase quality thresholds**
   ```yaml
   data_validation:
     min_description_length: 50
     min_resolution_length: 100
   
   sop_generation:
     min_incidents_for_sop: 5
   ```

2. **Filter by specific categories**
   ```yaml
   servicenow:
     query:
       category: "Network"  # Focus on one category
   ```

3. **Use longer time range**
   ```bash
   python main.py --days 180
   ```

---

### Performance Issues

#### Issue: Processing is very slow

**Solutions:**

1. **Use smaller model**
   ```yaml
   categorization:
     embedding_model: all-MiniLM-L6-v2  # Fast
     # Instead of: all-mpnet-base-v2    # Slow
   ```

2. **Process fewer incidents**
   ```bash
   python main.py --limit 1000
   ```

3. **Reduce feature complexity**
   ```yaml
   categorization:
     features:
       - description
       - resolution_notes
       # Remove: symptoms, category, etc.
   ```

#### Issue: Out of memory

**Solution:**
Process in batches:
```bash
# Process first 500
python main.py --limit 500

# Then next 500 (modify date range)
python main.py --days 45 --limit 500
```

---

### Import Errors

#### Issue: `ModuleNotFoundError: No module named 'xxx'`

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or install specific package
pip install xxx
```

#### Issue: `ImportError: cannot import name 'xxx'`

**Solution:**
```bash
# Ensure you're in the project root
cd Incident_Analyser_SOP_Creator

# Run with proper Python path
python main.py
```

---

### Output Issues

#### Issue: "Permission denied" when writing files

**Solution:**
```bash
# Check directory permissions
# On Windows
icacls output
icacls data

# Create directories manually
mkdir output\sops
mkdir output\reports
mkdir data\incidents
```

#### Issue: Can't find generated SOPs

**Solution:**
Check the output directory:
```bash
# List SOPs
ls output/sops/
# or Windows
dir output\sops\

# Check logs for file paths
cat logs/app.log | grep "Generated SOP"
```

---

## Debug Mode

Enable debug logging for detailed information:

1. **Edit `.env`**
   ```env
   LOG_LEVEL=DEBUG
   ```

2. **Run the application**
   ```bash
   python main.py
   ```

3. **Check detailed logs**
   ```bash
   cat logs/app.log
   ```

---

## Getting Help

If you still have issues:

1. **Check logs**
   ```bash
   tail -f logs/app.log
   # or Windows
   Get-Content logs\app.log -Tail 50
   ```

2. **Verify configuration**
   ```bash
   cat config.yaml
   cat .env
   ```

3. **Test components individually**
   ```bash
   # Test ServiceNow connection
   python -c "from src.servicenow import create_client_from_env; create_client_from_env().test_connection()"
   
   # Test validation
   python examples/validation_example.py
   ```

4. **Collect diagnostics**
   ```bash
   # System info
   python --version
   pip list
   
   # Configuration
   cat config.yaml
   
   # Recent logs
   tail -100 logs/app.log
   ```

---

## Known Limitations

1. **Single-threaded**: Processing is sequential
   - Workaround: Process batches separately

2. **Memory usage**: Large datasets loaded into memory
   - Workaround: Use `--limit` flag

3. **No incremental updates**: Must reprocess all data
   - Workaround: Use date ranges to process recent data

4. **English only**: NLP models optimized for English
   - Workaround: Use multilingual models (slower)
