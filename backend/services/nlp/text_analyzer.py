"""Text analysis module for similarity, ATS compatibility, and quality checks."""

import re
from typing import Dict, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from utils.logger import app_logger

stop_words = set(stopwords.words('english'))


def calculate_keyword_density(resume_text: str, job_keywords: List[str]) -> float:
    """
    Calculate how frequently job keywords appear in resume.

    Args:
        resume_text: Resume text
        job_keywords: List of keywords from job description

    Returns:
        Keyword density score (0.0 to 1.0)
    """
    try:
        if not job_keywords or not resume_text:
            return 0.0

        resume_lower = resume_text.lower()
        total_keywords = len(job_keywords)
        found_keywords = 0

        for keyword in job_keywords:
            if keyword.lower() in resume_lower:
                found_keywords += 1

        density = found_keywords / total_keywords if total_keywords > 0 else 0.0

        app_logger.debug(f"Keyword density: {found_keywords}/{total_keywords} = {density:.2f}")
        return density

    except Exception as e:
        app_logger.error(f"Error calculating keyword density: {e}")
        return 0.0


def check_ats_compatibility(resume_text: str) -> Dict:
    """
    Check ATS (Applicant Tracking System) compatibility.

    Args:
        resume_text: Resume text

    Returns:
        Dictionary with ATS compatibility details:
        {
            'score': int (0-100),
            'issues': List of issues found,
            'recommendations': List of recommendations
        }

    ATS compatibility factors:
    - Standard section headings
    - No special characters
    - Readable formatting
    - Standard fonts (inferred from text quality)
    """
    try:
        issues = []
        recommendations = []
        score = 100

        if not resume_text or len(resume_text) < 100:
            return {
                'score': 0,
                'issues': ['Resume too short'],
                'recommendations': ['Provide a complete resume']
            }

        special_char_pattern = r'[^\w\s.,;:()\-\'\"/\n]'
        special_chars = re.findall(special_char_pattern, resume_text)
        if len(special_chars) > 20:
            issues.append(f"Contains {len(special_chars)} special characters that may confuse ATS")
            recommendations.append("Remove special characters and symbols")
            score -= 15

        standard_sections = ['experience', 'education', 'skills']
        resume_lower = resume_text.lower()
        found_sections = sum(1 for section in standard_sections if section in resume_lower)

        if found_sections < 2:
            issues.append("Missing standard section headings")
            recommendations.append("Use clear section headers: Experience, Education, Skills")
            score -= 20

        lines = resume_text.split('\n')
        very_long_lines = [line for line in lines if len(line) > 200]
        if len(very_long_lines) > 3:
            issues.append("Contains very long lines that may indicate tables or complex formatting")
            recommendations.append("Use simple formatting without tables")
            score -= 10

        bullet_points = resume_text.count('•') + resume_text.count('*') + resume_text.count('-')
        word_count = len(resume_text.split())
        if word_count > 0 and bullet_points < (word_count / 100):
            issues.append("Few bullet points detected")
            recommendations.append("Use bullet points to list achievements and responsibilities")
            score -= 5

        score = max(0, min(100, score))

        app_logger.info(f"ATS compatibility score: {score}/100, issues: {len(issues)}")

        return {
            'score': score,
            'issues': issues,
            'recommendations': recommendations
        }

    except Exception as e:
        app_logger.error(f"Error checking ATS compatibility: {e}")
        return {
            'score': 50,
            'issues': ['Error during ATS check'],
            'recommendations': []
        }


def calculate_text_similarity(resume_text: str, job_desc: str) -> float:
    """
    Calculate cosine similarity between resume and job description using TF-IDF.

    Args:
        resume_text: Resume text
        job_desc: Job description text

    Returns:
        Similarity score (0.0 to 1.0)
    """
    try:
        if not resume_text or not job_desc:
            return 0.0

        vectorizer = TfidfVectorizer(stop_words='english', max_features=500)

        documents = [resume_text, job_desc]
        tfidf_matrix = vectorizer.fit_transform(documents)

        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

        app_logger.debug(f"Text similarity (TF-IDF cosine): {similarity:.3f}")
        return float(similarity)

    except Exception as e:
        app_logger.error(f"Error calculating text similarity: {e}")
        return 0.0


def count_quantified_achievements(resume_text: str) -> int:
    """
    Count quantified achievements in resume (numbers, percentages, metrics).

    Args:
        resume_text: Resume text

    Returns:
        Count of quantified achievements
    """
    try:
        patterns = [
            r'\d+%',
            r'\$[\d,]+',
            r'\d+[kKmMbB]\+?',
            r'\d+x',
            r'\d+\+?\s*(?:years?|months?|weeks?)',
            r'increased?\s+by\s+\d+',
            r'reduced?\s+by\s+\d+',
            r'saved?\s+\$?\d+',
            r'grew?\s+\d+',
        ]

        total_count = 0
        for pattern in patterns:
            matches = re.findall(pattern, resume_text, re.IGNORECASE)
            total_count += len(matches)

        app_logger.debug(f"Found {total_count} quantified achievements")
        return total_count

    except Exception as e:
        app_logger.error(f"Error counting quantified achievements: {e}")
        return 0


def extract_action_verbs(resume_text: str) -> List[str]:
    """
    Extract action verbs from resume.

    Args:
        resume_text: Resume text

    Returns:
        List of action verbs found

    Common strong action verbs in resumes.
    """
    strong_action_verbs = {
        'achieved', 'architected', 'built', 'created', 'designed', 'developed',
        'directed', 'engineered', 'established', 'executed', 'implemented',
        'improved', 'increased', 'launched', 'led', 'managed', 'optimized',
        'orchestrated', 'pioneered', 'reduced', 'spearheaded', 'streamlined',
        'transformed', 'accelerated', 'automated', 'collaborated', 'delivered',
        'drove', 'enhanced', 'generated', 'initiated', 'integrated', 'maintained',
        'modernized', 'planned', 'resolved', 'scaled', 'standardized'
    }

    resume_lower = resume_text.lower()
    found_verbs = [verb for verb in strong_action_verbs if verb in resume_lower]

    app_logger.debug(f"Found {len(found_verbs)} strong action verbs")
    return found_verbs


def analyze_text_quality(resume_text: str) -> Dict:
    """
    Analyze overall text quality of resume.

    Args:
        resume_text: Resume text

    Returns:
        Dictionary with quality metrics:
        {
            'avg_sentence_length': float,
            'action_verb_count': int,
            'quantified_achievements': int,
            'word_count': int,
            'readability_score': float (0-100)
        }
    """
    try:
        sentences = resume_text.split('.')
        sentences = [s.strip() for s in sentences if s.strip()]

        words = resume_text.split()
        word_count = len(words)

        avg_sentence_length = word_count / len(sentences) if sentences else 0

        action_verbs = extract_action_verbs(resume_text)
        action_verb_count = len(action_verbs)

        quantified = count_quantified_achievements(resume_text)

        readability_score = min(100, (
            (action_verb_count * 5) +
            (quantified * 3) +
            (50 if 10 <= avg_sentence_length <= 25 else 0) +
            (30 if word_count >= 300 else (word_count / 300 * 30))
        ))

        quality_data = {
            'avg_sentence_length': round(avg_sentence_length, 1),
            'action_verb_count': action_verb_count,
            'quantified_achievements': quantified,
            'word_count': word_count,
            'readability_score': round(readability_score, 1)
        }

        app_logger.info(f"Text quality analysis: {quality_data}")
        return quality_data

    except Exception as e:
        app_logger.error(f"Error analyzing text quality: {e}")
        return {
            'avg_sentence_length': 0,
            'action_verb_count': 0,
            'quantified_achievements': 0,
            'word_count': 0,
            'readability_score': 0
        }
