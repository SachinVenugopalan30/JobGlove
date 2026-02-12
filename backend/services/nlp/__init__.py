"""NLP module for resume parsing, analysis, and scoring."""

from .entity_extractor import extract_all_entities
from .local_scorer import score_resume_against_job
from .resume_parser import clean_text, extract_text, extract_text_from_docx, extract_text_from_pdf
from .skill_extractor import (
    calculate_keyword_match,
    extract_keywords_from_job_description,
    extract_keywords_from_resume,
)
from .text_analyzer import analyze_text_quality, calculate_text_similarity, check_ats_compatibility

__all__ = [
    'extract_text',
    'extract_text_from_docx',
    'extract_text_from_pdf',
    'clean_text',
    'extract_all_entities',
    'extract_keywords_from_job_description',
    'extract_keywords_from_resume',
    'calculate_keyword_match',
    'calculate_text_similarity',
    'check_ats_compatibility',
    'analyze_text_quality',
    'score_resume_against_job'
]
