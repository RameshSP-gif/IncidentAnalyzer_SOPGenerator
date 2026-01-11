"""
Flask Web Application for SOP Generation
Professional UI for incident analysis and SOP creation
With MongoDB Knowledge Base Backend
"""

from flask import Flask, render_template, request, jsonify, send_file
import sys
from pathlib import Path
from datetime import datetime
import io
import json
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_validation import DataValidator
from sop_generation import SOPGenerator
from csv_importer import CSVIncidentImporter

# Import MongoDB handler
try:
    from db.mongodb_handler import MongoDBHandler
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

app = Flask(__name__)

# MongoDB initialization
mongodb_handler = None

def get_mongodb_handler():
    """Get or initialize MongoDB handler"""
    global mongodb_handler
    if mongodb_handler is None and MONGODB_AVAILABLE:
        try:
            mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017')
            mongodb_handler = MongoDBHandler(mongodb_uri)
            print(f"✓ MongoDB connected successfully")
        except Exception as e:
            print(f"⚠ MongoDB connection failed, will use JSON fallback: {e}")
            mongodb_handler = None
    return mongodb_handler

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
        
        # Get MongoDB URI for resolution finder
        mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017')
        resolution_finder = ResolutionFinder(
            embedding_model="all-MiniLM-L6-v2",
            mongodb_uri=mongodb_uri
        )
        
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
    """Get all incidents from knowledge base (MongoDB or JSON)"""
    try:
        # Try MongoDB first
        mongodb = get_mongodb_handler()
        kb_data = []
        storage_type = 'MongoDB'
        
        if mongodb:
            kb_data = mongodb.get_all_incidents()
        else:
            # Fallback to JSON file
            kb_file = Path(__file__).parent / 'data' / 'knowledge_base.json'
            storage_type = 'JSON'
            
            if kb_file.exists():
                with open(kb_file, 'r', encoding='utf-8') as f:
                    kb_data = json.load(f)
        
        return jsonify({
            'success': True,
            'incidents': kb_data,
            'count': len(kb_data),
            'storage': storage_type
        })
            
    except Exception as e:
        print(f"[ERROR] Exception in get_knowledge_base: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/update_incident/<incident_number>', methods=['PUT'])
def update_incident(incident_number):
    """Update an existing incident in knowledge base (MongoDB or JSON)"""
    try:
        data = request.json
        
        # Try MongoDB first
        mongodb = get_mongodb_handler()
        storage_type = 'MongoDB'
        
        # Prepare updated incident
        update_data = {
            'short_description': data.get('short_description'),
            'description': data.get('description'),
            'category': data.get('category'),
            'priority': data.get('priority'),
            'resolution_notes': data.get('resolution_notes'),
            'updated_at': datetime.now().isoformat()
        }
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        incident_found = False
        
        if mongodb:
            try:
                result = mongodb.update_incident(incident_number, update_data)
                incident_found = result is not None
            except Exception as e:
                print(f"[WARNING] MongoDB update failed, falling back to JSON: {e}")
        
        # Fallback to JSON file
        if not mongodb or not incident_found:
            storage_type = 'JSON'
            kb_file = Path(__file__).parent / 'data' / 'knowledge_base.json'
            
            if not kb_file.exists():
                return jsonify({
                    'success': False,
                    'error': 'Knowledge base not found'
                }), 404
            
            with open(kb_file, 'r', encoding='utf-8') as f:
                kb_data = json.load(f)
            
            # Find and update incident
            for i, incident in enumerate(kb_data):
                if incident.get('number') == incident_number:
                    kb_data[i].update(update_data)
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
            'storage': storage_type,
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
    """Delete an incident from knowledge base (MongoDB or JSON)"""
    try:
        # Try MongoDB first
        mongodb = get_mongodb_handler()
        storage_type = 'MongoDB'
        incident_found = False
        
        if mongodb:
            try:
                mongodb.delete_incident(incident_number)
                incident_found = True
            except Exception as e:
                print(f"[WARNING] MongoDB delete failed, falling back to JSON: {e}")
        
        # Fallback to JSON file
        if not mongodb or not incident_found:
            storage_type = 'JSON'
            kb_file = Path(__file__).parent / 'data' / 'knowledge_base.json'
            
            if not kb_file.exists():
                return jsonify({
                    'success': False,
                    'error': 'Knowledge base not found'
                }), 404
            
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
            'storage': storage_type,
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
    """Search incidents in knowledge base (MongoDB or JSON)"""
    try:
        data = request.json
        search_query = data.get('query', '').lower()
        category_filter = data.get('category', '')
        
        # Try MongoDB first
        mongodb = get_mongodb_handler()
        storage_type = 'MongoDB'
        filtered = []
        
        if mongodb:
            try:
                # MongoDB text search
                if search_query:
                    filtered = mongodb.search_incidents(search_query)
                else:
                    filtered = mongodb.get_all_incidents()
                
                # Apply category filter
                if category_filter:
                    filtered = [inc for inc in filtered if inc.get('category') == category_filter]
            except Exception as e:
                print(f"[WARNING] MongoDB search failed, falling back to JSON: {e}")
        
        # Fallback to JSON file
        if not mongodb or not filtered:
            storage_type = 'JSON'
            kb_file = Path(__file__).parent / 'data' / 'knowledge_base.json'
            
            if not kb_file.exists():
                return jsonify({
                    'success': True,
                    'incidents': [],
                    'count': 0,
                    'storage': storage_type
                })
            
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
            'count': len(filtered),
            'storage': storage_type
        })
        
    except Exception as e:
        print(f"[ERROR] Exception in search_incidents: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/import_csv', methods=['POST'])
def import_csv():
    """Import incidents from CSV file and add to knowledge base"""
    try:
        # Check if file is in request
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
        
        if not file.filename.endswith('.csv'):
            return jsonify({
                'success': False,
                'error': 'Only CSV files are supported'
            }), 400
        
        # Get optional field mapping from request
        field_mapping_str = request.form.get('field_mapping')
        field_mapping = None
        if field_mapping_str:
            try:
                field_mapping = json.loads(field_mapping_str)
            except:
                pass
        
        # Save file temporarily
        temp_file_path = Path(__file__).parent / 'temp' / file.filename
        temp_file_path.parent.mkdir(parents=True, exist_ok=True)
        file.save(str(temp_file_path))
        
        try:
            # Create importer and import incidents
            importer = CSVIncidentImporter(validator=validator)
            imported_incidents, errors, warnings = importer.import_from_csv(
                str(temp_file_path),
                field_mapping=field_mapping,
                skip_invalid=True
            )
            
            if not imported_incidents:
                return jsonify({
                    'success': False,
                    'error': 'No valid incidents found in CSV',
                    'errors': errors,
                    'warnings': warnings
                }), 400
            
            # Add to local incidents database
            incidents_db.extend(imported_incidents)
            
            # Add to knowledge base (MongoDB or JSON fallback)
            mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017')
            kb_added, kb_errors = importer.add_to_knowledge_base(
                imported_incidents,
                mongodb_uri=mongodb_uri,
                kb_file_path=Path(__file__).parent / 'data' / 'knowledge_base.json'
            )
            
            # Reload RAG system
            global resolution_finder
            resolution_finder = None
            
            print(f"[INFO] Imported {len(imported_incidents)} incidents, {kb_added} added to knowledge base")
            
            return jsonify({
                'success': True,
                'total_imported': len(imported_incidents),
                'added_to_kb': kb_added,
                'added_to_db': len(incidents_db),
                'errors': errors,
                'warnings': warnings,
                'kb_errors': kb_errors,
                'message': f"Successfully imported {len(imported_incidents)} incidents, {kb_added} added to knowledge base"
            })
            
        finally:
            # Clean up temp file
            if temp_file_path.exists():
                temp_file_path.unlink()
        
    except Exception as e:
        print(f"[ERROR] Exception in import_csv: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/export_template', methods=['GET'])
def export_template():
    """Export sample CSV template for import"""
    try:
        # Create sample CSV content
        sample_content = """Incident Number,Short Description,Description,Category,Priority,Status,Assignment Group,Assigned To,Resolution Notes,Created Date,Resolved Date
INC0001234,Database connection timeout,Application unable to connect to primary database server. Users cannot access the system.,Database,1,Closed,Database Team,John Doe,Restarted database service and verified connectivity. Implemented connection pooling to prevent future issues.,2024-01-15,2024-01-15
INC0001235,Email delivery failure,System unable to send email notifications. Queue is stuck with 500+ pending emails.,Email,2,Closed,Application Team,Jane Smith,Cleared stuck email queue and restarted mail service. Updated DNS MX records.,2024-01-16,2024-01-17
INC0001236,Login page not responding,Users report that login page fails to load. Service is timing out.,Authentication,2,Closed,Web Team,Mike Johnson,Cleared web server cache and restarted nginx. Updated SSL certificates.,2024-01-17,2024-01-18
INC0001237,Report generation timeout,Monthly reports take over 1 hour to generate.,Reporting,3,Closed,Analytics Team,Sarah Williams,Optimized SQL queries and added database indexes for report tables.,2024-01-18,2024-01-19
INC0001238,API rate limit errors,Third-party integrations receiving 429 rate limit errors.,Integration,2,Closed,API Team,Tom Brown,Increased rate limits and implemented request throttling with queue management.,2024-01-19,2024-01-20
"""
        
        # Create response
        bytes_io = io.BytesIO(sample_content.encode('utf-8'))
        bytes_io.seek(0)
        
        return send_file(
            bytes_io,
            mimetype='text/csv',
            as_attachment=True,
            download_name='incident_import_template.csv'
        )
        
    except Exception as e:
        print(f"[ERROR] Exception in export_template: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/get_csv_field_mapping', methods=['GET'])
def get_csv_field_mapping():
    """Get suggested field mapping for CSV import"""
    try:
        # Common field variations
        field_variations = {
            'number': ['Ticket', 'Incident', 'Incident Number', 'Ticket Number', 'ID', 'Number'],
            'short_description': ['Short Description', 'Summary', 'Title', 'Subject', 'Brief'],
            'description': ['Description', 'Details', 'Problem', 'Problem Statement'],
            'category': ['Category', 'Type', 'Incident Type', 'Classification'],
            'priority': ['Priority', 'Severity', 'Impact'],
            'resolution_notes': ['Resolution', 'Resolution Notes', 'Solution', 'Fix'],
            'assignment_group': ['Assignment Group', 'Assigned Group', 'Team'],
            'assigned_to': ['Assigned To', 'Assignee', 'Owner'],
            'status': ['Status', 'State', 'Incident State'],
            'sys_created_on': ['Created Date', 'Created On', 'Date Created'],
            'resolved_at': ['Resolved Date', 'Resolved At', 'Date Resolved']
        }
        
        return jsonify({
            'success': True,
            'field_variations': field_variations,
            'description': 'Suggested CSV column names for each incident field'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/batch_resolve_incidents', methods=['POST'])
def batch_resolve_incidents():
    """Batch resolve incidents using RAG suggestions and update knowledge base"""
    try:
        data = request.json
        incident_numbers = data.get('incident_numbers', [])
        use_rag_suggestions = data.get('use_rag_suggestions', True)
        
        if not incident_numbers:
            return jsonify({
                'success': False,
                'error': 'No incident numbers provided'
            }), 400
        
        # Get MongoDB handler
        mongodb = get_mongodb_handler()
        
        # Load knowledge base from MongoDB or JSON
        kb_data = []
        if mongodb:
            kb_data = mongodb.get_all_incidents()
        else:
            # Fallback to JSON file
            kb_file_path = Path(__file__).parent / 'data' / 'knowledge_base.json'
            if kb_file_path.exists():
                with open(kb_file_path, 'r', encoding='utf-8') as f:
                    kb_data = json.load(f)
        
        if not kb_data:
            return jsonify({
                'success': False,
                'error': 'Knowledge base is empty'
            }), 404
        
        # Load RAG finder for suggestions
        finder = get_resolution_finder() if use_rag_suggestions else None
        
        updated_incidents = []
        failed_incidents = []
        
        for incident_number in incident_numbers:
            try:
                # Find incident in knowledge base
                incident_found = False
                for incident in kb_data:
                    if incident.get('number') == incident_number:
                        incident_found = True
                        
                        # If no resolution, try RAG suggestion
                        if not incident.get('resolution_notes') or len(incident.get('resolution_notes', '')) < 30:
                            if finder:
                                # Get RAG suggestion
                                full_description = f"{incident.get('short_description', '')}. {incident.get('description', '')}"
                                suggestion = finder.suggest_resolution(
                                    problem_description=full_description,
                                    category=incident.get('category')
                                )
                                
                                if suggestion['success']:
                                    incident['resolution_notes'] = suggestion['suggested_resolution']
                                    incident['resolution_source'] = 'RAG Suggestion'
                                    incident['resolution_confidence'] = suggestion.get('confidence', 0)
                                    incident['updated_at'] = datetime.now().isoformat()
                                    
                                    # Update in MongoDB if available
                                    if mongodb:
                                        mongodb.update_incident(incident_number, incident)
                        
                        updated_incidents.append(incident)
                        break
                
                if not incident_found:
                    failed_incidents.append({
                        'number': incident_number,
                        'error': 'Incident not found in knowledge base'
                    })
                    
            except Exception as e:
                failed_incidents.append({
                    'number': incident_number,
                    'error': str(e)
                })
        
        # Save updated knowledge base to JSON as fallback
        kb_file_path = Path(__file__).parent / 'data' / 'knowledge_base.json'
        kb_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(kb_file_path, 'w', encoding='utf-8') as f:
            json.dump(kb_data, f, indent=2, ensure_ascii=False)
        
        # Reload RAG system
        global resolution_finder
        resolution_finder = None
        
        return jsonify({
            'success': True,
            'updated_count': len(updated_incidents),
            'failed_count': len(failed_incidents),
            'updated_incidents': updated_incidents,
            'failed_incidents': failed_incidents,
            'storage': 'MongoDB' if mongodb else 'JSON',
            'message': f"Updated {len(updated_incidents)} incidents with resolutions"
        })
        
    except Exception as e:
        print(f"[ERROR] Exception in batch_resolve_incidents: {str(e)}")
        import traceback
        traceback.print_exc()
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
    
    # Auto-load sample data into MongoDB if available and empty
    try:
        mongodb = get_mongodb_handler()
        if mongodb and mongodb.is_connected():
            # Check if MongoDB is empty
            count = mongodb.collection.count_documents({})
            if count == 0:
                # Load from knowledge_base.json
                kb_file = Path(__file__).parent / "data" / "knowledge_base.json"
                if kb_file.exists():
                    print("[INFO] Loading sample incidents from knowledge_base.json...")
                    with open(kb_file, 'r', encoding='utf-8') as f:
                        incidents = json.load(f)
                    
                    # Add incidents to MongoDB
                    added, errors = mongodb.add_incidents_batch(incidents)
                    print(f"[INFO] Loaded {added} sample incidents into MongoDB")
                    if errors:
                        print(f"[WARNING] Errors during load: {errors}")
    except Exception as e:
        print(f"[WARNING] Could not auto-load sample data: {str(e)}")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
