"""
Vercel serverless function handler for Flask app
Uses simplified version without heavy ML dependencies
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the simplified Flask app for Vercel
from api.web_app_vercel import app

# Export the app for Vercel
app = app
