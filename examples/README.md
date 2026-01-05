# Examples

This directory contains example scripts demonstrating different features of the SOP Creator system.

## Available Examples

### 1. Basic Usage (`basic_usage.py`)

Demonstrates the simplest way to use the system - running the full pipeline.

```bash
python examples/basic_usage.py
```

**What it does:**
- Initializes the orchestrator
- Fetches incidents from ServiceNow
- Validates data quality
- Categorizes incidents
- Generates SOPs

### 2. Custom Categorization (`custom_categorization.py`)

Shows how to customize the categorization process with your own settings.

```bash
python examples/custom_categorization.py
```

**Features:**
- Custom clustering parameters
- Manual incident analysis
- Custom SOP generation settings

### 3. Data Validation (`validation_example.py`)

Demonstrates data quality checking and validation.

```bash
python examples/validation_example.py
```

**Features:**
- Data quality validation
- Error detection and reporting
- Quality metrics generation

## Running Examples

### Prerequisites

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment:
   ```bash
   copy .env.example .env
   # Edit .env with your credentials
   ```

### Run an Example

```bash
# From project root
python examples/basic_usage.py
```

## Customizing Examples

Feel free to modify these examples to suit your needs:

- Adjust clustering parameters
- Change validation rules
- Customize SOP templates
- Add custom processing logic

## Example Data

The examples use either:
- Real data from ServiceNow (basic_usage.py)
- Sample data embedded in the script (other examples)

You can modify the sample data to test different scenarios.

## Output

Examples generate output in:
- `output/sops/` - Generated SOPs
- `output/reports/` - Analysis reports
- Current directory - Example-specific output

## Troubleshooting

If you encounter import errors:
```bash
# Make sure you're in the project root
cd Incident_Analyser_SOP_Creator
python examples/basic_usage.py
```

If you get ServiceNow connection errors:
- Check your `.env` file
- Verify credentials
- Test connection manually
