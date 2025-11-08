"""Integration tests for NLP modules."""

import pytest
from services.nlp import (
    extract_text, clean_text,
    extract_all_entities,
    extract_keywords_from_job_description,
    extract_keywords_from_resume,
    calculate_keyword_match,
    calculate_text_similarity,
    check_ats_compatibility,
    analyze_text_quality,
    score_resume_against_job
)


class TestResumeParser:
    """Test resume parsing functionality."""

    def test_clean_text(self):
        """Test text cleaning."""
        text = "This  is   a   test\n\n\n\nwith    extra    whitespace"
        cleaned = clean_text(text)

        assert cleaned == "This is a test\n\nwith extra whitespace"
        assert "   " not in cleaned


class TestEntityExtractor:
    """Test entity extraction."""

    def test_extract_all_entities(self):
        """Test extracting all entities from sample resume."""
        resume_text = """
        John Doe
        john.doe@example.com
        (555) 123-4567

        EXPERIENCE
        Software Engineer at Tech Corp
        - Developed web applications

        EDUCATION
        Bachelor's in Computer Science

        SKILLS
        Python, JavaScript, React
        """

        entities = extract_all_entities(resume_text)

        assert entities is not None
        assert 'name' in entities
        assert 'email' in entities
        assert 'phone' in entities
        assert 'sections' in entities

        assert entities['email'] == 'john.doe@example.com'
        assert 'EXPERIENCE' in resume_text.upper() or 'experience' in entities['sections']


class TestSkillExtractor:
    """Test skill and keyword extraction."""

    def test_extract_keywords_from_job_description(self):
        """Test extracting keywords from job description."""
        job_desc = """
        We are looking for a Senior Software Engineer with 5+ years of experience in Python,
        JavaScript, and React. The ideal candidate will have experience with AWS, Docker,
        and Kubernetes. Bachelor's degree in Computer Science required.
        """

        keywords = extract_keywords_from_job_description(job_desc)

        assert keywords is not None
        assert len(keywords) > 0

        keywords_lower = [k.lower() for k in keywords]
        assert any('python' in k for k in keywords_lower)

    def test_extract_keywords_from_resume(self):
        """Test extracting keywords from resume."""
        resume_text = """
        Experienced Software Engineer with expertise in Python, React, and AWS.
        Built scalable applications using Docker and Kubernetes.
        """

        keywords = extract_keywords_from_resume(resume_text)

        assert keywords is not None
        assert len(keywords) > 0

    def test_calculate_keyword_match(self):
        """Test keyword matching."""
        resume_keywords = ['Python', 'React', 'AWS', 'SQL']
        job_keywords = ['Python', 'React', 'Docker', 'Kubernetes']

        match = calculate_keyword_match(resume_keywords, job_keywords)

        assert match is not None
        assert 'matched' in match
        assert 'missing' in match
        assert 'match_percentage' in match

        assert len(match['matched']) == 2
        assert len(match['missing']) == 2
        assert match['match_percentage'] == 50.0


class TestTextAnalyzer:
    """Test text analysis functions."""

    def test_calculate_text_similarity(self):
        """Test text similarity calculation."""
        text1 = "Python developer with React experience"
        text2 = "Looking for a Python engineer who knows React"

        similarity = calculate_text_similarity(text1, text2)

        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.2

    def test_check_ats_compatibility(self):
        """Test ATS compatibility check."""
        resume_text = """
        EXPERIENCE
        Software Engineer
        - Developed applications
        - Led team of developers

        EDUCATION
        Bachelor's in Computer Science

        SKILLS
        Python, JavaScript, React
        """

        ats_check = check_ats_compatibility(resume_text)

        assert ats_check is not None
        assert 'score' in ats_check
        assert 'issues' in ats_check
        assert 'recommendations' in ats_check

        assert 0 <= ats_check['score'] <= 100

    def test_analyze_text_quality(self):
        """Test text quality analysis."""
        resume_text = """
        Developed a web application that increased user engagement by 50%.
        Led a team of 5 developers to deliver project ahead of schedule.
        Implemented CI/CD pipeline that reduced deployment time by 75%.
        """

        quality = analyze_text_quality(resume_text)

        assert quality is not None
        assert 'quantified_achievements' in quality
        assert 'action_verb_count' in quality
        assert 'word_count' in quality
        assert 'readability_score' in quality

        assert quality['quantified_achievements'] >= 2
        assert quality['action_verb_count'] >= 1


class TestLocalScorer:
    """Test local resume scoring."""

    def test_score_resume_against_job(self):
        """Test complete resume scoring."""
        resume_text = """
        John Doe
        john.doe@example.com

        EXPERIENCE
        Senior Software Engineer at Tech Corp (2019-2024)
        - Developed web applications using Python and React
        - Led team of 5 developers
        - Increased system performance by 40%
        - Implemented CI/CD pipeline using Docker and AWS

        EDUCATION
        Bachelor's in Computer Science

        SKILLS
        Python, JavaScript, React, Docker, AWS, SQL
        """

        job_description = """
        We are looking for a Senior Software Engineer with 5+ years of experience.

        Requirements:
        - Strong experience with Python and React
        - Experience with AWS and Docker
        - Leadership experience
        - Bachelor's degree in Computer Science

        You will be responsible for:
        - Building scalable web applications
        - Leading engineering teams
        - Implementing best practices
        """

        score = score_resume_against_job(resume_text, job_description)

        assert score is not None
        assert 'total_score' in score
        assert 'keyword_match_score' in score
        assert 'keyword_match_details' in score
        assert 'relevance_score' in score
        assert 'ats_score' in score
        assert 'quality_score' in score
        assert 'recommendations' in score

        assert 0 <= score['total_score'] <= 100
        assert 0 <= score['keyword_match_score'] <= 100
        assert 0 <= score['relevance_score'] <= 100
        assert 0 <= score['ats_score'] <= 100
        assert 0 <= score['quality_score'] <= 100

        assert isinstance(score['recommendations'], list)
        assert len(score['recommendations']) > 0

        assert score['total_score'] > 30

    def test_score_poor_match(self):
        """Test scoring with poor resume-job match."""
        resume_text = """
        Marketing Specialist with experience in social media campaigns.
        Managed brand presence across multiple platforms.
        """

        job_description = """
        Looking for a Senior Backend Engineer with Python and AWS experience.
        Must have 5+ years of software development experience.
        """

        score = score_resume_against_job(resume_text, job_description)

        assert score is not None
        assert score['total_score'] < 50

    def test_score_empty_inputs(self):
        """Test scoring with empty or invalid inputs."""
        score = score_resume_against_job("", "")

        assert score is not None
        assert score['total_score'] == 0
