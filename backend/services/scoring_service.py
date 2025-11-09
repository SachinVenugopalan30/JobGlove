import json
from typing import Dict, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from services.ai_service import AIProvider
from utils.logger import app_logger

# Import new modules (optional dependencies)
try:
    from services.embedding_manager import get_embedding_manager
    from services.ats_recommendations import ATSRecommendationEngine
    ENHANCED_SCORING_AVAILABLE = True
except ImportError as e:
    ENHANCED_SCORING_AVAILABLE = False
    app_logger.warning(f"Enhanced scoring modules not available: {e}")


def calculate_cosine_similarity(resume_text: str, job_description: str) -> float:
    """
    Calculate cosine similarity between resume and job description using TF-IDF vectorization.
    
    Args:
        resume_text: The resume text content
        job_description: The job description text
        
    Returns:
        Similarity score as a percentage (0-100)
    """
    try:
        # Preprocess: Remove extra whitespace and ensure non-empty strings
        resume_cleaned = ' '.join(resume_text.strip().split())
        jd_cleaned = ' '.join(job_description.strip().split())
        
        if not resume_cleaned or not jd_cleaned:
            app_logger.warning("Empty resume or job description provided for similarity calculation")
            return 0.0
        
        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            max_features=1000,  # Limit features for performance
            ngram_range=(1, 2)  # Use unigrams and bigrams
        )
        
        # Fit and transform both texts
        tfidf_matrix = vectorizer.fit_transform([resume_cleaned, jd_cleaned])
        
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        # Convert to percentage and round
        similarity_percentage = round(similarity * 100, 2)
        
        app_logger.info(f"Cosine similarity calculated: {similarity_percentage}%")
        return similarity_percentage
        
    except Exception as e:
        app_logger.error(f"Error calculating cosine similarity: {e}")
        return 0.0


def calculate_embedding_similarity(resume_text: str, job_description: str) -> float:
    """
    Calculate semantic similarity using embeddings (if available).
    Falls back to 0 if sentence-transformers is not installed.
    
    Args:
        resume_text: The resume content
        job_description: The job description
        
    Returns:
        Similarity score as percentage (0-100)
    """
    if not ENHANCED_SCORING_AVAILABLE:
        app_logger.warning("Embedding-based scoring not available. Install sentence-transformers.")
        return 0.0
    
    try:
        embedding_manager = get_embedding_manager()
        similarity = embedding_manager.calculate_embedding_similarity(resume_text, job_description)
        return similarity
    except Exception as e:
        app_logger.error(f"Error calculating embedding similarity: {e}")
        return 0.0


def generate_ats_recommendations(
    resume_text: str,
    job_description: str,
    embedding_similarity: float = None,
    tfidf_similarity: float = None
) -> dict:
    """
    Generate comprehensive ATS recommendations.
    
    Args:
        resume_text: The resume content
        job_description: The job description
        embedding_similarity: Optional embedding similarity score
        tfidf_similarity: Optional TF-IDF similarity score
        
    Returns:
        Dictionary containing ATS score and recommendations
    """
    if not ENHANCED_SCORING_AVAILABLE:
        app_logger.warning("ATS recommendations not available")
        return {
            'ats_score': 0.0,
            'recommendations': [{
                'priority': 'high',
                'title': 'Enhanced Scoring Unavailable',
                'description': 'Install required packages for ATS analysis'
            }]
        }
    
    try:
        engine = ATSRecommendationEngine()
        recommendations = engine.generate_recommendations(
            resume_text,
            job_description,
            embedding_similarity,
            tfidf_similarity
        )
        return recommendations
    except Exception as e:
        app_logger.error(f"Error generating ATS recommendations: {e}")
        return {'ats_score': 0.0, 'recommendations': []}


SCORING_PROMPT_TEMPLATE = """
You are an expert resume analyst and career coach. Analyze the following resume against the job description and provide a detailed scoring breakdown.

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

Provide a scoring analysis in the following JSON format:
{{
  "ats_score": <number 0-20>,
  "ats_feedback": "<detailed feedback on ATS readability, formatting, keyword usage, parseability>",
  "content_score": <number 0-20>,
  "content_feedback": "<detailed feedback on relevance, achievements, quantification, clarity>",
  "style_score": <number 0-25>,
  "style_feedback": "<detailed feedback on action verbs, conciseness, consistency, professionalism>",
  "match_score": <number 0-25>,
  "match_feedback": "<detailed feedback on alignment with job requirements, relevant skills, experience match>",
  "readiness_score": <number 0-10>,
  "readiness_feedback": "<detailed feedback on overall polish, completeness, competitive strength>"
}}

Scoring Guidelines:
1. ATS Readability (0-20): Assess formatting consistency, keyword presence, structure clarity, and parseability by ATS systems
2. Content Quality (0-20): Evaluate relevance of experience, achievement impact, use of metrics/numbers, and clarity
3. Writing Style (0-25): Analyze use of strong action verbs, conciseness, consistency, and professional tone
4. Job Match (0-25): Compare resume against specific job requirements, required skills, and relevant experience
5. Readiness Score (0-10): Overall assessment of whether the resume is competitive and ready for submission

Be objective and constructive in your feedback. Highlight both strengths and areas for improvement.
Return ONLY the JSON object, no additional text.
"""

class ScoringService:
    def __init__(self, ai_provider: AIProvider):
        self.ai_provider = ai_provider
        app_logger.info(f"ScoringService initialized with {ai_provider.__class__.__name__}")

    def score_resume(self, resume_text: str, job_description: str) -> dict:
        try:
            prompt = SCORING_PROMPT_TEMPLATE.format(
                job_description=job_description,
                resume_text=resume_text
            )

            app_logger.info("Requesting resume scoring from AI")
            response = self.ai_provider.generate(prompt)

            response_text = response.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            scores = json.loads(response_text)

            total_score = (
                scores.get('ats_score', 0) +
                scores.get('content_score', 0) +
                scores.get('style_score', 0) +
                scores.get('match_score', 0) +
                scores.get('readiness_score', 0)
            )
            scores['total_score'] = round(total_score, 1)

            app_logger.info(f"Resume scored successfully. Total: {scores['total_score']}/100")
            return scores

        except json.JSONDecodeError as e:
            app_logger.error(f"Failed to parse AI scoring response as JSON: {e}")
            app_logger.error(f"Response was: {response[:500] if len(response) > 500 else response}")
            return self._fallback_score(f"Failed to parse AI response: {str(e)}")
        except Exception as e:
            app_logger.error(f"Error during resume scoring: {e}")
            return self._fallback_score(str(e))

    def _fallback_score(self, error_message: str) -> dict:
        return {
            'ats_score': 0,
            'ats_feedback': f'Scoring unavailable: {error_message}',
            'content_score': 0,
            'content_feedback': f'Scoring unavailable: {error_message}',
            'style_score': 0,
            'style_feedback': f'Scoring unavailable: {error_message}',
            'match_score': 0,
            'match_feedback': f'Scoring unavailable: {error_message}',
            'readiness_score': 0,
            'readiness_feedback': f'Scoring unavailable: {error_message}',
            'total_score': 0
        }

def create_scoring_service(api_name: str) -> ScoringService:
    provider = AIProvider.create(api_name)
    return ScoringService(provider)
