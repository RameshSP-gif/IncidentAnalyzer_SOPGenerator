"""
Flask Web Application for SOP Generation
Professional UI for incident analysis and SOP creation with MongoDB integration
"""

from flask import Flask, render_template, request, jsonify, send_file
import sys
from pathlib import Path
from datetime import datetime
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_validation import DataValidator
from sop_generation import SOPGenerator
from database import get_db_client

app = Flask(__name__)

# Initialize MongoDB client
db_client = get_db_client()

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

# Cache for incidents (load once, reuse many times)
incidents_cache = {
    'data': None,
    'last_loaded': None,
    'count': 0
}

def get_incidents_cache():
    """Get cached incidents or load from database"""
    global incidents_cache
    
    # If cache is empty, load all incidents
    if incidents_cache['data'] is None:
        print("[INFO] Loading all incidents into cache (first time)...")
        incidents_cache['data'] = db_client.get_all_incidents(limit=10000)  # Large number to get all
        incidents_cache['count'] = len(incidents_cache['data'])
        incidents_cache['last_loaded'] = datetime.now()
        print(f"[INFO] Cached {incidents_cache['count']} incidents")
    
    return incidents_cache['data']

def refresh_incidents_cache():
    """Refresh the incidents cache (call after adding/updating incidents)"""
    global incidents_cache
    print("[INFO] Refreshing incidents cache...")
    incidents_cache['data'] = db_client.get_all_incidents(limit=10000)  # Large number to get all
    incidents_cache['count'] = len(incidents_cache['data'])
    incidents_cache['last_loaded'] = datetime.now()
    print(f"[INFO] Cache refreshed with {incidents_cache['count']} incidents")

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
        try:
            print("[INFO] Loading RAG resolution finder (first time only)...")
            
            from rag import ResolutionFinder
            
            # Initialize with in-memory storage (disable ChromaDB for web app)
            resolution_finder = ResolutionFinder(
                embedding_model="all-MiniLM-L6-v2",
                use_chromadb=False  # Disable ChromaDB to avoid loading issues
            )
            
            # Check if ChromaDB is empty - if so, load from MongoDB
            # Disabled for now as we're using in-memory
            # Fallback to in-memory: Load from MongoDB
            print("[INFO] Using in-memory storage. Loading from MongoDB...")
            incidents_from_db = db_client.get_all_incidents(limit=1000)  # Limit to 1000 for faster loading
            if incidents_from_db:
                resolution_finder.load_knowledge_base(incidents_from_db)
                print(f"[INFO] Loaded {len(incidents_from_db)} incidents into memory")
            
            # Try loading from saved knowledge base (legacy support)
            kb_file = Path(__file__).parent / "data" / "knowledge_base.json"
            if kb_file.exists():
                try:
                    resolution_finder.load_from_file(str(kb_file))
                    print(f"[INFO] Loaded knowledge base from {kb_file}")
                except Exception as e:
                    print(f"[WARNING] Could not load knowledge base file: {e}")
            
            print("[INFO] RAG resolution finder loaded successfully!")
        except Exception as e:
            print(f"[ERROR] Failed to load RAG resolution finder: {e}")
            import traceback
            traceback.print_exc()
            # Return None to handle gracefully
            return None
    return resolution_finder


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/manage')
def manage():
    """Unified MongoDB and Knowledge Base management interface"""
    return render_template('mongodb_manager_fixed.html')


@app.route('/mongodb')
def mongodb_manager():
    """MongoDB incident manager page - unified interface"""
    return render_template('mongodb_manager_fixed.html')


@app.route('/add_incident', methods=['POST'])
def add_incident():
    """Add a new incident"""
    try:
        data = request.json
        
        # Generate incident number if not provided
        incident_count = db_client.get_incident_count()
        
        # Create incident object
        incident = {
            "number": data.get('incident_number', f"INC{incident_count:04d}"),
            "short_description": data.get('short_description', ''),
            "description": data.get('description', ''),
            "category": data.get('category', 'General'),
            "subcategory": data.get('subcategory', ''),
            "priority": data.get('priority', '3'),
            "state": data.get('state', 'Closed'),
            "resolution_notes": data.get('resolution_notes', ''),
            "close_notes": data.get('close_notes', ''),
            "work_notes": data.get('work_notes', ''),
            "assignment_group": data.get('assignment_group', ''),
            "assigned_to": data.get('assigned_to', ''),
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
        
        # Add to MongoDB
        doc_id = db_client.insert_incident(incident)
        
        if not doc_id:
            return jsonify({
                'success': False,
                'error': 'Failed to insert incident (duplicate number?)'
            }), 400
        
        # Refresh cache after adding new incident
        refresh_incidents_cache()
        
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
            'document_id': doc_id,
            'message': f"Incident {incident['number']} added successfully to MongoDB"
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/generate_sop', methods=['POST'])
def generate_sop():
    """Generate SOP from stored incidents in MongoDB"""
    try:
        # Get incidents from MongoDB
        incidents_from_db = db_client.get_all_incidents(limit=5000)
        
        if not incidents_from_db:
            return jsonify({
                'success': False,
                'error': 'No incidents available in MongoDB. Please add incidents first.'
            }), 400
        
        # Load categorizer lazily
        cat = get_categorizer()
        
        # Categorize incidents
        clusters = cat.categorize_incidents(incidents_from_db)
        
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
            'total_incidents': len(incidents_from_db),
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
    """Get all stored incidents from MongoDB"""
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 100))
        skip = (page - 1) * per_page
        
        # Get incidents from MongoDB
        incidents = db_client.get_all_incidents(skip=skip, limit=per_page)
        total_count = db_client.get_incident_count()
        
        return jsonify({
            'success': True,
            'incidents': incidents,
            'count': len(incidents),
            'total': total_count,
            'page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/update_incident/<incident_number>', methods=['PUT'])
def update_incident_by_number(incident_number):
    """Update an existing incident in MongoDB"""
    try:
        data = request.json
        
        # Remove fields that shouldn't be updated
        update_data = {k: v for k, v in data.items() if k != 'number'}
        
        # Update in MongoDB
        success = db_client.update_incident(incident_number, update_data)
        
        if success:
            # Refresh cache after update
            refresh_incidents_cache()
            return jsonify({
                'success': True,
                'message': f'Incident {incident_number} updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Incident {incident_number} not found or no changes made'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/delete_incident/<incident_number>', methods=['DELETE'])
def delete_incident_by_number(incident_number):
    """Delete an incident from MongoDB"""
    try:
        success = db_client.delete_incident(incident_number)
        
        if success:
            # Refresh cache after delete
            refresh_incidents_cache()
            return jsonify({
                'success': True,
                'message': f'Incident {incident_number} deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Incident {incident_number} not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/search_incidents', methods=['POST'])
def search_incidents():
    """Search incidents in MongoDB"""
    try:
        data = request.json
        query = data.get('query', '')
        category = data.get('category')
        priority = data.get('priority')
        
        incidents = db_client.search_incidents(
            query=query if query else None,
            category=category,
            priority=priority,
            limit=200
        )
        
        return jsonify({
            'success': True,
            'incidents': incidents,
            'count': len(incidents)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/import_csv', methods=['POST'])
def import_csv():
    """Import incidents from CSV file"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Save temporarily
        temp_path = Path('temp_import.csv')
        file.save(str(temp_path))
        
        # Import from CSV
        result = db_client.import_from_csv(str(temp_path))
        
        # Clean up
        temp_path.unlink()
        
        # Refresh cache after importing incidents
        if result.get('imported', 0) > 0:
            refresh_incidents_cache()
            print(f"[INFO] Cache refreshed after importing {result['imported']} incidents")
        
        # If import was successful, update RAG knowledge base
        if result.get('imported', 0) > 0:
            try:
                print(f"[INFO] Syncing {result['imported']} new incidents to RAG knowledge base...")
                finder = get_resolution_finder()
                incidents_from_db = get_incidents_cache()  # Use cache instead of re-querying DB
                if incidents_from_db:
                    finder.load_knowledge_base(incidents_from_db)
                    print(f"[INFO] RAG knowledge base updated with {len(incidents_from_db)} total incidents")
                    result['rag_synced'] = True
                    result['rag_total'] = len(incidents_from_db)
            except Exception as e:
                print(f"[WARNING] Failed to sync to RAG: {e}")
                result['rag_synced'] = False
                result['rag_error'] = str(e)
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/export_csv', methods=['GET'])
def export_csv():
    """Export all incidents to CSV"""
    try:
        import csv
        from io import StringIO
        
        incidents = db_client.get_all_incidents(limit=10000)
        
        if not incidents:
            return jsonify({
                'success': False,
                'error': 'No incidents to export'
            }), 400
        
        # Create CSV in memory
        output = StringIO()
        fieldnames = ['number', 'short_description', 'description', 'category', 
                     'subcategory', 'priority', 'state', 'resolution_notes', 
                     'close_notes', 'assignment_group', 'assigned_to',
                     'sys_created_on', 'sys_updated_on', 'resolved_at']
        
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(incidents)
        
        # Send file
        from io import BytesIO
        csv_data = output.getvalue().encode('utf-8')
        
        return send_file(
            BytesIO(csv_data),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'incidents_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/get_stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    try:
        total_count = db_client.get_incident_count()
        categories = db_client.get_categories()
        
        # Get recent incidents
        recent = db_client.get_all_incidents(limit=10)
        
        return jsonify({
            'success': True,
            'total_incidents': total_count,
            'categories': categories,
            'category_count': len(categories),
            'recent_incidents': recent[:5]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/analyze_single', methods=['POST'])
def analyze_single():
    """Analyze a single incident and provide immediate SOP"""
    try:
        data = request.json
        print(f"\n[DEBUG] Received data: {data}")
        
        # Map "Other" category to "General" for compatibility
        category = data.get('category', 'General')
        if category == 'Other':
            category = 'General'
        
        # Create incident object
        # Map "Other" category to "General" before validation
        category = data.get('category', 'General')
        if category and category.lower() == 'other':
            category = 'General'
        
        incident = {
            "number": data.get('incident_number', f"INC{datetime.now().strftime('%Y%m%d%H%M%S')}"),
            "short_description": data.get('short_description', ''),
            "description": data.get('description', ''),
            "category": category,
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
    """Suggest resolution from similar past incidents in MongoDB"""
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
        
        # Get incidents from cache (loaded once at startup)
        print("[DEBUG] Getting incidents from cache...")
        incidents_from_db = get_incidents_cache()
        print(f"[DEBUG] Using {len(incidents_from_db)} cached incidents")
        
        if not incidents_from_db:
            return jsonify({
                'success': False,
                'message': 'No incidents found in database',
                'suggested_resolution': 'Database is empty. Please add incidents to knowledge base first.'
            })
        
        # Find similar incidents using simple keyword matching
        combined_description = f"{short_description} {problem_description}".lower()
        keywords = set(word for word in combined_description.split() if len(word) > 3)  # Only words > 3 chars
        
        print(f"[DEBUG] Search keywords: {keywords}")
        
        similar_incidents = []
        for incident in incidents_from_db:
            inc_desc = f"{incident.get('short_description', '')} {incident.get('description', '')}".lower()
            inc_resolution = incident.get('resolution_notes', '')
            
            # Skip incidents without resolution
            if not inc_resolution or len(inc_resolution) < 20:
                continue
            
            # Calculate similarity score (simple keyword matching)
            inc_words = set(word for word in inc_desc.split() if len(word) > 3)
            common_words = keywords.intersection(inc_words)
            
            # Calculate similarity as percentage of matching keywords
            if len(keywords) > 0:
                similarity_score = len(common_words) / len(keywords)
            else:
                similarity_score = 0
            
            # Also check category match
            if category and incident.get('category') == category:
                similarity_score += 0.3
            
            # Cap similarity at 1.0
            similarity_score = min(similarity_score, 1.0)
            
            # Lower threshold to 0.01 (1%) to catch more matches
            if similarity_score > 0.01:
                similar_incidents.append({
                    'incident': incident,
                    'score': similarity_score
                })
        
        print(f"[DEBUG] Found {len(similar_incidents)} incidents with similarity > 0.01")
        
        # Sort by similarity score
        similar_incidents.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"[DEBUG] Found {len(similar_incidents)} similar incidents with scores")
        
        if not similar_incidents:
            print("[DEBUG] No similar incidents found - returning empty message")
            return jsonify({
                'success': False,
                'message': 'No similar incidents found',
                'suggested_resolution': 'No similar past incidents found in knowledge base. Please enter resolution manually.'
            })
        
        # Get the best match
        best_match = similar_incidents[0]['incident']
        suggested_resolution = best_match.get('resolution_notes', '')
        
        # If best match has very low score, try to get any incident from same category
        if similar_incidents[0]['score'] < 0.1 and category:
            print(f"[DEBUG] Low score ({similar_incidents[0]['score']:.2f}), trying category fallback")
            for incident in incidents_from_db:
                if incident.get('category') == category and incident.get('resolution_notes') and len(incident.get('resolution_notes', '')) > 30:
                    best_match = incident
                    suggested_resolution = incident.get('resolution_notes', '')
                    print(f"[DEBUG] Using category fallback: {incident.get('number')}")
                    break
        
        print(f"[DEBUG] Found {len(similar_incidents)} similar incidents")
        print(f"[DEBUG] Best match: {best_match.get('number')} (score: {similar_incidents[0]['score']:.2f})")
        print(f"[DEBUG] Resolution length: {len(suggested_resolution)} characters")
        
        return jsonify({
            'success': True,
            'suggested_resolution': suggested_resolution,
            'confidence': round(similar_incidents[0]['score'] * 100, 1),
            'primary_source': {
                'number': best_match.get('number'),
                'short_description': best_match.get('short_description'),
                'category': best_match.get('category')
            },
            'alternatives': [
                {
                    'number': inc['incident'].get('number'),
                    'resolution': inc['incident'].get('resolution_notes', '')[:200] + '...',
                    'confidence': round(inc['score'] * 100, 1)
                }
                for inc in similar_incidents[1:4]  # Top 3 alternatives
            ]
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
    """Get all incidents from knowledge base (MongoDB)"""
    try:
        # Get incidents from MongoDB with resolutions
        incidents = db_client.search_incidents(limit=1000)
        
        # Filter only incidents with resolutions
        with_resolutions = [
            inc for inc in incidents 
            if inc.get('resolution_notes') and len(inc.get('resolution_notes', '')) > 10
        ]
        
        return jsonify({
            'success': True,
            'incidents': with_resolutions,
            'count': len(with_resolutions)
        })
            
    except Exception as e:
        print(f"[ERROR] Exception in get_knowledge_base: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/kb/update_incident/<incident_number>', methods=['PUT'])
def update_kb_incident(incident_number):
    """Update an existing incident in MongoDB (deprecated route for compatibility)"""
    return update_incident_by_number(incident_number)


@app.route('/kb/delete_incident/<incident_number>', methods=['DELETE'])
def delete_kb_incident(incident_number):
    """Delete an incident from MongoDB (deprecated route for compatibility)"""
    return delete_incident_by_number(incident_number)


@app.route('/sync_knowledge_base', methods=['POST'])
def sync_knowledge_base():
    """Sync MongoDB incidents to knowledge base for RAG system"""
    try:
        # Get all incidents with resolutions from MongoDB
        incidents = db_client.get_all_incidents(limit=10000)
        
        # Filter incidents with resolutions
        with_resolutions = [
            inc for inc in incidents 
            if inc.get('resolution_notes') and len(inc.get('resolution_notes', '')) > 10
        ]
        
        if not with_resolutions:
            return jsonify({
                'success': False,
                'error': 'No incidents with resolutions found'
            }), 400
        
        # Save to knowledge base JSON file
        kb_file = Path(__file__).parent / "data" / "knowledge_base.json"
        kb_file.parent.mkdir(parents=True, exist_ok=True)
        
        import json
        with open(kb_file, 'w', encoding='utf-8') as f:
            json.dump(with_resolutions, f, indent=2, ensure_ascii=False)
        
        # Reload RAG system
        global resolution_finder
        resolution_finder = None
        
        return jsonify({
            'success': True,
            'synced_count': len(with_resolutions),
            'message': f'Successfully synced {len(with_resolutions)} incidents to knowledge base'
        })
        
    except Exception as e:
        print(f"[ERROR] Exception in sync_knowledge_base: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/clear_all_incidents', methods=['POST'])
def clear_all_incidents():
    """Clear all incidents from MongoDB (dangerous operation)"""
    try:
        # Get count before deletion
        count_before = db_client.get_incident_count()
        
        # Delete all documents in collection
        result = db_client.collection.delete_many({})
        
        # Refresh cache after clearing all
        refresh_incidents_cache()
        
        return jsonify({
            'success': True,
            'deleted_count': result.deleted_count,
            'message': f'Deleted {result.deleted_count} incidents from MongoDB'
        })
        
    except Exception as e:
        print(f"[ERROR] Exception in clear_all_incidents: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/bulk_update', methods=['POST'])
def bulk_update():
    """Bulk update multiple incidents"""
    try:
        data = request.json
        incident_numbers = data.get('incident_numbers', [])
        update_fields = data.get('update_fields', {})
        
        if not incident_numbers or not update_fields:
            return jsonify({
                'success': False,
                'error': 'incident_numbers and update_fields are required'
            }), 400
        
        updated_count = 0
        for number in incident_numbers:
            if db_client.update_incident(number, update_fields):
                updated_count += 1
        
        return jsonify({
            'success': True,
            'updated_count': updated_count,
            'total': len(incident_numbers)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/get_incident/<incident_number>', methods=['GET'])
def get_incident(incident_number):
    """Get a single incident by number"""
    try:
        incident = db_client.get_incident_by_number(incident_number)
        
        if incident:
            return jsonify({
                'success': True,
                'incident': incident
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Incident not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500



if __name__ == '__main__':
    print("\n" + "="*70)
    print("SOP Generator Web Application Starting with MongoDB Integration...")
    print("="*70)
    print(f"\nMongoDB Database: {db_client.database_name}")
    print(f"Total Incidents: {db_client.get_incident_count()}")
    print(f"Categories: {', '.join(db_client.get_categories()[:10])}")
    print("\nAccess the application at: http://127.0.0.1:5000")
    print("\nPress CTRL+C to stop the server")
    print("="*70 + "\n")
    
    # Run with use_reloader=False to prevent issues with ML model loading
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
