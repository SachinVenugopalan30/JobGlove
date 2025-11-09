"""
Embedding Manager for Resume-Job Description Matching

This module provides embedding-based similarity scoring using sentence transformers,
following the architecture pattern from the Resume Matcher project.
"""

import re
from typing import List, Tuple, Dict, Any
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from utils.logger import app_logger

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    app_logger.warning("sentence-transformers not installed. Embedding-based scoring will be unavailable.")


class EmbeddingManager:
    """
    Manages embeddings for resume and job description matching.
    Uses sentence transformers for semantic similarity.
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the embedding manager.
        
        Args:
            model_name: Name of the sentence-transformer model to use.
                       'all-MiniLM-L6-v2' is lightweight and fast (default).
                       'all-mpnet-base-v2' provides better quality but slower.
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers is required for embedding-based scoring. "
                "Install it with: pip install sentence-transformers"
            )
        
        try:
            self.model = SentenceTransformer(model_name)
            self.model_name = model_name
            app_logger.info(f"EmbeddingManager initialized with model: {model_name}")
        except Exception as e:
            app_logger.error(f"Failed to load sentence-transformer model: {e}")
            raise
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding vector for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            Numpy array representing the text embedding
        """
        try:
            if not text or not text.strip():
                app_logger.warning("Empty text provided for embedding generation")
                return np.zeros(self.model.get_sentence_embedding_dimension())
            
            # Clean the text
            cleaned_text = self._clean_text(text)
            
            # Generate embedding
            embedding = self.model.encode(cleaned_text, convert_to_numpy=True)
            
            return embedding
            
        except Exception as e:
            app_logger.error(f"Error generating embedding: {e}")
            return np.zeros(self.model.get_sentence_embedding_dimension())
    
    def generate_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts efficiently.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            2D numpy array where each row is an embedding
        """
        try:
            if not texts:
                return np.array([])
            
            # Clean all texts
            cleaned_texts = [self._clean_text(text) for text in texts]
            
            # Generate embeddings in batch (more efficient)
            embeddings = self.model.encode(cleaned_texts, convert_to_numpy=True, show_progress_bar=False)
            
            return embeddings
            
        except Exception as e:
            app_logger.error(f"Error generating batch embeddings: {e}")
            return np.array([])
    
    def calculate_embedding_similarity(
        self, 
        resume_text: str, 
        job_description: str
    ) -> float:
        """
        Calculate semantic similarity between resume and job description using embeddings.
        This provides a more semantic understanding compared to keyword-based TF-IDF.
        
        Args:
            resume_text: The resume content
            job_description: The job description content
            
        Returns:
            Similarity score as percentage (0-100)
        """
        try:
            # Generate embeddings
            resume_embedding = self.generate_embedding(resume_text)
            jd_embedding = self.generate_embedding(job_description)
            
            # Reshape for cosine_similarity
            resume_embedding = resume_embedding.reshape(1, -1)
            jd_embedding = jd_embedding.reshape(1, -1)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(resume_embedding, jd_embedding)[0][0]
            
            # Convert to percentage
            similarity_percentage = round(float(similarity) * 100, 2)
            
            app_logger.info(f"Embedding-based similarity calculated: {similarity_percentage}%")
            return similarity_percentage
            
        except Exception as e:
            app_logger.error(f"Error calculating embedding similarity: {e}")
            return 0.0
    
    def calculate_section_similarities(
        self,
        resume_sections: Dict[str, str],
        job_description: str
    ) -> Dict[str, float]:
        """
        Calculate similarity scores for individual resume sections.
        Useful for identifying which sections are well-aligned with the job.
        
        Args:
            resume_sections: Dictionary mapping section names to their content
            job_description: The job description
            
        Returns:
            Dictionary mapping section names to similarity scores (0-100)
        """
        try:
            jd_embedding = self.generate_embedding(job_description)
            section_scores = {}
            
            for section_name, section_content in resume_sections.items():
                if not section_content or not section_content.strip():
                    section_scores[section_name] = 0.0
                    continue
                
                section_embedding = self.generate_embedding(section_content)
                
                # Calculate similarity
                similarity = cosine_similarity(
                    section_embedding.reshape(1, -1),
                    jd_embedding.reshape(1, -1)
                )[0][0]
                
                section_scores[section_name] = round(float(similarity) * 100, 2)
            
            app_logger.info(f"Section similarities calculated: {section_scores}")
            return section_scores
            
        except Exception as e:
            app_logger.error(f"Error calculating section similarities: {e}")
            return {}
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Clean text for embedding generation.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s\.\,\-\(\)\/\+\#]', '', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text


# Singleton instance for reuse
_embedding_manager_instance = None


def get_embedding_manager(model_name: str = 'all-MiniLM-L6-v2') -> EmbeddingManager:
    """
    Get or create a singleton EmbeddingManager instance.
    Reusing the model instance saves memory and initialization time.
    
    Args:
        model_name: Sentence-transformer model name
        
    Returns:
        EmbeddingManager instance
    """
    global _embedding_manager_instance
    
    if _embedding_manager_instance is None:
        _embedding_manager_instance = EmbeddingManager(model_name)
    
    return _embedding_manager_instance
