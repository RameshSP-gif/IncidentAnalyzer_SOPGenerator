"""
MongoDB Handler for Knowledge Base Management
Manages incident storage and retrieval from MongoDB
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from typing import Dict, List, Optional
import os
from datetime import datetime
from loguru import logger


class MongoDBHandler:
    """MongoDB handler for knowledge base operations"""
    
    def __init__(self, 
                 uri: str = None,
                 db_name: str = "incident_analyzer",
                 collection_name: str = "knowledge_base"):
        """
        Initialize MongoDB connection
        
        Args:
            uri: MongoDB connection string (defaults to local MongoDB)
            db_name: Database name
            collection_name: Collection name for incidents
        """
        # Use provided URI or environment variable or default to local
        self.uri = uri or os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        self.db_name = db_name
        self.collection_name = collection_name
        
        self.client = None
        self.db = None
        self.collection = None
        
        self._connect()
    
    def _connect(self) -> bool:
        """
        Connect to MongoDB
        
        Returns:
            True if connected successfully, False otherwise
        """
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')
            
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            
            # Create indexes for better performance
            self._create_indexes()
            
            logger.info(f"✓ Connected to MongoDB: {self.db_name}.{self.collection_name}")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"✗ Failed to connect to MongoDB: {str(e)}")
            logger.warning("MongoDB not available. Using fallback mode.")
            return False
        except Exception as e:
            logger.error(f"✗ MongoDB connection error: {str(e)}")
            return False
    
    def _create_indexes(self):
        """Create indexes for efficient querying"""
        try:
            # Index for incident number (unique)
            self.collection.create_index("number", unique=True, sparse=True)
            
            # Index for category (for filtering)
            self.collection.create_index("category")
            
            # Index for priority
            self.collection.create_index("priority")
            
            # Text index for search
            self.collection.create_index([
                ("short_description", "text"),
                ("description", "text"),
                ("resolution_notes", "text")
            ])
            
            logger.info("✓ MongoDB indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Note: Some indexes may already exist: {str(e)}")
    
    def is_connected(self) -> bool:
        """Check if MongoDB is connected"""
        if not self.client:
            return False
        
        try:
            self.client.admin.command('ping')
            return True
        except:
            return False
    
    def add_incident(self, incident: Dict) -> bool:
        """
        Add a single incident to knowledge base
        
        Args:
            incident: Incident dictionary
            
        Returns:
            True if successful
        """
        if not self.is_connected():
            logger.error("MongoDB not connected")
            return False
        
        try:
            incident_number = incident.get('number')
            
            # Check if incident already exists
            existing = self.collection.find_one({"number": incident_number})
            
            if existing:
                logger.warning(f"Incident {incident_number} already exists in KB")
                return False
            
            # Add timestamp
            incident['added_at'] = datetime.now().isoformat()
            incident['updated_at'] = datetime.now().isoformat()
            
            # Calculate resolution_length for RAG filtering
            resolution_notes = incident.get('resolution_notes', '')
            incident['resolution_length'] = len(resolution_notes) if resolution_notes else 0
            
            result = self.collection.insert_one(incident)
            logger.info(f"✓ Added incident {incident_number} to knowledge base")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to add incident: {str(e)}")
            return False
    
    def add_incidents_batch(self, incidents: List[Dict]) -> tuple:
        """
        Add multiple incidents to knowledge base
        
        Args:
            incidents: List of incident dictionaries
            
        Returns:
            Tuple of (count_added, errors)
        """
        if not self.is_connected():
            logger.error("MongoDB not connected")
            return 0, ["MongoDB not connected"]
        
        count_added = 0
        errors = []
        
        for incident in incidents:
            if self.add_incident(incident):
                count_added += 1
            else:
                errors.append(f"Failed to add {incident.get('number')}")
        
        logger.info(f"✓ Batch add: {count_added} incidents added, {len(errors)} errors")
        return count_added, errors
    
    def get_all_incidents(self) -> List[Dict]:
        """
        Get all incidents from knowledge base
        
        Returns:
            List of incidents
        """
        if not self.is_connected():
            logger.error("MongoDB not connected")
            return []
        
        try:
            incidents = list(self.collection.find({}, {"_id": 0}))
            logger.info(f"✓ Retrieved {len(incidents)} incidents from KB")
            return incidents
            
        except Exception as e:
            logger.error(f"✗ Failed to retrieve incidents: {str(e)}")
            return []
    
    def get_incidents_by_category(self, category: str) -> List[Dict]:
        """
        Get incidents filtered by category
        
        Args:
            category: Category to filter by
            
        Returns:
            List of incidents in category
        """
        if not self.is_connected():
            return []
        
        try:
            incidents = list(self.collection.find(
                {"category": category},
                {"_id": 0}
            ))
            return incidents
            
        except Exception as e:
            logger.error(f"✗ Failed to retrieve incidents by category: {str(e)}")
            return []
    
    def get_resolved_incidents(self) -> List[Dict]:
        """
        Get only resolved incidents (with resolution notes)
        
        Returns:
            List of resolved incidents
        """
        if not self.is_connected():
            return []
        
        try:
            incidents = list(self.collection.find(
                {
                    "resolution_notes": {"$exists": True, "$ne": ""},
                    "resolution_length": {"$gte": 30}
                },
                {"_id": 0}
            ))
            return incidents
            
        except Exception as e:
            # Fallback: filter in Python
            try:
                all_incidents = self.get_all_incidents()
                resolved = [
                    inc for inc in all_incidents
                    if inc.get('resolution_notes') and len(inc.get('resolution_notes', '')) > 20
                ]
                return resolved
            except:
                return []
    
    def get_unresolved_incidents(self) -> List[Dict]:
        """
        Get only unresolved incidents
        
        Returns:
            List of unresolved incidents
        """
        if not self.is_connected():
            return []
        
        try:
            incidents = list(self.collection.find(
                {
                    "$or": [
                        {"resolution_notes": {"$exists": False}},
                        {"resolution_notes": ""},
                        {"resolution_notes": None}
                    ]
                },
                {"_id": 0}
            ))
            return incidents
            
        except Exception as e:
            logger.error(f"✗ Failed to retrieve unresolved incidents: {str(e)}")
            return []
    
    def get_incident_by_number(self, incident_number: str) -> Optional[Dict]:
        """
        Get a specific incident by number
        
        Args:
            incident_number: Incident number
            
        Returns:
            Incident dictionary or None
        """
        if not self.is_connected():
            return None
        
        try:
            incident = self.collection.find_one(
                {"number": incident_number},
                {"_id": 0}
            )
            return incident
            
        except Exception as e:
            logger.error(f"✗ Failed to retrieve incident {incident_number}: {str(e)}")
            return None
    
    def search_incidents(self, query: str, category: str = None) -> List[Dict]:
        """
        Search incidents by text
        
        Args:
            query: Search query string
            category: Optional category filter
            
        Returns:
            List of matching incidents
        """
        if not self.is_connected():
            return []
        
        try:
            search_filter = {"$text": {"$search": query}}
            if category:
                search_filter["category"] = category
            
            incidents = list(self.collection.find(
                search_filter,
                {"_id": 0, "score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]))
            
            return incidents
            
        except Exception as e:
            # Fallback to simple text search
            logger.warning(f"Text search failed, using fallback: {str(e)}")
            all_incidents = self.get_all_incidents()
            query_lower = query.lower()
            
            filtered = [
                inc for inc in all_incidents
                if query_lower in inc.get('short_description', '').lower() or
                   query_lower in inc.get('description', '').lower() or
                   query_lower in inc.get('resolution_notes', '').lower()
            ]
            
            if category:
                filtered = [inc for inc in filtered if inc.get('category') == category]
            
            return filtered
    
    def update_incident(self, incident_number: str, update_data: Dict) -> bool:
        """
        Update an incident
        
        Args:
            incident_number: Incident number to update
            update_data: Dictionary with fields to update
            
        Returns:
            True if successful
        """
        if not self.is_connected():
            return False
        
        try:
            update_data['updated_at'] = datetime.now().isoformat()
            
            result = self.collection.update_one(
                {"number": incident_number},
                {"$set": update_data}
            )
            
            if result.matched_count > 0:
                logger.info(f"✓ Updated incident {incident_number}")
                return True
            else:
                logger.warning(f"Incident {incident_number} not found")
                return False
                
        except Exception as e:
            logger.error(f"✗ Failed to update incident: {str(e)}")
            return False
    
    def delete_incident(self, incident_number: str) -> bool:
        """
        Delete an incident
        
        Args:
            incident_number: Incident number to delete
            
        Returns:
            True if successful
        """
        if not self.is_connected():
            return False
        
        try:
            result = self.collection.delete_one({"number": incident_number})
            
            if result.deleted_count > 0:
                logger.info(f"✓ Deleted incident {incident_number}")
                return True
            else:
                logger.warning(f"Incident {incident_number} not found")
                return False
                
        except Exception as e:
            logger.error(f"✗ Failed to delete incident: {str(e)}")
            return False
    
    def get_statistics(self) -> Dict:
        """
        Get knowledge base statistics
        
        Returns:
            Dictionary with KB stats
        """
        if not self.is_connected():
            return {"error": "MongoDB not connected"}
        
        try:
            total = self.collection.count_documents({})
            
            resolved = self.collection.count_documents({
                "resolution_notes": {"$exists": True, "$ne": ""}
            })
            
            unresolved = total - resolved
            
            # Category distribution
            pipeline = [
                {"$group": {"_id": "$category", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            categories = list(self.collection.aggregate(pipeline))
            
            return {
                "total_incidents": total,
                "resolved_incidents": resolved,
                "unresolved_incidents": unresolved,
                "resolution_rate": round(resolved / total * 100, 2) if total > 0 else 0,
                "by_category": {cat["_id"]: cat["count"] for cat in categories},
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"✗ Failed to get statistics: {str(e)}")
            return {"error": str(e)}
    
    def clear_all(self) -> bool:
        """
        Clear all incidents from knowledge base (use with caution!)
        
        Returns:
            True if successful
        """
        if not self.is_connected():
            return False
        
        try:
            result = self.collection.delete_many({})
            logger.warning(f"⚠ Cleared {result.deleted_count} incidents from KB")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to clear KB: {str(e)}")
            return False
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("✓ MongoDB connection closed")


def get_mongodb_handler(uri: str = None) -> MongoDBHandler:
    """
    Factory function to get MongoDB handler
    
    Args:
        uri: Optional MongoDB connection URI
        
    Returns:
        MongoDBHandler instance
    """
    return MongoDBHandler(uri=uri)
