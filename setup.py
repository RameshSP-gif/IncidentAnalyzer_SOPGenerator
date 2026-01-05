"""
Setup script for Incident Analyzer & SOP Creator
Run this to verify installation and setup
"""

import sys
import os
from pathlib import Path


def check_python_version():
    """Check if Python version is adequate"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor} detected")
        print("    Required: Python 3.8 or higher")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    print("\nChecking dependencies...")
    
    required = [
        'requests',
        'pandas',
        'numpy',
        'sklearn',
        'sentence_transformers',
        'yaml',
        'dotenv',
        'loguru',
        'jinja2',
        'tqdm'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package}")
            missing.append(package)
    
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True


def check_directories():
    """Check and create necessary directories"""
    print("\nChecking directories...")
    
    directories = [
        "data/incidents",
        "data/validated",
        "data/clusters",
        "output/sops",
        "output/reports",
        "logs"
    ]
    
    for directory in directories:
        path = Path(directory)
        if path.exists():
            print(f"  ✓ {directory}")
        else:
            path.mkdir(parents=True, exist_ok=True)
            print(f"  + Created {directory}")
    
    return True


def check_env_file():
    """Check if .env file exists"""
    print("\nChecking environment configuration...")
    
    if Path(".env").exists():
        print("  ✓ .env file exists")
        
        # Check if it has required variables
        with open(".env", 'r') as f:
            content = f.read()
            
        required_vars = [
            'SERVICENOW_INSTANCE',
            'SERVICENOW_USERNAME',
            'SERVICENOW_PASSWORD'
        ]
        
        missing_vars = []
        for var in required_vars:
            if var not in content or f"{var}=your-" in content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"  ⚠ .env file needs configuration:")
            for var in missing_vars:
                print(f"    - {var}")
            return False
        else:
            print("  ✓ Environment variables configured")
            return True
    else:
        print("  ✗ .env file not found")
        print("    Copy .env.example to .env and configure it")
        
        if Path(".env.example").exists():
            print("    Run: copy .env.example .env")
        
        return False


def check_config_file():
    """Check if config.yaml exists"""
    print("\nChecking configuration file...")
    
    if Path("config.yaml").exists():
        print("  ✓ config.yaml exists")
        return True
    else:
        print("  ✗ config.yaml not found")
        return False


def download_models():
    """Download required ML models"""
    print("\nDownloading ML models...")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        print("  Downloading all-MiniLM-L6-v2 model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("  ✓ Model downloaded successfully")
        return True
    except Exception as e:
        print(f"  ✗ Failed to download model: {e}")
        return False


def test_servicenow_connection():
    """Test connection to ServiceNow"""
    print("\nTesting ServiceNow connection...")
    
    if not Path(".env").exists():
        print("  ⚠ Skipping (no .env file)")
        return True
    
    try:
        from dotenv import load_dotenv
        from src.servicenow import create_client_from_env
        
        load_dotenv()
        
        # Check if credentials are configured
        instance = os.getenv("SERVICENOW_INSTANCE")
        username = os.getenv("SERVICENOW_USERNAME")
        password = os.getenv("SERVICENOW_PASSWORD")
        
        if not instance or "your-" in instance:
            print("  ⚠ Skipping (credentials not configured)")
            return True
        
        client = create_client_from_env()
        
        if client.test_connection():
            print("  ✓ Successfully connected to ServiceNow")
            return True
        else:
            print("  ✗ Failed to connect to ServiceNow")
            print("    Check your credentials in .env")
            return False
            
    except Exception as e:
        print(f"  ✗ Connection test failed: {e}")
        return False


def main():
    """Run all setup checks"""
    print("="*60)
    print("Incident Analyzer & SOP Creator - Setup Check")
    print("="*60)
    
    results = []
    
    # Run checks
    results.append(("Python Version", check_python_version()))
    results.append(("Dependencies", check_dependencies()))
    results.append(("Directories", check_directories()))
    results.append(("Config File", check_config_file()))
    results.append(("Environment File", check_env_file()))
    
    # Optional checks
    if results[1][1]:  # If dependencies are installed
        results.append(("ML Models", download_models()))
        results.append(("ServiceNow Connection", test_servicenow_connection()))
    
    # Summary
    print("\n" + "="*60)
    print("Setup Summary")
    print("="*60)
    
    for name, passed in results:
        status = "✓" if passed else "✗"
        print(f"{status} {name}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n✓ Setup complete! You're ready to run the system.")
        print("\nNext steps:")
        print("  1. Review config.yaml if needed")
        print("  2. Run: python main.py")
    else:
        print("\n✗ Setup incomplete. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Create .env file: copy .env.example .env")
        print("  - Configure ServiceNow credentials in .env")
    
    print("\nFor help, see docs/QUICKSTART.md")
    print("="*60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
