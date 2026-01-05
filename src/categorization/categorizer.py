"""
Incident Categorization Module

Uses ML to group incidents based on similar resolutions.
"""

from typing import List, Dict, Tuple
import numpy as np
from sklearn.cluster import HDBSCAN
from sklearn.preprocessing import normalize
from sentence_transformers import SentenceTransformer
from loguru import logger


class IncidentCategorizer:
    """Categorizes incidents using machine learning"""
    
    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        min_cluster_size: int = 5,
        min_samples: int = 3,
        similarity_threshold: float = 0.75
    ):
        """
        Initialize incident categorizer
        
        Args:
            embedding_model: Name of sentence transformer model
            min_cluster_size: Minimum size for a cluster
            min_samples: Minimum samples for core points
            similarity_threshold: Threshold for similarity matching
        """
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples
        self.similarity_threshold = similarity_threshold
        
        logger.info(f"Loading embedding model: {embedding_model}")
        self.model = SentenceTransformer(embedding_model)
        
        self.clusterer = None
        self.embeddings = None
        self.incidents = None
        
    def categorize_incidents(self, incidents: List[Dict]) -> Dict[int, List[Dict]]:
        """
        Categorize incidents into clusters
        
        Args:
            incidents: List of validated incidents
            
        Returns:
            Dictionary mapping cluster_id to list of incidents
        """
        logger.info(f"Categorizing {len(incidents)} incidents")
        
        if not incidents:
            logger.warning("No incidents to categorize")
            return {}
        
        self.incidents = incidents
        
        # Extract text features for clustering
        texts = self._extract_features(incidents)
        
        # Generate embeddings
        logger.info("Generating embeddings...")
        self.embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Normalize embeddings
        self.embeddings = normalize(self.embeddings)
        
        # Perform clustering
        logger.info("Clustering incidents...")
        self.clusterer = HDBSCAN(
            min_cluster_size=self.min_cluster_size,
            min_samples=self.min_samples,
            metric='cosine',
            cluster_selection_method='eom'
        )
        
        labels = self.clusterer.fit_predict(self.embeddings)
        
        # Group incidents by cluster
        clusters = {}
        noise_count = 0
        
        for idx, label in enumerate(labels):
            if label == -1:  # Noise point
                noise_count += 1
                continue
            
            if label not in clusters:
                clusters[label] = []
            
            clusters[label].append(incidents[idx])
        
        logger.info(
            f"Created {len(clusters)} clusters. "
            f"Noise points: {noise_count} ({noise_count/len(incidents)*100:.1f}%)"
        )
        
        return clusters
    
    def _extract_features(self, incidents: List[Dict]) -> List[str]:
        """
        Extract text features from incidents for embedding
        
        Args:
            incidents: List of incidents
            
        Returns:
            List of text strings for embedding
        """
        texts = []
        
        for incident in incidents:
            # Combine relevant fields
            parts = []
            
            # Short description (problem statement)
            short_desc = incident.get("short_description", "")
            if short_desc:
                parts.append(f"Problem: {short_desc}")
            
            # Description (details)
            desc = incident.get("description", "")
            if desc:
                parts.append(f"Details: {desc}")
            
            # Resolution notes (solution)
            resolution = (
                incident.get("resolution_notes", "") or
                incident.get("close_notes", "")
            )
            if resolution:
                parts.append(f"Resolution: {resolution}")
            
            # Category information
            category = incident.get("category", "")
            subcategory = incident.get("subcategory", "")
            if category:
                parts.append(f"Category: {category}")
            if subcategory:
                parts.append(f"Subcategory: {subcategory}")
            
            # Combine all parts
            text = " | ".join(parts) if parts else "Unknown incident"
            texts.append(text)
        
        return texts
    
    def analyze_cluster(self, cluster_id: int, incidents: List[Dict]) -> Dict:
        """
        Analyze a cluster to extract common patterns
        
        Args:
            cluster_id: ID of the cluster
            incidents: Incidents in the cluster
            
        Returns:
            Analysis dictionary with common patterns
        """
        logger.info(f"Analyzing cluster {cluster_id} with {len(incidents)} incidents")
        
        # Extract common categories
        categories = [inc.get("category", "") for inc in incidents if inc.get("category")]
        category_counts = {}
        for cat in categories:
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        # Extract common keywords from resolutions
        resolutions = []
        for inc in incidents:
            res = inc.get("resolution_notes", "") or inc.get("close_notes", "")
            if res:
                resolutions.append(res)
        
        # Find common resolution patterns
        common_patterns = self._extract_common_patterns(resolutions)
        
        # Get representative incident (closest to centroid)
        representative = self._get_representative_incident(cluster_id, incidents)
        
        analysis = {
            "cluster_id": cluster_id,
            "incident_count": len(incidents),
            "common_categories": dict(sorted(
                category_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )),
            "common_patterns": common_patterns,
            "representative_incident": representative.get("number") if representative else None,
            "priority_distribution": self._get_priority_distribution(incidents),
            "avg_resolution_time": self._calculate_avg_resolution_time(incidents)
        }
        
        return analysis
    
    def _extract_common_patterns(self, texts: List[str], top_n: int = 10) -> List[str]:
        """Extract common patterns from text"""
        # Simple approach: find common words/phrases
        # In production, use more sophisticated NLP
        
        word_freq = {}
        for text in texts:
            words = text.lower().split()
            for word in words:
                if len(word) > 4:  # Filter short words
                    word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top patterns
        sorted_patterns = sorted(
            word_freq.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [pattern for pattern, _ in sorted_patterns[:top_n]]
    
    def _get_representative_incident(
        self,
        cluster_id: int,
        incidents: List[Dict]
    ) -> Dict:
        """Get the incident closest to cluster centroid"""
        if not incidents or self.embeddings is None:
            return {}
        
        # Get indices of incidents in this cluster
        indices = []
        for i, inc in enumerate(self.incidents):
            if inc in incidents:
                indices.append(i)
        
        if not indices:
            return incidents[0] if incidents else {}
        
        # Calculate centroid
        cluster_embeddings = self.embeddings[indices]
        centroid = np.mean(cluster_embeddings, axis=0)
        
        # Find closest incident
        similarities = np.dot(cluster_embeddings, centroid)
        closest_idx = np.argmax(similarities)
        
        return incidents[closest_idx]
    
    def _get_priority_distribution(self, incidents: List[Dict]) -> Dict[str, int]:
        """Get distribution of priorities"""
        priorities = {}
        for inc in incidents:
            priority = inc.get("priority", "Unknown")
            priorities[str(priority)] = priorities.get(str(priority), 0) + 1
        return priorities
    
    def _calculate_avg_resolution_time(self, incidents: List[Dict]) -> float:
        """Calculate average resolution time in hours"""
        from datetime import datetime
        
        times = []
        for inc in incidents:
            created = inc.get("sys_created_on")
            resolved = inc.get("resolved_at") or inc.get("closed_at")
            
            if created and resolved:
                try:
                    created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    resolved_dt = datetime.fromisoformat(resolved.replace("Z", "+00:00"))
                    diff = (resolved_dt - created_dt).total_seconds() / 3600
                    times.append(diff)
                except:
                    continue
        
        return sum(times) / len(times) if times else 0.0


def create_categorizer_from_config(config: Dict) -> IncidentCategorizer:
    """Create categorizer from configuration"""
    cat_config = config.get("categorization", {})
    
    return IncidentCategorizer(
        embedding_model=cat_config.get("embedding_model", "all-MiniLM-L6-v2"),
        min_cluster_size=cat_config.get("min_cluster_size", 5),
        min_samples=cat_config.get("min_samples", 3),
        similarity_threshold=cat_config.get("similarity_threshold", 0.75)
    )
