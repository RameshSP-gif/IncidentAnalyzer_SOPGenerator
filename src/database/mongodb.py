"""
MongoDB Database Module

Handles all database operations for incident storage and retrieval.
"""

import os
from typing import List, Dict, Optional
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
from loguru import logger
import csv
import json


class MongoDBClient:
    """MongoDB client for incident management"""
    
    def __init__(
        self,
        connection_string: str = None,
        database_name: str = "incident_analyzer",
        collection_name: str = "incidents"
    ):
        """
        Initialize MongoDB client
        
        Args:
            connection_string: MongoDB connection string
            database_name: Name of the database
            collection_name: Name of the collection
        """
        self.connection_string = connection_string or os.getenv(
            "MONGODB_URI", 
            "mongodb://localhost:27017/"
        )
        self.database_name = database_name
        self.collection_name = collection_name
        
        # Initialize client
        logger.info(f"Connecting to MongoDB: {self.database_name}")
        self.client = MongoClient(self.connection_string)
        self.db = self.client[self.database_name]
        self.collection = self.db[self.collection_name]
        
        # Create indexes
        self._create_indexes()
        
    def _create_indexes(self):
        """Create necessary indexes for better performance"""
        try:
            # Unique index on incident number
            self.collection.create_index("number", unique=True)
            
            # Index on category for filtering
            self.collection.create_index("category")
            
            # Index on priority
            self.collection.create_index("priority")
            
            # Index on created date
            self.collection.create_index([("sys_created_on", DESCENDING)])
            
            # Text index for search
            self.collection.create_index([
                ("short_description", "text"),
                ("description", "text"),
                ("resolution_notes", "text")
            ])
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    def delete_all_incidents(self) -> int:
        """
        Delete all incidents from the collection
        
        Returns:
            Number of incidents deleted
        """
        try:
            result = self.collection.delete_many({})
            deleted_count = result.deleted_count
            logger.info(f"Deleted {deleted_count} incidents from database")
            return deleted_count
        except Exception as e:
            logger.error(f"Error deleting incidents: {e}")
            return 0
    
    def insert_incident(self, incident: Dict) -> Optional[str]:
        """
        Insert a single incident
        
        Args:
            incident: Incident data dictionary
            
        Returns:
            Inserted document ID or None if failed
        """
        try:
            # Add timestamp if not present
            if "sys_created_on" not in incident:
                incident["sys_created_on"] = datetime.now().isoformat()
            
            result = self.collection.insert_one(incident)
            logger.info(f"Inserted incident: {incident.get('number')}")
            return str(result.inserted_id)
        except DuplicateKeyError:
            logger.warning(f"Incident already exists: {incident.get('number')}")
            return None
        except Exception as e:
            logger.error(f"Error inserting incident: {e}")
            return None
    
    def insert_many_incidents(self, incidents: List[Dict]) -> int:
        """
        Insert multiple incidents
        
        Args:
            incidents: List of incident dictionaries
            
        Returns:
            Number of successfully inserted incidents
        """
        if not incidents:
            return 0
        
        inserted_count = 0
        errors = 0
        
        for incident in incidents:
            if self.insert_incident(incident):
                inserted_count += 1
            else:
                errors += 1
        
        logger.info(
            f"Bulk insert completed: {inserted_count} inserted, {errors} errors"
        )
        return inserted_count
    
    def get_incident_by_number(self, number: str) -> Optional[Dict]:
        """
        Get incident by incident number
        
        Args:
            number: Incident number
            
        Returns:
            Incident dictionary or None if not found
        """
        incident = self.collection.find_one({"number": number})
        if incident:
            incident['_id'] = str(incident['_id'])
        return incident
    
    def get_all_incidents(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "sys_created_on",
        sort_order: int = -1
    ) -> List[Dict]:
        """
        Get all incidents with pagination
        
        Args:
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            sort_by: Field to sort by
            sort_order: 1 for ascending, -1 for descending
            
        Returns:
            List of incident dictionaries
        """
        try:
            cursor = self.collection.find().skip(skip).limit(limit).sort(
                sort_by, sort_order
            )
            incidents = list(cursor)
            
            # Convert ObjectId to string
            for incident in incidents:
                incident['_id'] = str(incident['_id'])
            
            return incidents
        except Exception as e:
            logger.error(f"Error fetching incidents: {e}")
            return []
    
    def update_incident(self, number: str, update_data: Dict) -> bool:
        """
        Update an incident
        
        Args:
            number: Incident number
            update_data: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Remove _id if present
            update_data.pop('_id', None)
            
            # Add updated timestamp
            update_data['sys_updated_on'] = datetime.now().isoformat()
            
            result = self.collection.update_one(
                {"number": number},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"Updated incident: {number}")
                return True
            else:
                logger.warning(f"No changes made to incident: {number}")
                return False
        except Exception as e:
            logger.error(f"Error updating incident: {e}")
            return False
    
    def delete_incident(self, number: str) -> bool:
        """
        Delete an incident
        
        Args:
            number: Incident number
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.collection.delete_one({"number": number})
            
            if result.deleted_count > 0:
                logger.info(f"Deleted incident: {number}")
                return True
            else:
                logger.warning(f"Incident not found: {number}")
                return False
        except Exception as e:
            logger.error(f"Error deleting incident: {e}")
            return False
    
    def search_incidents(
        self,
        query: str = None,
        category: str = None,
        priority: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Search incidents by text query and filters
        
        Args:
            query: Text search query
            category: Filter by category
            priority: Filter by priority
            limit: Maximum number of results
            
        Returns:
            List of matching incidents
        """
        try:
            filter_dict = {}
            
            # Text search
            if query:
                filter_dict['$text'] = {'$search': query}
            
            # Category filter
            if category:
                filter_dict['category'] = category
            
            # Priority filter
            if priority:
                filter_dict['priority'] = priority
            
            cursor = self.collection.find(filter_dict).limit(limit)
            incidents = list(cursor)
            
            # Convert ObjectId to string
            for incident in incidents:
                incident['_id'] = str(incident['_id'])
            
            return incidents
        except Exception as e:
            logger.error(f"Error searching incidents: {e}")
            return []
    
    def get_incident_count(self) -> int:
        """
        Get total count of incidents
        
        Returns:
            Total number of incidents
        """
        try:
            return self.collection.count_documents({})
        except Exception as e:
            logger.error(f"Error counting incidents: {e}")
            return 0
    
    def get_categories(self) -> List[str]:
        """
        Get distinct categories
        
        Returns:
            List of unique categories
        """
        try:
            return self.collection.distinct("category")
        except Exception as e:
            logger.error(f"Error fetching categories: {e}")
            return []
    
    def import_from_csv(self, csv_file_path: str) -> Dict:
        """
        Import incidents from CSV file
        
        Args:
            csv_file_path: Path to CSV file
            
        Returns:
            Dictionary with import statistics
        """
        logger.info(f"Importing incidents from CSV: {csv_file_path}")
        
        imported = 0
        skipped = 0
        errors = 0
        
        try:
            # Try multiple encodings to handle different CSV formats
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
            file_content = None
            successful_encoding = None
            
            for encoding in encodings:
                try:
                    with open(csv_file_path, 'r', encoding=encoding) as f:
                        file_content = f.read()
                        successful_encoding = encoding
                        break
                except (UnicodeDecodeError, UnicodeError):
                    continue
            
            if file_content is None:
                raise ValueError("Could not decode CSV file with any known encoding. Please save the file as UTF-8.")
            
            logger.info(f"Successfully decoded CSV with encoding: {successful_encoding}")
            
            # Parse CSV with detected encoding
            from io import StringIO
            csv_data = StringIO(file_content)
            reader = csv.DictReader(csv_data)
            
            # Log CSV column headers for debugging
            if reader.fieldnames:
                logger.info(f"CSV columns found: {reader.fieldnames}")
            
            row_count = 0
            for row in reader:
                row_count += 1
                
                # Log first row for debugging
                if row_count == 1:
                    logger.info(f"First row sample: {dict(list(row.items())[:3])}")
                
                # Skip completely empty rows
                if not any(v and str(v).strip() for v in row.values()):
                    skipped += 1
                    continue
                
                # Convert row to incident format
                incident = self._csv_row_to_incident(row)
                
                if incident:
                    if self.insert_incident(incident):
                        imported += 1
                        if imported <= 3:
                            logger.info(f"Successfully imported: {incident['number']}")
                    else:
                        skipped += 1
                        logger.debug(f"Skipped duplicate: {incident.get('number', 'unknown')}")
                else:
                    errors += 1
            
            result = {
                'imported': imported,
                'skipped': skipped,
                'errors': errors,
                'total': imported + skipped + errors
            }
            
            logger.info(f"CSV import completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error importing CSV: {e}")
            return {
                'imported': imported,
                'skipped': skipped,
                'errors': errors + 1,
                'error_message': str(e),
                'total': imported + skipped + errors + 1
            }
    
    def _csv_row_to_incident(self, row: Dict) -> Optional[Dict]:
        """
        Convert CSV row to incident format
        
        Args:
            row: CSV row dictionary
            
        Returns:
            Incident dictionary or None if invalid
        """
        try:
            # Strip whitespace from keys and values, handle None
            cleaned_row = {}
            for k, v in row.items():
                if k:
                    key = str(k).strip()
                    if v is None:
                        cleaned_row[key] = ''
                    elif isinstance(v, str):
                        cleaned_row[key] = v.strip()
                    else:
                        cleaned_row[key] = str(v).strip()
            
            row = cleaned_row
            
            # Helper function to get values with multiple key attempts
            def get_value(*keys):
                """Try multiple key variations and return first non-empty value"""
                for key in keys:
                    val = row.get(key, '')
                    if val and val != 'None':
                        return val
                return ''
            
            # Extract fields with multiple column name variations
            number = get_value('number', 'Number', 'incident_number', 'Incident Number', 
                              'Incident_Number', 'incident_id', 'ID')
            
            short_desc = get_value('short_description', 'Short description', 'Short Description', 
                                  'short_desc', 'summary', 'Summary', 'Title', 'title')
            
            description = get_value('description', 'Description', 'details', 'Details',
                                   'long_description', 'Long Description')
            
            # If description is empty but short_description exists, use short_description
            if not description and short_desc:
                description = short_desc
            
            # Auto-generate number if missing
            if not number:
                number = f"INC{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Build incident object with all fields from CSV mapped correctly
            incident = {
                'number': number,
                'short_description': short_desc or description[:100] if description else 'Imported incident',
                'description': description or short_desc or 'No description provided',
                'contact_type': get_value('contact_type', 'Contact type', 'Contact Type', 'contacttype') or '',
                'service_offering': get_value('service_offering', 'Service offering', 'Service Offering', 'serviceoffering') or '',
                'category': get_value('category', 'Category') or 'General',
                'subcategory': get_value('subcategory', 'Subcategory', 'sub_category', 'Sub Category') or '',
                'priority': get_value('priority', 'Priority', 'pri') or '3',
                'state': get_value('state', 'State', 'status', 'Status', 'incident_state', 'Incident state', 'incident state') or 'Closed',
                'resolution_notes': get_value('resolution_notes', 'Resolution notes', 'Resolution Notes', 
                                             'resolution', 'Resolution', 'fix', 'Fix', 'solution', 'Solution',
                                             'resolutionnotes') or '',
                'close_notes': get_value('close_notes', 'Close Notes', 'Close notes', 'closing_notes', 'closenotes') or '',
                'closed_by': get_value('closed_by', 'Closed by', 'Closed By', 'closedby') or '',
                'work_notes': get_value('work_notes', 'Work Notes', 'Work notes', 'notes', 'Notes', 'worknotes') or '',
                'assignment_group': get_value('assignment_group', 'Assignment group', 'Assignment Group', 'group', 'assignmentgroup') or '',
                'assigned_to': get_value('assigned_to', 'Assigned to', 'Assigned To', 'assignee', 'Assignee', 'assignedto') or '',
                'sys_created_on': get_value('sys_created_on', 'Created', 'created_on', 'created', 'Created On') or datetime.now().isoformat(),
                'sys_updated_on': get_value('sys_updated_on', 'Updated', 'updated_on', 'modified', 'Updated On') or datetime.now().isoformat(),
                'resolved_at': get_value('resolved_at', 'Resolved', 'Resolved At', 'resolved', 'resolution_date', 'Resolved at') or '',
            }
            
            # Final validation - must have at least a description
            if not incident['short_description'] or incident['short_description'] == 'Imported incident':
                if not (number or short_desc or description):
                    logger.debug(f"Skipping empty row")
                    return None
            
            return incident
            
        except Exception as e:
            logger.error(f"Error converting CSV row: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def export_to_json(self, output_file: str) -> bool:
        """
        Export all incidents to JSON file
        
        Args:
            output_file: Path to output JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            incidents = self.get_all_incidents(limit=10000)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(incidents, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(incidents)} incidents to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return False
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


# Global database client instance
_db_client = None


def get_db_client(
    connection_string: str = None,
    database_name: str = "incident_analyzer"
) -> MongoDBClient:
    """
    Get or create global database client instance
    
    Args:
        connection_string: MongoDB connection string
        database_name: Name of the database
        
    Returns:
        MongoDBClient instance
    """
    global _db_client
    
    if _db_client is None:
        _db_client = MongoDBClient(
            connection_string=connection_string,
            database_name=database_name
        )
    
    return _db_client
