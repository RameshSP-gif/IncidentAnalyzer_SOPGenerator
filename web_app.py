"""
Flask Web Application for SOP Generation
Professional UI for incident analysis and SOP creation
"""

from flask import Flask, render_template, request, jsonify
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_validation import DataValidator
from sop_generation import SOPGenerator

app = Flask(__name__)

# Initialize components (without ML categorizer for faster startup)
validator = DataValidator(
    required_fields=["number", "short_description"],  # Resolution now optional with RAG
    min_description_length=20,
    min_resolution_length=30
)

generator = SOPGenerator(
    min_incidents=1,  # Allow single incident for demo
    template_format="markdown"
)

# Lazy load categorizer and RAG resolver
categorizer = None
resolution_finder = None

def get_categorizer():
    """Lazy load the ML categorizer"""
    global categorizer
    if categorizer is None:
        print("[INFO] Loading ML categorizer (first time only)...")
        from categorization import IncidentCategorizer
        categorizer = IncidentCategorizer(
            embedding_model="all-MiniLM-L6-v2",
            min_cluster_size=2,
            min_samples=1
        )
        print("[INFO] ML categorizer loaded successfully!")
    return categorizer

def get_resolution_finder():
    """Lazy load the RAG resolution finder"""
    global resolution_finder
    if resolution_finder is None:
        print("[INFO] Loading RAG resolution finder (first time only)...")
        from rag import ResolutionFinder
        resolution_finder = ResolutionFinder(embedding_model="all-MiniLM-L6-v2")
        
        # Load past incidents into knowledge base
        if incidents_db:
            resolution_finder.load_knowledge_base(incidents_db)
        
        # Try loading from saved knowledge base
        kb_file = Path(__file__).parent / "data" / "knowledge_base.json"
        if kb_file.exists():
            resolution_finder.load_from_file(str(kb_file))
        
        print("[INFO] RAG resolution finder loaded successfully!")
    return resolution_finder

# Store incidents in memory (use database in production)
incidents_db = []


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/manage')
def manage():
    """Knowledge base management page"""
    return render_template('manage.html')


@app.route('/add_incident', methods=['POST'])
def add_incident():
    """Add a new incident"""
    try:
        data = request.json
        
        # Create incident object
        incident = {
            "number": data.get('incident_number', f"INC{len(incidents_db):04d}"),
            "short_description": data.get('short_description', ''),
            "description": data.get('description', ''),
            "category": data.get('category', 'General'),
            "subcategory": data.get('subcategory', ''),
            "priority": data.get('priority', '3'),
            "resolution_notes": data.get('resolution_notes', ''),
            "sys_created_on": datetime.now().isoformat(),
            "resolved_at": datetime.now().isoformat()
        }
        
        # Validate incident
        validation_result = validator.validate_incident(incident)
        
        if not validation_result['is_valid']:
            return jsonify({
                'success': False,
                'errors': validation_result['errors']
            }), 400
        
        # Add to database
        incidents_db.append(incident)
        
        # Also add to knowledge base if resolution is provided
        if incident.get('resolution_notes'):
            try:
                finder = get_resolution_finder()
                finder.add_to_knowledge_base(incident)
                print(f"[INFO] Incident {incident['number']} added to knowledge base")
            except Exception as kb_error:
                print(f"[WARNING] Failed to add to knowledge base: {str(kb_error)}")
                # Don't fail the request if knowledge base update fails
        
        return jsonify({
            'success': True,
            'incident_number': incident['number'],
            'message': f"Incident {incident['number']} added successfully"
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/generate_sop', methods=['POST'])
def generate_sop():
    """Generate SOP from stored incidents"""
    try:
        if not incidents_db:
            return jsonify({
                'success': False,
                'error': 'No incidents available. Please add incidents first.'
            }), 400
        
        # Load categorizer lazily
        cat = get_categorizer()
        
        # Categorize incidents
        clusters = cat.categorize_incidents(incidents_db)
        
        if not clusters:
            return jsonify({
                'success': False,
                'error': 'Could not categorize incidents. Try adding more similar incidents.'
            }), 400
        
        # Generate SOPs for all clusters
        sops = []
        for cluster_id, cluster_incidents in clusters.items():
            analysis = cat.analyze_cluster(cluster_id, cluster_incidents)
            sop_content = generator.generate_sop(cluster_id, cluster_incidents, analysis)
            
            if sop_content:
                sops.append({
                    'cluster_id': cluster_id,
                    'category': list(analysis['common_categories'].keys())[0] if analysis['common_categories'] else 'General',
                    'incident_count': len(cluster_incidents),
                    'content': sop_content,
                    'analysis': analysis
                })
        
        return jsonify({
            'success': True,
            'total_incidents': len(incidents_db),
            'clusters': len(clusters),
            'sops': sops
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/get_incidents', methods=['GET'])
def get_incidents():
    """Get all stored incidents"""
    return jsonify({
        'success': True,
        'incidents': incidents_db,
        'count': len(incidents_db)
    })


@app.route('/clear_incidents', methods=['POST'])
def clear_incidents():
    """Clear all incidents"""
    incidents_db.clear()
    return jsonify({
        'success': True,
        'message': 'All incidents cleared'
    })


@app.route('/analyze_single', methods=['POST'])
def analyze_single():
    """Analyze a single incident and provide immediate SOP"""
    try:
        data = request.json
        print(f"\n[DEBUG] Received data: {data}")
        
        # Create incident object
        incident = {
            "number": data.get('incident_number', f"INC{datetime.now().strftime('%Y%m%d%H%M%S')}"),
            "short_description": data.get('short_description', ''),
            "description": data.get('description', ''),
            "category": data.get('category', 'General'),
            "resolution_notes": data.get('resolution_notes', ''),
            "priority": data.get('priority', '3'),
            "sys_created_on": datetime.now().isoformat(),
            "resolved_at": datetime.now().isoformat()
        }
        
        print(f"[DEBUG] Created incident: {incident['number']}")
        
        # Validate only required fields (resolution now optional)
        validation_result = validator.validate_incident(incident)
        print(f"[DEBUG] Validation result: {validation_result}")
        
        # Filter out resolution-related errors if resolution is empty (it's optional now)
        if not validation_result['is_valid']:
            errors = []
            for e in validation_result.get('errors', []):
                # Skip resolution-related errors if resolution field is empty (optional)
                if isinstance(e, dict):
                    fields = e.get('fields', [])
                    if 'resolution_notes' in fields and not incident.get('resolution_notes'):
                        continue  # Skip this error since resolution is optional
                errors.append(e)
            
            if errors:
                return jsonify({
                    'success': False,
                    'errors': errors
                }), 400
        
        # Create simple SOP for single incident
        analysis = {
            'cluster_id': 0,
            'incident_count': 1,
            'common_categories': {incident['category']: 1},
            'common_patterns': [],
            'representative_incident': incident['number'],
            'priority_distribution': {incident['priority']: 1},
            'avg_resolution_time': 0
        }
        
        print(f"[DEBUG] Generating SOP...")
        
        # If no resolution provided, add a placeholder
        if not incident.get('resolution_notes') or len(incident.get('resolution_notes', '')) < 10:
            incident['resolution_notes'] = "Resolution pending. Use 'AI Suggest Resolution' feature or enter resolution manually for complete SOP."
        
        sop_content = generator.generate_sop(0, [incident], analysis)
        print(f"[DEBUG] SOP generated, length: {len(sop_content) if sop_content else 0}")
        
        return jsonify({
            'success': True,
            'incident': incident,
            'sop': sop_content
        })
        
    except Exception as e:
        print(f"[ERROR] Exception in analyze_single: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/suggest_resolution', methods=['POST'])
def suggest_resolution():
    """Suggest resolution using RAG from past incidents"""
    try:
        data = request.json
        print(f"\n[DEBUG] Resolution suggestion requested")
        
        problem_description = data.get('description', '')
        short_description = data.get('short_description', '')
        category = data.get('category', '')
        
        if not problem_description and not short_description:
            return jsonify({
                'success': False,
                'error': 'Please provide problem description'
            }), 400
        
        # Load RAG finder
        finder = get_resolution_finder()
        
        # Combine descriptions
        full_description = f"{short_description}. {problem_description}"
        
        # Find similar incidents and suggest resolution
        suggestion = finder.suggest_resolution(
            problem_description=full_description,
            category=category if category else None
        )
        
        print(f"[DEBUG] Resolution suggestion: {suggestion['success']}")
        
        if suggestion['success']:
            return jsonify({
                'success': True,
                'suggested_resolution': suggestion['suggested_resolution'],
                'confidence': suggestion.get('confidence', 0),
                'primary_source': suggestion.get('primary_source', {}),
                'alternatives': suggestion.get('alternative_resolutions', [])
            })
        else:
            return jsonify({
                'success': False,
                'message': suggestion.get('message', 'No similar incidents found'),
                'suggested_resolution': 'No resolution suggestions available. Please enter resolution manually or add more historical data to knowledge base.'
            })
        
    except Exception as e:
        print(f"[ERROR] Exception in suggest_resolution: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'suggested_resolution': 'Error finding resolution. Please enter manually.'
        }), 500


@app.route('/add_to_knowledge_base', methods=['POST'])
def add_to_knowledge_base():
    """Add resolved incident to RAG knowledge base"""
    try:
        data = request.json
        incident = data.get('incident', {})
        
        if not incident.get('resolution_notes'):
            return jsonify({
                'success': False,
                'error': 'Resolution required to add to knowledge base'
            }), 400
        
        # Load finder and add incident
        finder = get_resolution_finder()
        finder.add_to_knowledge_base(incident)
        
        return jsonify({
            'success': True,
            'message': f"Incident {incident.get('number', 'Unknown')} added to knowledge base"
        })
        
    except Exception as e:
        print(f"[ERROR] Exception in add_to_knowledge_base: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/get_knowledge_base', methods=['GET'])
def get_knowledge_base():
    """Get all incidents from knowledge base"""
    try:
        kb_file = Path(__file__).parent / 'data' / 'knowledge_base.json'
        
        if kb_file.exists():
            import json
            with open(kb_file, 'r', encoding='utf-8') as f:
                kb_data = json.load(f)
            
            return jsonify({
                'success': True,
                'incidents': kb_data,
                'count': len(kb_data)
            })
        else:
            return jsonify({
                'success': True,
                'incidents': [],
                'count': 0
            })
            
    except Exception as e:
        print(f"[ERROR] Exception in get_knowledge_base: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/update_incident/<incident_number>', methods=['PUT'])
def update_incident(incident_number):
    """Update an existing incident in knowledge base"""
    try:
        data = request.json
        kb_file = Path(__file__).parent / 'data' / 'knowledge_base.json'
        
        if not kb_file.exists():
            return jsonify({
                'success': False,
                'error': 'Knowledge base file not found'
            }), 404
        
        import json
        with open(kb_file, 'r', encoding='utf-8') as f:
            kb_data = json.load(f)
        
        # Find and update incident
        incident_found = False
        for i, incident in enumerate(kb_data):
            if incident.get('number') == incident_number:
                # Update fields
                kb_data[i].update({
                    'short_description': data.get('short_description', incident.get('short_description')),
                    'description': data.get('description', incident.get('description')),
                    'category': data.get('category', incident.get('category')),
                    'priority': data.get('priority', incident.get('priority')),
                    'resolution_notes': data.get('resolution_notes', incident.get('resolution_notes')),
                    'updated_at': datetime.now().isoformat()
                })
                incident_found = True
                break
        
        if not incident_found:
            return jsonify({
                'success': False,
                'error': f'Incident {incident_number} not found'
            }), 404
        
        # Save back to file
        with open(kb_file, 'w', encoding='utf-8') as f:
            json.dump(kb_data, f, indent=2, ensure_ascii=False)
        
        # Reload RAG system
        global resolution_finder
        resolution_finder = None
        
        return jsonify({
            'success': True,
            'message': f'Incident {incident_number} updated successfully'
        })
        
    except Exception as e:
        print(f"[ERROR] Exception in update_incident: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/delete_incident/<incident_number>', methods=['DELETE'])
def delete_incident(incident_number):
    """Delete an incident from knowledge base"""
    try:
        kb_file = Path(__file__).parent / 'data' / 'knowledge_base.json'
        
        if not kb_file.exists():
            return jsonify({
                'success': False,
                'error': 'Knowledge base file not found'
            }), 404
        
        import json
        with open(kb_file, 'r', encoding='utf-8') as f:
            kb_data = json.load(f)
        
        # Find and remove incident
        original_count = len(kb_data)
        kb_data = [inc for inc in kb_data if inc.get('number') != incident_number]
        
        if len(kb_data) == original_count:
            return jsonify({
                'success': False,
                'error': f'Incident {incident_number} not found'
            }), 404
        
        # Save back to file
        with open(kb_file, 'w', encoding='utf-8') as f:
            json.dump(kb_data, f, indent=2, ensure_ascii=False)
        
        # Reload RAG system
        global resolution_finder
        resolution_finder = None
        
        return jsonify({
            'success': True,
            'message': f'Incident {incident_number} deleted successfully'
        })
        
    except Exception as e:
        print(f"[ERROR] Exception in delete_incident: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/search_incidents', methods=['POST'])
def search_incidents():
    """Search incidents in knowledge base"""
    try:
        data = request.json
        search_query = data.get('query', '').lower()
        category_filter = data.get('category', '')
        
        kb_file = Path(__file__).parent / 'data' / 'knowledge_base.json'
        
        if not kb_file.exists():
            return jsonify({
                'success': True,
                'incidents': [],
                'count': 0
            })
        
        import json
        with open(kb_file, 'r', encoding='utf-8') as f:
            kb_data = json.load(f)
        
        # Filter incidents
        filtered = kb_data
        
        if category_filter:
            filtered = [inc for inc in filtered if inc.get('category') == category_filter]
        
        if search_query:
            filtered = [
                inc for inc in filtered
                if search_query in inc.get('short_description', '').lower() or
                   search_query in inc.get('description', '').lower() or
                   search_query in inc.get('number', '').lower()
            ]
        
        return jsonify({
            'success': True,
            'incidents': filtered,
            'count': len(filtered)
        })
        
    except Exception as e:
        print(f"[ERROR] Exception in search_incidents: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("\n" + "="*70)
    print("SOP Generator Web Application Starting...")
    print("="*70)
    print("\nAccess the application at: http://127.0.0.1:5000")
    print("\nPress CTRL+C to stop the server")
    print("="*70 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
