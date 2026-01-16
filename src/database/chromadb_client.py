"""
ChromaDB Client for Vector Storage
Stores and retrieves incident embeddings for fast similarity search
"""

import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
from loguru import logger


class ChromaDBClient:
    """ChromaDB client for storing and retrieving incident embeddings"""
    
    def __init__(
        self,
        collection_name: str = "incident_resolutions",
        persist_directory: str = None,
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize ChromaDB client
        
        Args:
            collection_name: Name of the collection
            persist_directory: Directory to store ChromaDB data
            embedding_model: Sentence transformer model for embeddings
        """
        self.collection_name = collection_name
        
        # Set persist directory
        if persist_directory is None:
            persist_directory = str(Path(__file__).parent.parent.parent / "data" / "chromadb")
        
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB client with persistence
        logger.info(f"Initializing ChromaDB at: {persist_directory}")
        self.client = chromadb.Client(
            Settings(
                persist_directory=persist_directory,
                anonymized_telemetry=False
            )
        )
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(f"Loaded existing collection: {collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "Incident resolution embeddings for RAG"}
            )
            logger.info(f"Created new collection: {collection_name}")
    
    def add_incident(self, incident: Dict) -> bool:
        """
        Add a single incident to ChromaDB
        
        Args:
            incident: Incident dictionary with resolution
            
        Returns:
            True if successful
        """
        try:
            # Check if incident has resolution
            if not incident.get('resolution_notes') or len(incident.get('resolution_notes', '')) < 20:
                logger.warning(f"Incident {incident.get('number')} has insufficient resolution notes")
                return False
            
            # Create text for embedding
            text = self._create_embedding_text(incident)
            
            # Generate embedding
            embedding = self.embedding_model.encode(text).tolist()
            
            # Prepare metadata (only store simple types in metadata)
            metadata = {
                "number": incident.get('number', 'Unknown'),
                "category": incident.get('category', 'Unknown'),
                "short_description": incident.get('short_description', '')[:500],  # Limit length
                "priority": str(incident.get('priority', '3'))
            }
            
            # Add to collection
            self.collection.add(
                ids=[incident.get('number', f"INC_{id(incident)}")],
                embeddings=[embedding],
                documents=[incident.get('resolution_notes', '')],
                metadatas=[metadata]
            )
            
            logger.info(f"Added incident {incident.get('number')} to ChromaDB")
            return True
            
        except Exception as e:
            logger.error(f"Error adding incident to ChromaDB: {e}")
            return False
    
    def add_incidents_bulk(self, incidents: List[Dict]) -> int:
        """
        Add multiple incidents to ChromaDB in bulk
        
        Args:
            incidents: List of incident dictionaries
            
        Returns:
            Number of successfully added incidents
        """
        # Filter incidents with resolutions OR at least good descriptions
        valid_incidents = [
            inc for inc in incidents 
            if (inc.get('resolution_notes') and len(inc.get('resolution_notes', '')) > 20) or
               (inc.get('description') and len(inc.get('description', '')) > 30)
        ]
        
        if not valid_incidents:
            logger.warning("No incidents with resolutions or descriptions to add")
            return 0
        
        try:
            # Prepare batch data
            ids = []
            embeddings = []
            documents = []
            metadatas = []
            
            for incident in valid_incidents:
                # Create text for embedding
                text = self._create_embedding_text(incident)
                
                # Generate embedding
                embedding = self.embedding_model.encode(text).tolist()
                
                # Use resolution if available, otherwise use description
                resolution_text = incident.get('resolution_notes', '')
                if not resolution_text or len(resolution_text) < 20:
                    resolution_text = incident.get('description', 'No resolution available')
                
                # Prepare data
                ids.append(incident.get('number', f"INC_{id(incident)}"))
                embeddings.append(embedding)
                documents.append(resolution_text)
                metadatas.append({
                    "number": incident.get('number', 'Unknown'),
                    "category": incident.get('category', 'Unknown'),
                    "short_description": incident.get('short_description', '')[:500],
                    "priority": str(incident.get('priority', '3')),
                    "has_resolution": 'yes' if incident.get('resolution_notes') else 'no'
                })
            
            # Add to collection in smaller batches to avoid timeout
            batch_size = 500
            total_added = 0
            
            for i in range(0, len(ids), batch_size):
                batch_end = min(i + batch_size, len(ids))
                self.collection.add(
                    ids=ids[i:batch_end],
                    embeddings=embeddings[i:batch_end],
                    documents=documents[i:batch_end],
                    metadatas=metadatas[i:batch_end]
                )
                total_added += (batch_end - i)
                logger.info(f"Added batch {i//batch_size + 1}: {total_added}/{len(ids)} incidents")
            
            logger.info(f"Successfully added {len(valid_incidents)} incidents to ChromaDB")
            return len(valid_incidents)
            
        except Exception as e:
            logger.error(f"Error in bulk add: {e}")
            # Try adding one by one if bulk fails
            count = 0
            for incident in valid_incidents:
                if self.add_incident(incident):
                    count += 1
            return count
    
    def search_similar(
        self,
        problem_description: str,
        category: str = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Search for similar incidents using semantic search
        
        Args:
            problem_description: Current problem description
            category: Optional category filter
            top_k: Number of results to return
            
        Returns:
            List of similar incidents with metadata and similarity scores
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(problem_description).tolist()
            
            # Prepare where filter for category
            where_filter = None
            if category:
                where_filter = {"category": category}
            
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter
            )
            
            # Format results
            similar_incidents = []
            if results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    similar_incidents.append({
                        'number': results['metadatas'][0][i].get('number', 'Unknown'),
                        'category': results['metadatas'][0][i].get('category', 'Unknown'),
                        'short_description': results['metadatas'][0][i].get('short_description', ''),
                        'resolution_notes': results['documents'][0][i],
                        'similarity_score': 1 - results['distances'][0][i],  # Convert distance to similarity
                        'distance': results['distances'][0][i]
                    })
            
            return similar_incidents
            
        except Exception as e:
            logger.error(f"Error searching ChromaDB: {e}")
            return []
    
    def update_incident(self, incident: Dict) -> bool:
        """
        Update an existing incident in ChromaDB
        
        Args:
            incident: Updated incident dictionary
            
        Returns:
            True if successful
        """
        try:
            incident_id = incident.get('number')
            if not incident_id:
                return False
            
            # Delete existing
            self.collection.delete(ids=[incident_id])
            
            # Add updated version
            return self.add_incident(incident)
            
        except Exception as e:
            logger.error(f"Error updating incident: {e}")
            return False
    
    def delete_incident(self, incident_number: str) -> bool:
        """
        Delete an incident from ChromaDB
        
        Args:
            incident_number: Incident number to delete
            
        Returns:
            True if successful
        """
        try:
            self.collection.delete(ids=[incident_number])
            logger.info(f"Deleted incident {incident_number} from ChromaDB")
            return True
        except Exception as e:
            logger.error(f"Error deleting incident: {e}")
            return False
    
    def get_count(self) -> int:
        """
        Get total number of incidents in ChromaDB
        
        Returns:
            Count of incidents
        """
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Error getting count: {e}")
            return 0
    
    def clear_collection(self) -> bool:
        """
        Clear all data from the collection
        
        Returns:
            True if successful
        """
        try:
            # Delete and recreate collection
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Incident resolution embeddings for RAG"}
            )
            logger.info(f"Cleared collection: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            return False
    
    def _create_embedding_text(self, incident: Dict) -> str:
        """
        Create text for embedding from incident
        
        Args:
            incident: Incident dictionary
            
        Returns:
            Combined text for embedding
        """
        parts = [
            incident.get('short_description', ''),
            incident.get('description', ''),
            incident.get('category', '')
        ]
        return " ".join([p for p in parts if p])


def get_chromadb_client(
    collection_name: str = "incident_resolutions",
    persist_directory: str = None
) -> ChromaDBClient:
    """
    Factory function to get ChromaDB client
    
    Args:
        collection_name: Name of the collection
        persist_directory: Directory to store ChromaDB data
        
    Returns:
        ChromaDBClient instance
    """
    return ChromaDBClient(
        collection_name=collection_name,
        persist_directory=persist_directory
    )
