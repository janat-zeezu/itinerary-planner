"""
Embedding models for representing attractions semantically
"""

import numpy as np
from abc import ABC, abstractmethod
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer

class BaseEmbeddingModel(ABC):
    """Abstract base class for embedding models."""
    
    @abstractmethod
    def get_embeddings(self, texts):
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts (list): List of strings to embed
            
        Returns:
            numpy.ndarray: Array of embeddings, one per input text
        """
        pass


class TransformerEmbeddingModel(BaseEmbeddingModel):
    """Embedding model using sentence transformers."""
    
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initialize the transformer model.
        
        Args:
            model_name (str): Name of the sentence transformer model to use
        """
        print(f"Loading transformer model: {model_name}")
        try:
            self.model = SentenceTransformer(model_name)
            print(f"Successfully loaded model {model_name}")
        except Exception as e:
            print(f"Failed to load transformer model: {e}")
            print("Falling back to simple embedding model")
            # Fallback to simple model if transformer fails
            self.model = None
    
    def get_embeddings(self, texts):
        """
        Generate embeddings using the transformer model.
        
        Args:
            texts (list): List of texts to embed
            
        Returns:
            numpy.ndarray: Array of embeddings
        """
        if self.model is None:
            # Fallback to simple embedding if model failed to load
            return SimpleEmbeddingModel().get_embeddings(texts)
        
        try:
            # Generate embeddings using the transformer model
            embeddings = self.model.encode(texts, show_progress_bar=False)
            return embeddings
        except Exception as e:
            print(f"Error generating transformer embeddings: {e}")
            # Fallback to simple embedding if embedding fails
            return SimpleEmbeddingModel().get_embeddings(texts)


class SimpleEmbeddingModel(BaseEmbeddingModel):
    """Simple embedding model using TF-IDF."""
    
    def __init__(self):
        """Initialize the TF-IDF vectorizer."""
        self.vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    def get_embeddings(self, texts):
        """
        Generate embeddings using TF-IDF.
        
        Args:
            texts (list): List of texts to embed
            
        Returns:
            numpy.ndarray: Array of embeddings
        """
        if not texts:
            return np.array([])
        
        # Fit and transform the texts to TF-IDF vectors
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        
        # Convert sparse matrix to dense and normalize
        embeddings = tfidf_matrix.toarray()
        
        # Normalize embeddings
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        normalized_embeddings = embeddings / norms
        
        return normalized_embeddings