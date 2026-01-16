"""
Vercel serverless function handler for Flask app
Routes all requests to the Flask application
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import the Flask app
from web_app import app

# Export the app for Vercel
handler = app
