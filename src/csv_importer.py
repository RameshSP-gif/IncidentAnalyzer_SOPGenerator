"""
CSV Importer for Incidents
Handles importing incidents from CSV files and updating MongoDB knowledge base
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

try:
    from dateutil import parser as dateutil_parser
except ImportError:
    dateutil_parser = None

# Import MongoDB handler
try:
    from db.mongodb_handler import MongoDBHandler
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

class CSVIncidentImporter:
    """Import incidents from CSV files"""
    
    def __init__(self, validator=None, mongodb_uri: str = None):
        """
        Initialize CSV importer
        
        Args:
            validator: DataValidator instance for validating imported incidents
            mongodb_uri: Optional MongoDB connection string
        """
        self.validator = validator
        self.imported_incidents = []
        self.import_errors = []
        self.import_warnings = []
        
        # Initialize MongoDB handler if available
        self.mongodb = None
        if MONGODB_AVAILABLE:
            try:
                self.mongodb = MongoDBHandler(uri=mongodb_uri)
            except Exception as e:
                print(f"[WARNING] MongoDB initialization failed: {str(e)}")
                self.mongodb = None

    
    def import_from_csv(self, 
                       file_path: str,
                       field_mapping: Optional[Dict[str, str]] = None,
                       skip_invalid: bool = True) -> Tuple[List[Dict], List[Dict], List[str]]:
        """
        Import incidents from CSV file
        
        Args:
            file_path: Path to CSV file
            field_mapping: Optional mapping of CSV columns to incident fields
                          Example: {'Incident Number': 'number', 'Description': 'short_description'}
            skip_invalid: If True, skip invalid incidents; if False, raise error
            
        Returns:
            Tuple of (imported_incidents, errors, warnings)
        """
        self.imported_incidents = []
        self.import_errors = []
        self.import_warnings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                csv_reader = csv.DictReader(f)
                
                if not csv_reader.fieldnames:
                    raise ValueError("CSV file is empty or has no headers")
                
                # Auto-detect field mapping if not provided
                if field_mapping is None:
                    field_mapping = self._auto_detect_mapping(csv_reader.fieldnames)
                
                row_number = 1
                for row in csv_reader:
                    row_number += 1
                    
                    try:
                        # Convert CSV row to incident format
                        incident = self._convert_csv_row_to_incident(
                            row, 
                            field_mapping,
                            row_number
                        )
                        
                        # Validate if validator is available
                        if self.validator:
                            validation_result = self.validator.validate_incident(incident)
                            
                            if not validation_result['is_valid']:
                                error_msg = f"Row {row_number}: Invalid incident - "
                                error_msg += "; ".join([str(e) for e in validation_result.get('errors', [])])
                                
                                if skip_invalid:
                                    self.import_warnings.append(error_msg)
                                    continue
                                else:
                                    self.import_errors.append(error_msg)
                                    raise ValueError(error_msg)
                        
                        self.imported_incidents.append(incident)
                        
                    except Exception as e:
                        error_msg = f"Row {row_number}: {str(e)}"
                        if skip_invalid:
                            self.import_warnings.append(error_msg)
                        else:
                            self.import_errors.append(error_msg)
                            raise ValueError(error_msg)
            
            return self.imported_incidents, self.import_errors, self.import_warnings
            
        except Exception as e:
            self.import_errors.append(f"Failed to read CSV file: {str(e)}")
            return [], self.import_errors, self.import_warnings
    
    def _auto_detect_mapping(self, csv_headers: List[str]) -> Dict[str, str]:
        """
        Auto-detect field mapping from CSV headers
        
        Args:
            csv_headers: List of CSV column headers
            
        Returns:
            Mapping of CSV columns to incident fields
        """
        mapping = {}
        
        # Common field variations
        field_variations = {
            'number': ['ticket', 'incident', 'incident_number', 'ticket_number', 'id', 'number'],
            'short_description': ['short_description', 'summary', 'title', 'subject', 'brief'],
            'description': ['description', 'details', 'problem', 'problem_statement'],
            'category': ['category', 'type', 'incident_type', 'classification'],
            'subcategory': ['subcategory', 'sub_category', 'subtype'],
            'priority': ['priority', 'severity', 'impact'],
            'resolution_notes': ['resolution', 'resolution_notes', 'solution', 'fix', 'fix_description'],
            'assignment_group': ['assignment_group', 'assigned_group', 'team'],
            'assigned_to': ['assigned_to', 'assignee', 'owner'],
            'status': ['status', 'state', 'incident_state'],
            'sys_created_on': ['created_date', 'created_on', 'date_created', 'sys_created_on'],
            'resolved_at': ['resolved_date', 'resolved_at', 'date_resolved']
        }
        
        for header in csv_headers:
            header_lower = header.lower().strip()
            
            for incident_field, variations in field_variations.items():
                if any(var in header_lower for var in variations):
                    mapping[header] = incident_field
                    break
        
        return mapping
    
    def _convert_csv_row_to_incident(self, 
                                     row: Dict[str, str],
                                     field_mapping: Dict[str, str],
                                     row_number: int) -> Dict:
        """
        Convert a CSV row to incident format
        
        Args:
            row: CSV row as dictionary
            field_mapping: Mapping of CSV columns to incident fields
            row_number: Row number for error tracking
            
        Returns:
            Incident dictionary
        """
        incident = {}
        
        # Map CSV fields to incident format
        for csv_column, csv_value in row.items():
            if csv_column in field_mapping:
                incident_field = field_mapping[csv_column]
                incident[incident_field] = csv_value.strip() if csv_value else ""
        
        # Ensure required fields exist
        if 'number' not in incident or not incident['number']:
            incident['number'] = f"IMP_{row_number}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        if 'short_description' not in incident:
            # Try to use description or other fields as fallback
            incident['short_description'] = incident.get('description', '')[:100] or f"Imported Incident {row_number}"
        
        # Add metadata
        incident['imported_at'] = datetime.now().isoformat()
        incident['source'] = 'CSV Import'
        
        # Standardize date fields
        if 'sys_created_on' in incident and incident['sys_created_on']:
            try:
                incident['sys_created_on'] = self._parse_date(incident['sys_created_on'])
            except:
                pass  # Keep original if parsing fails
        
        if 'resolved_at' in incident and incident['resolved_at']:
            try:
                incident['resolved_at'] = self._parse_date(incident['resolved_at'])
            except:
                pass
        
        return incident
    
    def _parse_date(self, date_string: str) -> str:
        """
        Parse various date formats to ISO format
        
        Args:
            date_string: Date string in various formats
            
        Returns:
            ISO format date string
        """
        if dateutil_parser is None:
            # Return as-is if dateutil not available
            return date_string
        
        try:
            parsed_date = dateutil_parser.parse(date_string)
            return parsed_date.isoformat()
        except:
            # Return as-is if parsing fails
            return date_string
    
    def add_to_knowledge_base(self, 
                             incidents: List[Dict],
                             mongodb_uri: str = None,
                             kb_file_path: Path = None,
                             use_mongodb: bool = True) -> Tuple[int, List[str]]:
        """
        Add imported incidents to knowledge base
        Supports both MongoDB (primary) and JSON file (fallback)
        
        Args:
            incidents: List of incidents to add
            mongodb_uri: MongoDB connection URI (for MongoDB storage)
            kb_file_path: Path to knowledge base JSON file (for fallback)
            use_mongodb: Whether to use MongoDB if available
            
        Returns:
            Tuple of (count_added, errors)
        """
        errors = []
        count_added = 0
        
        # Initialize MongoDB if URI provided and not yet done
        if mongodb_uri and not self.mongodb and MONGODB_AVAILABLE:
            try:
                self.mongodb = MongoDBHandler(mongodb_uri)
            except Exception as e:
                errors.append(f"MongoDB connection failed: {str(e)}")
                self.mongodb = None
        
        # Try MongoDB first
        if use_mongodb and self.mongodb and self.mongodb.is_connected():
            return self._add_to_mongodb(incidents, errors)
        
        # Fallback to JSON file
        if kb_file_path:
            return self._add_to_json_file(incidents, str(kb_file_path), errors)
        
        errors.append("No storage backend available (MongoDB not connected and no file path provided)")
        return 0, errors
    
    def _add_to_mongodb(self, incidents: List[Dict], errors: List[str]) -> Tuple[int, List[str]]:
        """
        Add incidents to MongoDB
        
        Args:
            incidents: List of incidents
            errors: Error list to append to
            
        Returns:
            Tuple of (count_added, errors)
        """
        count_added = 0
        
        try:
            for incident in incidents:
                incident_number = incident.get('number')
                
                # Only add incidents with resolution notes to knowledge base
                if incident.get('resolution_notes') and len(incident.get('resolution_notes', '')) > 20:
                    if self.mongodb.add_incident(incident):
                        count_added += 1
                    else:
                        errors.append(f"Incident {incident_number} already exists in MongoDB KB")
                else:
                    errors.append(f"Incident {incident_number} has no resolution - skipped")
            
            print(f"[INFO] Added {count_added} incidents to MongoDB knowledge base")
            return count_added, errors
            
        except Exception as e:
            errors.append(f"MongoDB operation failed: {str(e)}")
            return count_added, errors
    
    def _add_to_json_file(self, incidents: List[Dict], kb_file_path: str, errors: List[str]) -> Tuple[int, List[str]]:
        """
        Fallback: Add incidents to JSON file
        
        Args:
            incidents: List of incidents
            kb_file_path: Path to JSON file
            errors: Error list to append to
            
        Returns:
            Tuple of (count_added, errors)
        """
        count_added = 0
        
        try:
            # Load existing knowledge base
            kb_file = Path(kb_file_path)
            if kb_file.exists():
                with open(kb_file, 'r', encoding='utf-8') as f:
                    kb_data = json.load(f)
            else:
                kb_data = []
            
            # Track existing incident numbers
            existing_numbers = {inc.get('number') for inc in kb_data}
            
            # Add new incidents
            for incident in incidents:
                incident_number = incident.get('number')
                
                if incident_number in existing_numbers:
                    errors.append(f"Incident {incident_number} already exists in KB")
                    continue
                
                # Only add incidents with resolution notes to knowledge base
                if incident.get('resolution_notes') and len(incident.get('resolution_notes', '')) > 20:
                    kb_data.append(incident)
                    existing_numbers.add(incident_number)
                    count_added += 1
                else:
                    errors.append(f"Incident {incident_number} has no resolution - skipped")
            
            # Save updated knowledge base
            kb_file.parent.mkdir(parents=True, exist_ok=True)
            with open(kb_file, 'w', encoding='utf-8') as f:
                json.dump(kb_data, f, indent=2, ensure_ascii=False)
            
            return count_added, errors
            
        except Exception as e:
            errors.append(f"JSON file operation failed: {str(e)}")
            return count_added, errors
    
    def get_import_summary(self) -> Dict:
        """
        Get summary of last import operation
        
        Returns:
            Summary dictionary
        """
        return {
            'total_imported': len(self.imported_incidents),
            'errors': len(self.import_errors),
            'warnings': len(self.import_warnings),
            'error_details': self.import_errors,
            'warning_details': self.import_warnings,
            'incidents': self.imported_incidents
        }
    
    @staticmethod
    def create_sample_csv(output_path: str) -> None:
        """
        Create a sample CSV template for importing incidents
        
        Args:
            output_path: Path to save sample CSV
        """
        sample_data = [
            {
                'Incident Number': 'INC0001234',
                'Short Description': 'Database connection timeout',
                'Description': 'Application unable to connect to primary database server. Users cannot access the system.',
                'Category': 'Database',
                'Priority': '1',
                'Status': 'Closed',
                'Assignment Group': 'Database Team',
                'Assigned To': 'John Doe',
                'Resolution Notes': 'Restarted database service and verified connectivity. Implemented connection pooling to prevent future issues.',
                'Created Date': '2024-01-15',
                'Resolved Date': '2024-01-15'
            },
            {
                'Incident Number': 'INC0001235',
                'Short Description': 'Email delivery failure',
                'Description': 'System unable to send email notifications. Queue is stuck with 500+ pending emails.',
                'Category': 'Email',
                'Priority': '2',
                'Status': 'Closed',
                'Assignment Group': 'Application Team',
                'Assigned To': 'Jane Smith',
                'Resolution Notes': 'Cleared stuck email queue and restarted mail service. Updated DNS MX records.',
                'Created Date': '2024-01-16',
                'Resolved Date': '2024-01-17'
            }
        ]
        
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                fieldnames = list(sample_data[0].keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(sample_data)
            
            print(f"[INFO] Sample CSV created at {output_path}")
        except Exception as e:
            print(f"[ERROR] Failed to create sample CSV: {str(e)}")


def create_csv_importer(validator=None) -> CSVIncidentImporter:
    """
    Factory function to create CSV importer
    
    Args:
        validator: Optional DataValidator instance
        
    Returns:
        CSVIncidentImporter instance
    """
    return CSVIncidentImporter(validator=validator)
