"""NLP module for resume parsing, analysis, and scoring."""

from .resume_parser import extract_text, extract_text_from_docx, extract_text_from_pdf, clean_text
from .entity_extractor import extract_all_entities
from .skill_extractor import extract_keywords_from_job_description, extract_keywords_from_resume, calculate_keyword_match
from .text_analyzer import calculate_text_similarity, check_ats_compatibility, analyze_text_quality
from .local_scorer import score_resume_against_job

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
