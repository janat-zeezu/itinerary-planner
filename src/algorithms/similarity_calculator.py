"""
Semantic similarity calculation module
"""

import numpy as np
from tqdm import tqdm

class SemanticSimilarityCalculator:
    """Calculate semantic similarities between attractions."""
    
    def __init__(self, embedding_model):
        """
        Initialize the similarity calculator.
        
        Args:
            embedding_model: Model that implements get_embeddings method
        """
        self.embedding_model = embedding_model
    
    def calculate_similarities(self, cities_data, preferences):
        """
        Calculate similarity matrices for attractions within each city.
        
        Args:
            cities_data (list): List of city dictionaries with attraction data
            preferences (list): User preferences
            
        Returns:
            dict: Dictionary mapping city indices to similarity matrices
        """
        similarity_matrices = {}
        preference_embedding = None
        
        # Create embedding for user preferences
        if preferences:
            preference_text = " ".join(preferences)
            preference_embedding = self.embedding_model.get_embeddings([preference_text])[0]
        
        print("Calculating similarities for each city...")
        for city_idx, city in enumerate(tqdm(cities_data)):
            attractions = city['attractions']
            if not attractions:
                continue
            
            # Get text representations for embeddings
            texts = [attr['text_for_embedding'] for attr in attractions]
            
            # Generate embeddings
            embeddings = self.embedding_model.get_embeddings(texts)
            
            # Calculate similarity matrix
            similarity_matrix = self._calculate_cosine_similarity(embeddings)
            
            # Apply preference weighting if available
            if preference_embedding is not None:
                preference_scores = self._calculate_preference_scores(
                    embeddings, preference_embedding
                )
                similarity_matrix = self._weight_by_preferences(
                    similarity_matrix, preference_scores
                )
            
            similarity_matrices[city_idx] = similarity_matrix
        
        return similarity_matrices
    
    def _calculate_cosine_similarity(self, embeddings):
        """
        Calculate cosine similarity between embeddings.
        
        Args:
            embeddings (numpy.ndarray): Matrix of embeddings
            
        Returns:
            numpy.ndarray: Similarity matrix
        """
        # Normalize the embeddings
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        normalized_embeddings = embeddings / norms
        
        # Calculate dot product for cosine similarity
        similarity_matrix = np.dot(normalized_embeddings, normalized_embeddings.T)
        
        return similarity_matrix
    
    def _calculate_preference_scores(self, embeddings, preference_embedding):
        """
        Calculate similarity scores between attractions and user preferences.
        
        Args:
            embeddings (numpy.ndarray): Attraction embeddings
            preference_embedding (numpy.ndarray): User preference embedding
            
        Returns:
            numpy.ndarray: Array of preference scores
        """
        # Normalize the preference embedding
        pref_norm = np.linalg.norm(preference_embedding)
        if pref_norm > 0:
            normalized_pref = preference_embedding / pref_norm
        else:
            normalized_pref = preference_embedding
        
        # Normalize the attraction embeddings
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        normalized_embeddings = embeddings / norms
        
        # Calculate similarity with preference
        preference_scores = np.dot(normalized_embeddings, normalized_pref)
        
        # Scale to 0-1 range for weighting
        preference_scores = (preference_scores + 1) / 2
        
        return preference_scores
    
    def _weight_by_preferences(self, similarity_matrix, preference_scores, weight=0.5):
        """
        Weight similarity matrix by preference scores.
        
        Args:
            similarity_matrix (numpy.ndarray): Original similarity matrix
            preference_scores (numpy.ndarray): Preference scores for each attraction
            weight (float): Weight to apply to preference scores (0-1)
            
        Returns:
            numpy.ndarray: Weighted similarity matrix
        """
        n = len(similarity_matrix)
        weighted_matrix = similarity_matrix.copy()
        
        # Calculate preference weight matrix
        for i in range(n):
            for j in range(n):
                # Take average of both attractions' preference scores
                pref_factor = (preference_scores[i] + preference_scores[j]) / 2
                
                # Apply weighted adjustment
                weighted_matrix[i, j] = (
                    (1 - weight) * similarity_matrix[i, j] + 
                    weight * pref_factor
                )
        
        return weighted_matrix