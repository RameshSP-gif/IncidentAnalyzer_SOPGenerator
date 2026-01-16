"""
Simplified Flask app for Vercel deployment
Only includes MongoDB functionality without ML dependencies
"""
from flask import Flask, render_template, request, jsonify, send_file
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DB = os.getenv('MONGODB_DB', 'incident_analyzer')

# Initialize MongoDB if available
mongodb_client = None
try:
    from pymongo import MongoClient
    mongodb_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    mongodb_client.server_info()  # Test connection
    db = mongodb_client[MONGODB_DB]
    incidents_collection = db['incidents']
    logger.info("MongoDB connected successfully")
except Exception as e:
    logger.warning(f"MongoDB connection failed: {e}")
    db = None
    incidents_collection = None

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/manage')
def manage():
    """Management page"""
    return render_template('manage.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'mongodb': 'connected' if mongodb_client else 'disconnected'
    }
    return jsonify(status)

@app.route('/api/incidents', methods=['GET'])
def get_incidents():
    """Get all incidents from MongoDB"""
    try:
        if not incidents_collection:
            return jsonify({'error': 'MongoDB not connected'}), 503
        
        incidents = list(incidents_collection.find({}, {'_id': 0}).limit(100))
        return jsonify({'incidents': incidents, 'count': len(incidents)})
    except Exception as e:
        logger.error(f"Error fetching incidents: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/incidents/count')
def get_incident_count():
    """Get incident count"""
    try:
        if not incidents_collection:
            return jsonify({'error': 'MongoDB not connected'}), 503
        
        count = incidents_collection.count_documents({})
        return jsonify({'count': count})
    except Exception as e:
        logger.error(f"Error counting incidents: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_incident():
    """Placeholder for incident analysis - requires full ML setup"""
    return jsonify({
        'error': 'Analysis features require full deployment with ML dependencies',
        'message': 'Please use the full application with all dependencies for analysis features'
    }), 501

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
