"""
RAG-based Resolution Finder
Retrieves similar past incidents and suggests resolutions using ChromaDB
"""

import numpy as np
from pathlib import Path
import json
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import sys

# Import ChromaDB client conditionally
try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from database.chromadb_client import ChromaDBClient
    CHROMADB_AVAILABLE = True
except Exception as e:
    print(f"[WARNING] ChromaDB not available: {e}")
    ChromaDBClient = None
    CHROMADB_AVAILABLE = False


class ResolutionFinder:
    """Find resolutions from past incidents using RAG with ChromaDB"""
    
    def __init__(
        self, 
        embedding_model: str = "all-MiniLM-L6-v2",
        use_chromadb: bool = True,
        chromadb_persist_dir: str = None
    ):
        """
        Initialize resolution finder with embeddings model
        
        Args:
            embedding_model: Name of sentence transformer model
            use_chromadb: Whether to use ChromaDB (True) or in-memory (False)
            chromadb_persist_dir: Directory to persist ChromaDB data
        """
        self.model = SentenceTransformer(embedding_model)
        self.use_chromadb = use_chromadb
        
        # Legacy in-memory storage (fallback)
        self.knowledge_base = []
        self.embeddings_cache = []
        self.kb_file_path = Path(__file__).parent.parent.parent / 'data' / 'knowledge_base.json'
        
        # Initialize ChromaDB if enabled
        self.chroma_client = None
        if use_chromadb and CHROMADB_AVAILABLE and ChromaDBClient:
            try:
                self.chroma_client = ChromaDBClient(
                    collection_name="incident_resolutions",
                    persist_directory=chromadb_persist_dir,
                    embedding_model=embedding_model
                )
                print(f"[INFO] ChromaDB initialized successfully with {self.chroma_client.get_count()} incidents")
            except Exception as e:
                print(f"[WARNING] Failed to initialize ChromaDB: {e}")
                print("[INFO] Falling back to in-memory storage")
                self.use_chromadb = False
        elif use_chromadb and not CHROMADB_AVAILABLE:
            print("[WARNING] ChromaDB requested but not available. Using in-memory storage.")
            self.use_chromadb = False
        
    def load_knowledge_base(self, incidents: List[Dict]) -> None:
        """
        Load past incidents into knowledge base
        
        Args:
            incidents: List of resolved incidents with resolution notes
        """
        # Filter incidents that have resolutions OR good descriptions
        valid_incidents = [
            inc for inc in incidents 
            if (inc.get('resolution_notes') and len(inc.get('resolution_notes', '')) > 20) or
               (inc.get('description') and len(inc.get('description', '')) > 30)
        ]
        
        if self.use_chromadb and self.chroma_client:
            # Use ChromaDB for storage
            print(f"[INFO] Adding {len(valid_incidents)} incidents to ChromaDB...")
            added_count = self.chroma_client.add_incidents_bulk(valid_incidents)
            print(f"[INFO] Successfully added {added_count} incidents to ChromaDB")
        else:
            # Use in-memory storage (legacy)
            self.knowledge_base = valid_incidents
            
            if valid_incidents:
                # Create embeddings for quick retrieval
                texts = [
                    f"{inc.get('short_description', '')} {inc.get('description', '')} {inc.get('category', '')}"
                    for inc in valid_incidents
                ]
                self.embeddings_cache = self.model.encode(texts, convert_to_numpy=True)
                print(f"[INFO] Loaded {len(valid_incidents)} incidents into in-memory storage")
    
    def find_similar_incidents(self, 
                              problem_description: str, 
                              category: str = None,
                              top_k: int = 5,
                              min_similarity: float = 0.5) -> List[Dict]:
        """
        Find similar past incidents using semantic search
        
        Args:
            problem_description: Current problem description
            category: Optional category filter
            top_k: Number of similar incidents to return
            min_similarity: Minimum similarity threshold (0-1)
            
        Returns:
            List of similar incidents with similarity scores
        """
        if self.use_chromadb and self.chroma_client:
            # Use ChromaDB for search
            results = self.chroma_client.search_similar(
                problem_description=problem_description,
                category=category,
                top_k=top_k
            )
            
            # Filter by minimum similarity
            filtered_results = [
                inc for inc in results 
                if inc.get('similarity_score', 0) >= min_similarity
            ]
            
            return filtered_results
        else:
            # Use in-memory search (legacy)
            if not self.knowledge_base:
                return []
            
            # Create embedding for current problem
            query_embedding = self.model.encode([problem_description], convert_to_numpy=True)
            
            # Calculate similarities
            similarities = cosine_similarity(query_embedding, self.embeddings_cache)[0]
            
            # Get top matches
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                similarity = float(similarities[idx])
                if similarity >= min_similarity:
                    incident = self.knowledge_base[idx].copy()
                    incident['similarity_score'] = similarity
                    
                    # Filter by category if specified
                    if category is None or incident.get('category', '').lower() == category.lower():
                        results.append(incident)
            
            return results
    
    def suggest_resolution(self, 
                          problem_description: str,
                          category: str = None,
                          symptoms: str = None) -> Dict:
        """
        Suggest resolution based on similar past incidents
        
        Args:
            problem_description: Description of current problem
            category: Problem category
            symptoms: Additional symptoms/details
            
        Returns:
            Dict with suggested resolution and source incidents
        """
        # Combine all available information
        full_description = problem_description
        if symptoms:
            full_description += " " + symptoms
        if category:
            full_description += " " + category
        
        # Find similar incidents
        similar_incidents = self.find_similar_incidents(
            full_description, 
            category=category,
            top_k=5,
            min_similarity=0.3  # Lowered threshold for better matches
        )
        
        if not similar_incidents:
            return {
                'success': False,
                'message': 'No similar past incidents found',
                'suggested_resolution': None,
                'source_incidents': []
            }
        
        # Extract resolutions from top matches
        resolutions = []
        for inc in similar_incidents:
            resolution_text = inc.get('resolution_notes', '')
            if not resolution_text or len(resolution_text) < 20:
                # Use description as fallback if no resolution
                resolution_text = f"Similar incident found: {inc.get('description', 'No details available')}"
            
            resolutions.append({
                'incident_number': inc.get('number', 'Unknown'),
                'resolution': resolution_text,
                'similarity': inc['similarity_score'],
                'category': inc.get('category', 'Unknown'),
                'has_resolution': bool(inc.get('resolution_notes'))
            })
        
        # Create combined resolution suggestion
        top_match = similar_incidents[0]
        suggested_resolution = self._create_combined_resolution(similar_incidents)
        
        return {
            'success': True,
            'suggested_resolution': suggested_resolution,
            'primary_source': {
                'incident': top_match.get('number', 'Unknown'),
                'similarity': top_match['similarity_score'],
                'resolution': resolutions[0]['resolution']
            },
            'alternative_resolutions': resolutions[1:4],  # Top 3 alternatives
            'confidence': top_match['similarity_score']
        }
    
    def _create_combined_resolution(self, incidents: List[Dict]) -> str:
        """
        Create a combined resolution from multiple similar incidents
        
        Args:
            incidents: List of similar incidents
            
        Returns:
            Combined resolution text
        """
        if not incidents:
            return ""
        
        # Use the highest similarity incident as base
        base_resolution = incidents[0].get('resolution_notes', '')
        
        # If we have multiple very similar incidents, note that
        if len(incidents) > 1 and incidents[1]['similarity_score'] > 0.8:
            additional_note = f"\n\n[Note: Based on {len(incidents)} similar resolved incidents]"
            return base_resolution + additional_note
        
        return base_resolution
    
    def load_from_file(self, file_path: str) -> bool:
        """
        Load knowledge base from JSON file
        
        Args:
            file_path: Path to JSON file with incidents
            
        Returns:
            True if successful
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                incidents = json.load(f)
            
            if isinstance(incidents, list):
                self.load_knowledge_base(incidents)
                return True
            else:
                print(f"[ERROR] Invalid format in {file_path}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Failed to load knowledge base: {e}")
            return False
    
    def add_to_knowledge_base(self, incident: Dict) -> None:
        """
        Add a single incident to knowledge base and save
        
        Args:
            incident: Incident with resolution to add
        """
        if incident.get('resolution_notes') and len(incident.get('resolution_notes', '')) > 20:
            if self.use_chromadb and self.chroma_client:
                # Add to ChromaDB
                success = self.chroma_client.add_incident(incident)
                if success:
                    print(f"[INFO] Added incident {incident.get('number', 'Unknown')} to ChromaDB")
                else:
                    print(f"[WARNING] Failed to add incident {incident.get('number', 'Unknown')} to ChromaDB")
            else:
                # Add to in-memory storage (legacy)
                self.knowledge_base.append(incident)
                
                # Update embeddings
                text = f"{incident.get('short_description', '')} {incident.get('description', '')} {incident.get('category', '')}"
                new_embedding = self.model.encode([text], convert_to_numpy=True)
                
                if len(self.embeddings_cache) == 0:
                    self.embeddings_cache = new_embedding
                else:
                    self.embeddings_cache = np.vstack([self.embeddings_cache, new_embedding])
                
                # Save to JSON file
                try:
                    # Load existing knowledge base from file
                    if self.kb_file_path.exists():
                        with open(self.kb_file_path, 'r', encoding='utf-8') as f:
                            kb_data = json.load(f)
                    else:
                        kb_data = []
                    
                    # Add new incident if not already present
                    incident_numbers = [inc.get('number') for inc in kb_data]
                    if incident.get('number') not in incident_numbers:
                        kb_data.append(incident)
                        
                        # Save back to file
                        with open(self.kb_file_path, 'w', encoding='utf-8') as f:
                            json.dump(kb_data, f, indent=2, ensure_ascii=False)
                        
                        print(f"[INFO] Added incident {incident.get('number', 'Unknown')} to knowledge base and saved to file")
                    else:
                        print(f"[INFO] Incident {incident.get('number', 'Unknown')} already exists in knowledge base file")
                        
                except Exception as e:
                    print(f"[ERROR] Failed to save to knowledge base file: {str(e)}")
                    # Still keep in memory even if file save fails


def create_resolution_finder(config: Optional[Dict] = None) -> ResolutionFinder:
    """
    Factory function to create resolution finder
    
    Args:
        config: Optional configuration dict
        
    Returns:
        ResolutionFinder instance
    """
    embedding_model = config.get('embedding_model', 'all-MiniLM-L6-v2') if config else 'all-MiniLM-L6-v2'
    return ResolutionFinder(embedding_model=embedding_model)
