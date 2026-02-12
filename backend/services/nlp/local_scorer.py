"""Local resume scoring module that combines all NLP analysis."""


from utils.logger import app_logger

from .skill_extractor import (
    calculate_keyword_match,
    extract_keywords_from_job_description,
    extract_keywords_from_resume,
)
from .text_analyzer import (
    analyze_text_quality,
    calculate_keyword_density,
    calculate_text_similarity,
    check_ats_compatibility,
)

KEYWORD_MATCH_WEIGHT = 0.40
RELEVANCE_WEIGHT = 0.25
ATS_WEIGHT = 0.20
QUALITY_WEIGHT = 0.15


def score_resume_against_job(resume_text: str, job_description: str) -> dict:
    """
    Score resume against job description using local NLP.

    Args:
        resume_text: Full resume text
        job_description: Job description text

    Returns:
        Dictionary with comprehensive scoring:
        {
            'total_score': int (0-100),

            'keyword_match_score': int (0-100),
            'keyword_match_details': {
                'matched': List[str],
                'missing': List[str],
                'match_percentage': float
            },

            'relevance_score': int (0-100),
            'relevance_details': {
                'similarity_score': float,
                'keyword_density': float
            },

            'ats_score': int (0-100),
            'ats_details': {
                'issues': List[str],
                'recommendations': List[str]
            },

            'quality_score': int (0-100),
            'quality_details': {
                'quantified_achievements': int,
                'action_verbs_count': int,
                'readability_score': float,
                'word_count': int
            },

            'recommendations': List[str]
        }
    """
    try:
        app_logger.info("Starting local NLP resume scoring")

        job_keywords = extract_keywords_from_job_description(job_description)
        resume_keywords = extract_keywords_from_resume(resume_text)

        keyword_match = calculate_keyword_match(resume_keywords, job_keywords)
        keyword_match_score = int(keyword_match['match_percentage'])

        text_similarity = calculate_text_similarity(resume_text, job_description)
        keyword_density = calculate_keyword_density(resume_text, job_keywords)

        relevance_score = int(
            (text_similarity * 60) +
            (keyword_density * 40)
        )

        ats_check = check_ats_compatibility(resume_text)
        ats_score = ats_check['score']

        quality_analysis = analyze_text_quality(resume_text)
        quality_score = int(quality_analysis['readability_score'])

        total_score = _calculate_total_score(
            keyword_match_score,
            relevance_score,
            ats_score,
            quality_score
        )

        recommendations = generate_recommendations({
            'keyword_match': keyword_match,
            'relevance_score': relevance_score,
            'ats_check': ats_check,
            'quality_analysis': quality_analysis
        })

        result = {
            'total_score': total_score,

            'keyword_match_score': keyword_match_score,
            'keyword_match_details': {
                'matched': keyword_match['matched'][:20],
                'missing': keyword_match['missing'][:20],
                'match_percentage': keyword_match['match_percentage']
            },

            'relevance_score': relevance_score,
            'relevance_details': {
                'similarity_score': round(text_similarity, 3),
                'keyword_density': round(keyword_density, 3)
            },

            'ats_score': ats_score,
            'ats_details': {
                'issues': ats_check['issues'],
                'recommendations': ats_check['recommendations']
            },

            'quality_score': quality_score,
            'quality_details': {
                'quantified_achievements': quality_analysis['quantified_achievements'],
                'action_verbs_count': quality_analysis['action_verb_count'],
                'readability_score': quality_analysis['readability_score'],
                'word_count': quality_analysis['word_count']
            },

            'recommendations': recommendations
        }

        app_logger.info(f"Resume scoring complete: Total score = {total_score}/100")
        return result

    except Exception as e:
        app_logger.error(f"Error scoring resume: {e}")
        return _fallback_score(str(e))


def _calculate_total_score(keyword_score: float, relevance_score: float,
                          ats_score: float, quality_score: float) -> int:
    """
    Calculate weighted total score.

    Weights:
    - Keyword match: 40%
    - Relevance: 25%
    - ATS compatibility: 20%
    - Quality: 15%

    Args:
        keyword_score: Keyword match score (0-100)
        relevance_score: Relevance score (0-100)
        ats_score: ATS compatibility score (0-100)
        quality_score: Quality score (0-100)

    Returns:
        Total weighted score (0-100)
    """
    total = (
        keyword_score * KEYWORD_MATCH_WEIGHT +
        relevance_score * RELEVANCE_WEIGHT +
        ats_score * ATS_WEIGHT +
        quality_score * QUALITY_WEIGHT
    )

    return int(round(total))


def generate_recommendations(score_data: dict) -> list[str]:
    """
    Generate actionable recommendations based on scores.

    Args:
        score_data: Dictionary containing all score components

    Returns:
        List of recommendations
    """
    recommendations = []

    keyword_match = score_data['keyword_match']
    if keyword_match['missing']:
        top_missing = keyword_match['missing'][:5]
        recommendations.append(
            f"Add these missing keywords from the job description: {', '.join(top_missing)}"
        )

    relevance_score = score_data['relevance_score']
    if relevance_score < 50:
        recommendations.append(
            "Tailor your resume content to better match the job description language"
        )

    ats_check = score_data['ats_check']
    if ats_check['recommendations']:
        recommendations.extend(ats_check['recommendations'][:2])

    quality_analysis = score_data['quality_analysis']

    if quality_analysis['quantified_achievements'] < 5:
        recommendations.append(
            f"Add more quantified achievements (currently {quality_analysis['quantified_achievements']}, aim for 10+)"
        )

    if quality_analysis['action_verb_count'] < 8:
        recommendations.append(
            "Use more strong action verbs (achieved, developed, led, etc.)"
        )

    if quality_analysis['word_count'] < 300:
        recommendations.append(
            "Expand your resume with more detailed experience descriptions"
        )
    elif quality_analysis['word_count'] > 1000:
        recommendations.append(
            "Consider condensing your resume to be more concise"
        )

    if not recommendations:
        recommendations.append("Your resume looks good! Consider minor refinements based on specific job requirements.")

    return recommendations[:8]


def _fallback_score(error_message: str) -> dict:
    """
    Return fallback score when scoring fails.

    Args:
        error_message: Error description

    Returns:
        Minimal score dictionary
    """
    return {
        'total_score': 0,
        'keyword_match_score': 0,
        'keyword_match_details': {
            'matched': [],
            'missing': [],
            'match_percentage': 0.0
        },
        'relevance_score': 0,
        'relevance_details': {
            'similarity_score': 0.0,
            'keyword_density': 0.0
        },
        'ats_score': 0,
        'ats_details': {
            'issues': [f'Scoring failed: {error_message}'],
            'recommendations': []
        },
        'quality_score': 0,
        'quality_details': {
            'quantified_achievements': 0,
            'action_verbs_count': 0,
            'readability_score': 0.0,
            'word_count': 0
        },
        'recommendations': ['Unable to score resume due to an error']
    }
