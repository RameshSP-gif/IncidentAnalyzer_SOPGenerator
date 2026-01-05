# Contributing to Incident Analyzer & SOP Creator

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🤝 How to Contribute

### Reporting Bugs

1. **Check existing issues** to avoid duplicates
2. **Use the bug report template** when creating new issues
3. **Include**:
   - Python version
   - OS and version
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages/logs
   - Configuration (sanitized)

### Suggesting Features

1. **Check existing feature requests** first
2. **Describe the use case** clearly
3. **Explain the benefits** to users
4. **Consider alternatives** you've explored

### Submitting Changes

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Test thoroughly**
5. **Commit with clear messages**
6. **Push and create a Pull Request**

## 💻 Development Setup

### Prerequisites
- Python 3.8+
- Git
- ServiceNow test instance (optional)

### Setup Development Environment

```bash
# Clone your fork
git clone https://github.com/your-username/Incident_Analyser_SOP_Creator.git
cd Incident_Analyser_SOP_Creator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8 mypy

# Run tests
python -m pytest tests/

# Run setup verification
python setup.py
```

## 📝 Code Style

### Python Style Guide

Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with these additions:

1. **Formatting**
   - Line length: 100 characters max
   - Use 4 spaces for indentation
   - Use double quotes for strings

2. **Naming Conventions**
   - Classes: `PascalCase`
   - Functions/Variables: `snake_case`
   - Constants: `UPPER_SNAKE_CASE`
   - Private members: `_leading_underscore`

3. **Type Hints**
   ```python
   def function_name(param: str, count: int = 5) -> List[str]:
       """Function docstring"""
       pass
   ```

4. **Docstrings**
   ```python
   def process_data(incidents: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
       """
       Process and validate incident data.
       
       Args:
           incidents: List of incident dictionaries
           
       Returns:
           Tuple of (valid_incidents, invalid_incidents)
       """
   ```

### Code Formatting

Use `black` for automatic formatting:
```bash
black src/ main.py examples/
```

### Linting

Run before committing:
```bash
# Linting
flake8 src/ main.py

# Type checking
mypy src/ main.py
```

## 🧪 Testing

### Running Tests

```bash
# All tests
python -m pytest tests/

# Specific test file
python -m pytest tests/test_validator.py

# With coverage
python -m pytest --cov=src tests/
```

### Writing Tests

1. **Place tests in `tests/` directory**
2. **Name test files** `test_*.py`
3. **Name test functions** `test_*`
4. **Use descriptive test names**

Example:
```python
def test_validator_detects_missing_required_fields():
    """Test that validator identifies missing required fields"""
    validator = DataValidator(required_fields=["number", "description"])
    incident = {"number": "INC001"}  # Missing description
    
    result = validator.validate_incident(incident)
    
    assert not result["is_valid"]
    assert any(e["type"] == "missing_fields" for e in result["errors"])
```

## 📚 Documentation

### Code Documentation

- Add docstrings to all classes and public methods
- Include type hints
- Document parameters and return values
- Add examples where helpful

### User Documentation

When adding features, update:
- `README.md` - If it affects usage
- `docs/API.md` - For API changes
- `docs/CONFIGURATION.md` - For new config options
- `CHANGELOG.md` - For all changes

## 🔄 Pull Request Process

1. **Update documentation** for any user-facing changes
2. **Add tests** for new functionality
3. **Ensure all tests pass**
4. **Update CHANGELOG.md**
5. **Write clear PR description**:
   - What changed?
   - Why was it changed?
   - How was it tested?
   - Any breaking changes?

### PR Title Format

```
[Type] Brief description

Types:
- [Feature] - New functionality
- [Fix] - Bug fixes
- [Docs] - Documentation only
- [Refactor] - Code restructuring
- [Test] - Test additions/changes
- [Chore] - Maintenance tasks
```

### PR Description Template

```markdown
## Description
Brief description of changes

## Motivation
Why is this change needed?

## Changes
- Change 1
- Change 2

## Testing
How was this tested?

## Breaking Changes
List any breaking changes or "None"

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Code follows style guide
- [ ] All tests passing
```

## 🎯 Areas for Contribution

### High Priority

1. **Performance Improvements**
   - Parallel processing
   - Caching mechanisms
   - Memory optimization

2. **Output Formats**
   - HTML generation
   - PDF export
   - Custom templates

3. **Integration**
   - ServiceNow KB publishing
   - REST API
   - Webhook support

### Good First Issues

Look for issues labeled `good-first-issue`:
- Documentation improvements
- Example scripts
- Configuration enhancements
- Error message improvements

### Advanced Contributions

1. **ML Improvements**
   - Alternative clustering algorithms
   - Better feature extraction
   - Model fine-tuning

2. **Architecture**
   - Database backend
   - Distributed processing
   - Microservices architecture

## 🚫 What NOT to Contribute

- Breaking changes without discussion
- Features without use cases
- Poorly tested code
- Undocumented changes
- Code style violations

## 📞 Communication

- **Issues**: For bugs and features
- **Discussions**: For questions and ideas
- **Pull Requests**: For code contributions

## 🏆 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Credited in release notes
- Thanked in the community

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## ❓ Questions?

- Check existing documentation
- Review example code
- Search closed issues
- Ask in discussions

---

Thank you for contributing to make this project better! 🎉
