# Project Index

Complete guide to navigating the Incident Analyzer & SOP Creator project.

## 📂 Project Structure

```
Incident_Analyser_SOP_Creator/
│
├── 📄 Main Application Files
│   ├── main.py                    # Main entry point
│   ├── setup.py                   # Setup verification script
│   ├── config.yaml                # Configuration file
│   ├── requirements.txt           # Python dependencies
│   └── .env.example              # Environment template
│
├── 📦 Source Code (src/)
│   ├── servicenow/               # ServiceNow integration
│   │   ├── __init__.py
│   │   └── client.py             # API client implementation
│   │
│   ├── data_validation/          # Data quality checking
│   │   ├── __init__.py
│   │   └── validator.py          # Validation logic
│   │
│   ├── categorization/           # ML-based clustering
│   │   ├── __init__.py
│   │   └── categorizer.py        # Categorization engine
│   │
│   └── sop_generation/           # SOP creation
│       ├── __init__.py
│       └── generator.py          # SOP generator
│
├── 📚 Documentation (docs/)
│   ├── QUICKSTART.md             # 5-minute quick start
│   ├── CONFIGURATION.md          # Configuration reference
│   ├── ARCHITECTURE.md           # System design
│   ├── API.md                    # API documentation
│   └── TROUBLESHOOTING.md        # Common issues
│
├── 💡 Examples (examples/)
│   ├── README.md                 # Examples guide
│   ├── basic_usage.py            # Full pipeline
│   ├── custom_categorization.py  # Custom ML
│   └── validation_example.py     # Data validation
│
├── 🧪 Tests (tests/)
│   └── test_validator.py         # Unit tests
│
├── 📋 Project Documentation
│   ├── README.md                 # Project overview
│   ├── GETTING_STARTED.md        # Beginner's guide
│   ├── PROJECT_SUMMARY.md        # Complete summary
│   ├── CHANGELOG.md              # Version history
│   ├── CONTRIBUTING.md           # Contribution guide
│   ├── LICENSE                   # MIT License
│   └── INDEX.md                  # This file
│
└── 📊 Generated Output (created at runtime)
    ├── data/                     # Intermediate data
    │   ├── incidents/           # Raw incident data
    │   ├── validated/           # Validated incidents
    │   └── clusters/            # Categorized groups
    │
    ├── output/                   # Final output
    │   ├── sops/               # Generated SOPs
    │   └── reports/            # Analysis reports
    │
    └── logs/                     # Application logs
        └── app.log
```

## 🎯 Quick Navigation

### 🚀 Getting Started

**New to the project?**
1. [README.md](README.md) - Project overview
2. [GETTING_STARTED.md](GETTING_STARTED.md) - Step-by-step setup
3. [docs/QUICKSTART.md](docs/QUICKSTART.md) - Fast setup (5 min)

**Installation:**
1. Install dependencies: `pip install -r requirements.txt`
2. Configure: `copy .env.example .env`
3. Verify: `python setup.py`
4. Run: `python main.py`

### 📖 Learning the System

**Understanding the architecture:**
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Complete overview
- [docs/API.md](docs/API.md) - API reference

**Configuration:**
- [docs/CONFIGURATION.md](docs/CONFIGURATION.md) - All settings
- [config.yaml](config.yaml) - Configuration file
- [.env.example](.env.example) - Environment template

### 💻 Using the System

**Basic usage:**
```bash
python main.py                    # Full pipeline
python main.py --days 30          # Last 30 days
python main.py --limit 500        # Limit incidents
```

**Examples:**
- [examples/basic_usage.py](examples/basic_usage.py) - Full pipeline
- [examples/custom_categorization.py](examples/custom_categorization.py) - Custom ML
- [examples/validation_example.py](examples/validation_example.py) - Data validation

### 🔧 Development

**Contributing:**
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [tests/](tests/) - Unit tests
- [CHANGELOG.md](CHANGELOG.md) - Version history

**Code structure:**
- [src/servicenow/](src/servicenow/) - ServiceNow integration
- [src/data_validation/](src/data_validation/) - Data validation
- [src/categorization/](src/categorization/) - ML categorization
- [src/sop_generation/](src/sop_generation/) - SOP generation

### 🆘 Troubleshooting

**Having issues?**
1. [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Common problems
2. `logs/app.log` - Application logs
3. `python setup.py` - Verify setup

## 📑 Document Types

### User Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| README.md | Project overview | Everyone |
| GETTING_STARTED.md | Step-by-step setup | New users |
| docs/QUICKSTART.md | Fast setup guide | Experienced users |
| docs/CONFIGURATION.md | Configuration reference | Users & admins |
| docs/TROUBLESHOOTING.md | Problem solving | All users |

### Technical Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| docs/ARCHITECTURE.md | System design | Developers |
| docs/API.md | API reference | Developers |
| PROJECT_SUMMARY.md | Complete overview | All stakeholders |
| CHANGELOG.md | Version history | Developers & users |
| CONTRIBUTING.md | Contribution guide | Contributors |

### Code Documentation

| Location | Content |
|----------|---------|
| src/ | Source code with docstrings |
| examples/ | Example implementations |
| tests/ | Unit tests |

## 🔍 Finding Information

### By Task

**Setting up the system:**
→ [GETTING_STARTED.md](GETTING_STARTED.md)

**Running the first time:**
→ [docs/QUICKSTART.md](docs/QUICKSTART.md)

**Configuring settings:**
→ [docs/CONFIGURATION.md](docs/CONFIGURATION.md)

**Understanding architecture:**
→ [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

**Solving problems:**
→ [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

**Contributing code:**
→ [CONTRIBUTING.md](CONTRIBUTING.md)

**Using the API:**
→ [docs/API.md](docs/API.md)

### By Role

**End Users:**
- README.md
- GETTING_STARTED.md
- docs/QUICKSTART.md
- docs/TROUBLESHOOTING.md

**System Administrators:**
- docs/CONFIGURATION.md
- config.yaml
- docs/TROUBLESHOOTING.md

**Developers:**
- docs/ARCHITECTURE.md
- docs/API.md
- CONTRIBUTING.md
- src/ (source code)

**Stakeholders:**
- PROJECT_SUMMARY.md
- README.md
- CHANGELOG.md

## 📊 Key Files Reference

### Configuration Files

| File | Purpose | Edit? |
|------|---------|-------|
| config.yaml | Application settings | Yes |
| .env | Credentials & secrets | Yes (create from .env.example) |
| .env.example | Environment template | No (copy to .env) |
| requirements.txt | Python dependencies | Only if adding packages |

### Entry Points

| File | Purpose | When to Use |
|------|---------|-------------|
| main.py | Main application | Production runs |
| setup.py | Setup verification | First-time setup |
| examples/*.py | Example scripts | Learning & testing |
| tests/*.py | Unit tests | Development & CI/CD |

### Source Modules

| Module | Responsibility |
|--------|---------------|
| servicenow.client | ServiceNow API communication |
| data_validation.validator | Data quality checking |
| categorization.categorizer | ML-based clustering |
| sop_generation.generator | SOP document creation |

## 🎓 Learning Path

### Beginner Path

1. Read [README.md](README.md)
2. Follow [GETTING_STARTED.md](GETTING_STARTED.md)
3. Run `python setup.py`
4. Try [examples/basic_usage.py](examples/basic_usage.py)
5. Review generated SOPs

### Intermediate Path

1. Study [docs/CONFIGURATION.md](docs/CONFIGURATION.md)
2. Customize config.yaml
3. Try different parameters
4. Run [examples/custom_categorization.py](examples/custom_categorization.py)
5. Review [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

### Advanced Path

1. Study [docs/API.md](docs/API.md)
2. Review source code in src/
3. Read [CONTRIBUTING.md](CONTRIBUTING.md)
4. Write custom scripts
5. Contribute improvements

## 🔗 External Resources

### Python Libraries

- [Sentence Transformers](https://www.sbert.net/) - Text embeddings
- [HDBSCAN](https://hdbscan.readthedocs.io/) - Clustering
- [scikit-learn](https://scikit-learn.org/) - ML utilities
- [pandas](https://pandas.pydata.org/) - Data processing

### ServiceNow

- [ServiceNow REST API](https://developer.servicenow.com/dev.do#!/reference/api/latest/rest/)
- [Table API](https://docs.servicenow.com/bundle/latest/page-integrate/reference/r_TableAPI-GET.html)

## 📝 Quick Reference

### Common Commands

```bash
# Setup
python setup.py

# Run full pipeline
python main.py

# Custom parameters
python main.py --days 30 --limit 500

# Examples
python examples/basic_usage.py
python examples/validation_example.py

# Tests
python -m pytest tests/
```

### Common Paths

- Configuration: `config.yaml`, `.env`
- Source code: `src/`
- Generated SOPs: `output/sops/`
- Reports: `output/reports/`
- Logs: `logs/app.log`

### Help Resources

- Quickstart: `docs/QUICKSTART.md`
- Troubleshooting: `docs/TROUBLESHOOTING.md`
- API docs: `docs/API.md`
- Examples: `examples/README.md`

---

**Need help finding something?** Use this index to navigate the project efficiently!
