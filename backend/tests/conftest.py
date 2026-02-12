import os
import sys
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app as flask_app
from database.db import Base, Session, engine


@pytest.fixture
def app():
    """Create Flask app for testing"""
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    })
    yield flask_app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def db_session():
    """Create in-memory database session for testing"""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session()

    Base.metadata.create_all(bind=engine)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def sample_resume_text():
    """Sample resume text for testing"""
    return """[HEADER]
John Doe | john@example.com | (555) 123-4567

[EDUCATION]
University of Example | Example City, CA
Bachelor of Science in Computer Science | May 2023

[EXPERIENCE]
Tech Corp | San Francisco, CA
Software Engineer | June 2023 - Present
- Developed scalable microservices handling 10,000+ requests per second
- Improved application performance by 50% through optimization
- Led team of 5 engineers on critical infrastructure project

StartupXYZ | Remote
Junior Developer | Jan 2022 - May 2023
- Built responsive web applications using React and Node.js
- Reduced page load time by 40% through code optimization
- Collaborated with designers to implement pixel-perfect UIs

[SKILLS]
Programming Languages: Python, JavaScript, Java, C++
Frameworks: React, Flask, Django, Node.js
Tools: Git, Docker, AWS, PostgreSQL

[PROJECTS]
E-Commerce Platform | React, Node.js, MongoDB
Jan 2023 - Mar 2023
- Developed full-stack e-commerce application with 1,000+ products
- Implemented secure payment processing with Stripe API
- Achieved 99.9% uptime during beta testing
"""

@pytest.fixture
def sample_job_description():
    """Sample job description for testing"""
    return """
We are seeking a talented Senior Software Engineer to join our team.

Requirements:
- 3+ years of experience in software development
- Strong proficiency in Python and JavaScript
- Experience with React and modern web frameworks
- Familiarity with cloud platforms (AWS, GCP, or Azure)
- Excellent problem-solving skills

Responsibilities:
- Design and implement scalable backend services
- Collaborate with cross-functional teams
- Mentor junior developers
- Optimize application performance

Nice to have:
- Experience with Docker and Kubernetes
- Knowledge of microservices architecture
- Contributions to open-source projects
"""

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    mock = MagicMock()
    mock.choices = [MagicMock()]
    mock.choices[0].message.content = """[EDUCATION]
University of Example | Example City, CA
Bachelor of Science in Computer Science | May 2023

[EXPERIENCE]
Tech Corp | San Francisco, CA
Senior Software Engineer | June 2023 - Present
- Architected scalable microservices handling 10,000+ requests per second
- Improved application performance by 50% through optimization
- Led team of 5 engineers on critical infrastructure project

[SKILLS]
Programming Languages: Python, JavaScript, Java, C++
Frameworks: React, Flask, Django, Node.js
Tools: Git, Docker, AWS, PostgreSQL
"""
    return mock

@pytest.fixture
def mock_scoring_response():
    """Mock AI scoring response"""
    return {
        'ats_score': 18.0,
        'ats_feedback': 'Good formatting and keyword usage',
        'content_score': 17.0,
        'content_feedback': 'Strong achievements with metrics',
        'style_score': 22.0,
        'style_feedback': 'Professional tone with action verbs',
        'match_score': 23.0,
        'match_feedback': 'Excellent alignment with job requirements',
        'readiness_score': 9.0,
        'readiness_feedback': 'Resume is nearly ready for submission',
        'total_score': 89.0
    }

@pytest.fixture
def mock_review_response():
    """Mock AI review response"""
    return {
        'bullets': [
            {
                'section': 'Experience',
                'original_text': 'Developed scalable microservices handling 10,000+ requests per second',
                'strengths': 'Quantifies impact with specific metrics',
                'refinement_suggestions': 'Could mention specific technologies used',
                'relevance_score': 5
            },
            {
                'section': 'Experience',
                'original_text': 'Improved application performance by 50% through optimization',
                'strengths': 'Shows measurable improvement',
                'refinement_suggestions': 'Specify what type of optimization was done',
                'relevance_score': 4
            }
        ]
    }
