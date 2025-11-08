"""Skill and keyword extraction module for dynamic keyword matching."""

import re
from typing import List, Dict, Set
import spacy
from utils.logger import app_logger

nlp = spacy.load('en_core_web_sm')


def extract_technical_terms(text: str) -> List[str]:
    """
    Extract technical terms using POS tagging and NER.

    Args:
        text: Input text

    Returns:
        List of technical terms

    Strategy:
    - Extract proper nouns (PROPN)
    - Extract named entities (PRODUCT, ORG for tech companies/products)
    - Extract acronyms (all caps words 2+ chars)
    - Extract compound nouns
    - Filter out generic proper nouns (months, common names, etc.)
    """
    doc = nlp(text)
    terms = set()
    
    # Generic proper nouns to exclude (common names, places that aren't tech-relevant)
    generic_proper_nouns = {
        'January', 'February', 'March', 'April', 'May', 'June', 'July',
        'August', 'September', 'October', 'November', 'December',
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
        'College', 'University', 'Institute', 'School', 'Academy',
        'Bachelor', 'Master', 'PhD', 'Doctorate',
        'USA', 'America', 'United', 'States',
        'Big', 'Ability', 'Build', 'Connections',
    }

    for token in doc:
        if token.pos_ == 'PROPN' and len(token.text) > 1:
            # Skip generic proper nouns
            if token.text not in generic_proper_nouns:
                terms.add(token.text)

    for ent in doc.ents:
        # Only include PRODUCT and ORG entities (technologies and companies)
        # Skip GPE (geopolitical entities like cities/countries) and NORP (nationalities)
        # as they're usually not relevant to job skills
        if ent.label_ in ['PRODUCT', 'ORG']:
            if ent.text not in generic_proper_nouns:
                terms.add(ent.text)

    # Extract acronyms, but be more selective
    acronym_pattern = r'\b[A-Z]{2,}\b'
    acronyms = re.findall(acronym_pattern, text)
    
    # Filter out common non-technical acronyms
    non_technical_acronyms = {'GPA', 'USA', 'PhD', 'MS', 'BS', 'BA', 'MA'}
    for acronym in acronyms:
        if acronym not in non_technical_acronyms:
            terms.add(acronym)

    return list(terms)


def extract_noun_phrases(text: str) -> List[str]:
    """
    Extract noun phrases from text.

    Args:
        text: Input text

    Returns:
        List of noun phrases
    """
    doc = nlp(text)
    noun_phrases = []
    
    # Generic phrases to exclude (these are too common/generic)
    generic_phrases = {
        'job description', 'work experience', 'team player', 'team member',
        'good communication', 'excellent communication', 'communication skills',
        'united states', 'new york', 'san francisco', 'los angeles',
        'problem solving', 'attention to detail', 'work ethic',
    }
    
    for chunk in doc.noun_chunks:
        # Filter by length
        if len(chunk.text.strip()) < 3:
            continue
        
        # Only extract 2-4 word phrases
        words = chunk.text.split()
        if len(words) < 2 or len(words) > 4:
            continue
        
        # Check if phrase is too generic
        phrase_lower = chunk.text.lower().strip()
        if phrase_lower in generic_phrases:
            continue
            
        # Require technical content: must have proper nouns or uppercase tokens
        # This filters out generic phrases like "job description" while keeping
        # technical terms like "Machine Learning" or "AWS Lambda"
        has_technical = any(
            token.pos_ in ['PROPN', 'NOUN'] and token.text[0].isupper() 
            for token in chunk
        )
        
        if has_technical or any(token.is_upper for token in chunk):
            noun_phrases.append(chunk.text.strip())

    return noun_phrases


def extract_requirements(text: str) -> List[str]:
    """
    Extract requirement statements from job description.

    Args:
        text: Job description text

    Returns:
        List of requirement keywords

    Strategy:
    - Look for patterns like "X years of experience"
    - Look for degree requirements
    - Look for skill requirements
    """
    requirements = []

    experience_pattern = r'(\d+\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp)(?:\s+(?:in|with))?\s+[\w\s]+)'
    experience_matches = re.findall(experience_pattern, text, re.IGNORECASE)
    requirements.extend(experience_matches)

    degree_pattern = r"(Bachelor'?s?|Master'?s?|PhD|Doctorate)(?:\s+(?:degree|in))?\s+[\w\s]+"
    degree_matches = re.findall(degree_pattern, text, re.IGNORECASE)
    requirements.extend(degree_matches)

    return requirements


def normalize_keywords(keywords: List[str]) -> List[str]:
    """
    Normalize keywords by cleaning and deduplicating.

    Args:
        keywords: List of raw keywords

    Returns:
        List of normalized keywords

    Operations:
    - Convert to lowercase
    - Remove duplicates (case-insensitive)
    - Remove very short keywords (< 2 chars)
    - Remove common stopwords and non-skill terms
    - Strip punctuation
    """
    # Common stopwords
    stopwords = {'and', 'or', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'as', 'is', 'are', 'was', 'were', 'be', 'been'}
    
    # Generic non-skill terms to exclude
    exclude_terms = {
        # Months
        'january', 'february', 'march', 'april', 'may', 'june', 'july', 
        'august', 'september', 'october', 'november', 'december',
        'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
        
        # Days
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
        'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun',
        
        # Date suffixes and patterns
        '1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th',
        '11th', '12th', '13th', '14th', '15th', '16th', '17th', '18th', '19th', '20th',
        '21st', '22nd', '23rd', '24th', '25th', '26th', '27th', '28th', '29th', '30th', '31st',
        
        # Generic academic/resume terms
        'gpa', 'college', 'university', 'school', 'institute', 'education', 
        'degree', 'bachelor', 'master', 'phd', 'graduate', 'undergraduate',
        'coursework', 'relevant coursework', 'extracurricular', 'activities',
        
        # Generic work terms
        'experience', 'responsibilities', 'duties', 'work', 'job', 'position', 
        'role', 'company', 'organization', 'team', 'project', 'projects',
        'description', 'summary', 'objective', 'skills', 'references',
        'ability', 'abilities', 'capability', 'capable',
        
        # Generic adjectives
        'big', 'small', 'large', 'good', 'great', 'excellent', 'strong', 'weak',
        
        # Generic action terms
        'build', 'connections', 'connection',
        
        # Generic verbs/actions
        'responsible', 'managed', 'developed', 'created', 'designed', 'implemented',
        'worked', 'assisted', 'helped', 'supported', 'performed', 'conducted',
        
        # Common locations (too generic)
        'city', 'state', 'country', 'usa', 'america', 'united states',
        
        # Time periods
        'present', 'current', 'year', 'years', 'month', 'months', 'week', 'weeks',
        'day', 'days', 'hour', 'hours',
        
        # Numbers and ranges
        'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
    }

    normalized = set()

    for keyword in keywords:
        keyword = keyword.strip().strip('.,;:!?')

        if len(keyword) < 2:
            continue

        keyword_lower = keyword.lower()

        # Skip stopwords
        if keyword_lower in stopwords:
            continue
            
        # Skip generic non-skill terms
        if keyword_lower in exclude_terms:
            continue
            
        # Skip dates with ordinal suffixes (e.g., "27th", "May 27th")
        if re.search(r'\d+(st|nd|rd|th)', keyword_lower):
            continue
            
        # Skip if it's just a number
        if keyword.replace('.', '').replace(',', '').isdigit():
            continue
            
        # Skip very generic single letters
        if len(keyword) == 1:
            continue

        # Preserve acronyms (all caps, 2+ chars)
        if keyword.isupper() and len(keyword) >= 2:
            normalized.add(keyword)
        # Preserve mixed case (likely proper nouns/technologies)
        elif any(char.isupper() for char in keyword):
            normalized.add(keyword)
        # Convert others to lowercase
        else:
            normalized.add(keyword_lower)

    return sorted(list(normalized))


def extract_keywords_from_job_description(job_desc: str) -> List[str]:
    """
    Extract keywords and skills from job description.

    Args:
        job_desc: Job description text

    Returns:
        List of extracted keywords

    Extraction strategy:
    1. Technical terms (proper nouns, acronyms, products)
    2. Noun phrases (skill combinations)
    3. Named entities (technologies, companies, locations)
    4. Requirements (experience, degrees)
    """
    try:
        if not job_desc or len(job_desc.strip()) < 10:
            app_logger.warning("Job description too short for keyword extraction")
            return []

        keywords = set()

        technical_terms = extract_technical_terms(job_desc)
        keywords.update(technical_terms)

        noun_phrases = extract_noun_phrases(job_desc)
        keywords.update(noun_phrases)

        requirements = extract_requirements(job_desc)
        keywords.update(requirements)

        normalized_keywords = normalize_keywords(list(keywords))

        app_logger.info(f"Extracted {len(normalized_keywords)} keywords from job description")
        app_logger.debug(f"Keywords: {normalized_keywords[:20]}")

        return normalized_keywords

    except Exception as e:
        app_logger.error(f"Error extracting keywords from job description: {e}")
        return []


def extract_keywords_from_resume(resume_text: str) -> List[str]:
    """
    Extract keywords and skills from resume.

    Args:
        resume_text: Resume text

    Returns:
        List of extracted keywords

    Uses same approach as job description extraction.
    """
    try:
        if not resume_text or len(resume_text.strip()) < 10:
            app_logger.warning("Resume text too short for keyword extraction")
            return []

        keywords = set()

        technical_terms = extract_technical_terms(resume_text)
        keywords.update(technical_terms)

        noun_phrases = extract_noun_phrases(resume_text)
        keywords.update(noun_phrases)

        normalized_keywords = normalize_keywords(list(keywords))

        app_logger.info(f"Extracted {len(normalized_keywords)} keywords from resume")
        app_logger.debug(f"Keywords: {normalized_keywords[:20]}")

        return normalized_keywords

    except Exception as e:
        app_logger.error(f"Error extracting keywords from resume: {e}")
        return []


def calculate_keyword_match(resume_keywords: List[str], job_keywords: List[str]) -> Dict:
    """
    Calculate keyword match between resume and job description.

    Args:
        resume_keywords: Keywords extracted from resume
        job_keywords: Keywords extracted from job description

    Returns:
        Dictionary with match details:
        {
            'matched': List of matched keywords,
            'missing': List of missing keywords,
            'match_percentage': Float (0-100)
        }
    """
    try:
        if not job_keywords:
            app_logger.warning("No job keywords to match against")
            return {
                'matched': [],
                'missing': [],
                'match_percentage': 0.0
            }

        resume_set = set(kw.lower() for kw in resume_keywords)
        job_set = set(kw.lower() for kw in job_keywords)

        matched_lower = resume_set.intersection(job_set)

        matched = []
        for kw in job_keywords:
            if kw.lower() in matched_lower:
                matched.append(kw)

        missing = []
        for kw in job_keywords:
            if kw.lower() not in matched_lower:
                missing.append(kw)

        match_percentage = (len(matched) / len(job_keywords) * 100) if job_keywords else 0.0

        app_logger.info(f"Keyword match: {len(matched)}/{len(job_keywords)} ({match_percentage:.1f}%)")

        return {
            'matched': matched,
            'missing': missing,
            'match_percentage': round(match_percentage, 1)
        }

    except Exception as e:
        app_logger.error(f"Error calculating keyword match: {e}")
        return {
            'matched': [],
            'missing': [],
            'match_percentage': 0.0
        }
