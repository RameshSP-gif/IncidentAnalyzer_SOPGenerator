"""
Vercel serverless function handler for Flask app
Routes all requests to the Flask application
"""
import sys
from pathlib import Path

# Add project root and src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Import the Flask app
from web_app import app

# Export the app for Vercel
app = app
