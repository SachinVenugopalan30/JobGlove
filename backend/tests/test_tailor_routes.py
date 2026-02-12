import json
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

from routes.resume import resume_bp


@pytest.fixture
def app():
    """Create test Flask app"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(resume_bp, url_prefix='/api')
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestTailorResumeEndpoint:
    """Test the updated /api/tailor-resume endpoint"""

    @patch('routes.resume.DocumentParser.extract_text')
    @patch('routes.resume.DocumentParser.extract_header')
    @patch('routes.resume.DocumentParser.remove_header')
    @patch('routes.resume.AIService.get_provider')
    @patch('routes.resume.LaTeXGenerator.generate_latex')
    @patch('routes.resume.get_session')
    @patch('routes.resume.os.path.exists')
    @patch('routes.resume.os.remove')
    def test_tailor_resume_success_with_scores(
        self,
        mock_remove,
        mock_exists,
        mock_get_session,
        mock_latex_gen,
        mock_get_provider,
        mock_remove_header,
        mock_extract_header,
        mock_extract_text,
        client
    ):
        mock_extract_text.return_value = "Full resume text with header"
        mock_extract_header.return_value = "[HEADER]\nJohn Doe\njohn@email.com\n"
        mock_remove_header.return_value = "Resume text without header"

        mock_provider = MagicMock()
        mock_ai_response = {
            'original_score': {
                'total_score': 72,
                'keyword_match_score': 68,
                'relevance_score': 75,
                'ats_score': 80,
                'quality_score': 65,
                'recommendations': ['Add more metrics', 'Use action verbs']
            },
            'tailored_resume': '[EDUCATION]\nUniversity | Location\nDegree | 2020',
            'tailored_score': {
                'total_score': 89,
                'keyword_match_score': 92,
                'relevance_score': 88,
                'ats_score': 85,
                'quality_score': 90
            }
        }
        mock_provider.score_and_tailor_resume.return_value = mock_ai_response
        mock_get_provider.return_value = mock_provider

        mock_latex_gen.return_value = ('/outputs/resume.pdf', '/outputs/resume.tex')

        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_exists.return_value = True

        request_data = {
            'file_path': 'uploads/resume.pdf',
            'job_description': 'Software Engineer position...',
            'api': 'openai',
            'user_name': 'John Doe',
            'company': 'Google',
            'job_title': 'Software Engineer',
            'custom_prompt': None
        }

        response = client.post(
            '/api/tailor-resume',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'original_score' in data
        assert 'tailored_score' in data
        assert data['original_score']['total_score'] == 72
        assert data['tailored_score']['total_score'] == 89
        assert data['pdf_file'] == 'resume.pdf'
        assert data['tex_file'] == 'resume.tex'
        assert 'message' in data

        mock_provider.score_and_tailor_resume.assert_called_once_with(
            "Resume text without header",
            "Software Engineer position...",
            None
        )

        mock_remove.assert_called_once()

    @patch('routes.resume.DocumentParser.extract_text')
    @patch('routes.resume.DocumentParser.extract_header')
    @patch('routes.resume.DocumentParser.remove_header')
    @patch('routes.resume.AIService.get_provider')
    @patch('routes.resume.LaTeXGenerator.generate_latex')
    @patch('routes.resume.get_session')
    @patch('routes.resume.os.path.exists')
    @patch('routes.resume.os.remove')
    def test_tailor_resume_with_custom_prompt(
        self,
        mock_remove,
        mock_exists,
        mock_get_session,
        mock_latex_gen,
        mock_get_provider,
        mock_remove_header,
        mock_extract_header,
        mock_extract_text,
        client
    ):
        mock_extract_text.return_value = "Resume text"
        mock_extract_header.return_value = "[HEADER]\n"
        mock_remove_header.return_value = "Resume"

        mock_provider = MagicMock()
        mock_ai_response = {
            'original_score': {'total_score': 70, 'keyword_match_score': 65, 'relevance_score': 75, 'ats_score': 70, 'quality_score': 70},
            'tailored_resume': 'Tailored',
            'tailored_score': {'total_score': 85, 'keyword_match_score': 80, 'relevance_score': 90, 'ats_score': 85, 'quality_score': 85}
        }
        mock_provider.score_and_tailor_resume.return_value = mock_ai_response
        mock_get_provider.return_value = mock_provider

        mock_latex_gen.return_value = ('/outputs/resume.pdf', '/outputs/resume.tex')
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_exists.return_value = True

        request_data = {
            'file_path': 'uploads/resume.pdf',
            'job_description': 'Job description',
            'api': 'claude',
            'user_name': 'Test',
            'company': 'Company',
            'job_title': 'Role',
            'custom_prompt': 'Focus on Python skills'
        }

        response = client.post(
            '/api/tailor-resume',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 200

        mock_provider.score_and_tailor_resume.assert_called_once_with(
            "Resume",
            "Job description",
            "Focus on Python skills"
        )

    def test_tailor_resume_missing_fields(self, client):
        request_data = {
            'file_path': 'uploads/resume.pdf'
        }

        response = client.post(
            '/api/tailor-resume',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    @patch('routes.resume.DocumentParser.extract_text')
    def test_tailor_resume_text_extraction_fails(self, mock_extract_text, client):
        mock_extract_text.return_value = ""

        request_data = {
            'file_path': 'uploads/resume.pdf',
            'job_description': 'Job description',
            'api': 'openai',
            'user_name': 'Test',
            'company': 'Company',
            'job_title': 'Role'
        }

        response = client.post(
            '/api/tailor-resume',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'extract text' in data['error'].lower()

    @patch('routes.resume.DocumentParser.extract_text')
    @patch('routes.resume.DocumentParser.extract_header')
    @patch('routes.resume.DocumentParser.remove_header')
    @patch('routes.resume.AIService.get_provider')
    def test_tailor_resume_ai_error(
        self,
        mock_get_provider,
        mock_remove_header,
        mock_extract_header,
        mock_extract_text,
        client
    ):
        mock_extract_text.return_value = "Resume text"
        mock_extract_header.return_value = "[HEADER]\n"
        mock_remove_header.return_value = "Resume"

        mock_provider = MagicMock()
        mock_provider.score_and_tailor_resume.side_effect = Exception("AI API Error")
        mock_get_provider.return_value = mock_provider

        request_data = {
            'file_path': 'uploads/resume.pdf',
            'job_description': 'Job description',
            'api': 'openai',
            'user_name': 'Test',
            'company': 'Company',
            'job_title': 'Role'
        }

        response = client.post(
            '/api/tailor-resume',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data

    @patch('routes.resume.Config')
    @patch('routes.resume.DocumentParser.extract_text')
    @patch('routes.resume.DocumentParser.extract_header')
    @patch('routes.resume.DocumentParser.remove_header')
    def test_tailor_resume_invalid_api_key(
        self,
        mock_remove_header,
        mock_extract_header,
        mock_extract_text,
        mock_config,
        client
    ):
        mock_extract_text.return_value = "Resume text"
        mock_extract_header.return_value = "[HEADER]\n"
        mock_remove_header.return_value = "Resume"

        mock_config.OPENAI_API_KEY = None
        mock_config.GEMINI_API_KEY = None
        mock_config.ANTHROPIC_API_KEY = None

        request_data = {
            'file_path': 'uploads/resume.pdf',
            'job_description': 'Job description',
            'api': 'openai',
            'user_name': 'Test',
            'company': 'Company',
            'job_title': 'Role'
        }

        response = client.post(
            '/api/tailor-resume',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'not configured' in data['error'].lower()


class TestScoreDataStructure:
    """Test that score data structure matches expected format"""

    @patch('routes.resume.DocumentParser.extract_text')
    @patch('routes.resume.DocumentParser.extract_header')
    @patch('routes.resume.DocumentParser.remove_header')
    @patch('routes.resume.AIService.get_provider')
    @patch('routes.resume.LaTeXGenerator.generate_latex')
    @patch('routes.resume.get_session')
    @patch('routes.resume.os.path.exists')
    @patch('routes.resume.os.remove')
    def test_score_structure_includes_all_fields(
        self,
        mock_remove,
        mock_exists,
        mock_get_session,
        mock_latex_gen,
        mock_get_provider,
        mock_remove_header,
        mock_extract_header,
        mock_extract_text,
        client
    ):
        mock_extract_text.return_value = "Resume text"
        mock_extract_header.return_value = "[HEADER]\n"
        mock_remove_header.return_value = "Resume"

        mock_provider = MagicMock()
        mock_ai_response = {
            'original_score': {
                'total_score': 72,
                'keyword_match_score': 68,
                'relevance_score': 75,
                'ats_score': 80,
                'quality_score': 65,
                'recommendations': ['Rec 1', 'Rec 2']
            },
            'tailored_resume': 'Tailored resume',
            'tailored_score': {
                'total_score': 89,
                'keyword_match_score': 92,
                'relevance_score': 88,
                'ats_score': 85,
                'quality_score': 90
            }
        }
        mock_provider.score_and_tailor_resume.return_value = mock_ai_response
        mock_get_provider.return_value = mock_provider

        mock_latex_gen.return_value = ('/outputs/resume.pdf', '/outputs/resume.tex')
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_exists.return_value = True

        request_data = {
            'file_path': 'uploads/resume.pdf',
            'job_description': 'Job',
            'api': 'openai',
            'user_name': 'Test',
            'company': 'Co',
            'job_title': 'Role'
        }

        response = client.post(
            '/api/tailor-resume',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        data = json.loads(response.data)

        assert 'original_score' in data
        assert 'total_score' in data['original_score']
        assert 'keyword_match_score' in data['original_score']
        assert 'relevance_score' in data['original_score']
        assert 'ats_score' in data['original_score']
        assert 'quality_score' in data['original_score']
        assert 'recommendations' in data['original_score']

        assert 'tailored_score' in data
        assert 'total_score' in data['tailored_score']
        assert 'keyword_match_score' in data['tailored_score']
        assert 'relevance_score' in data['tailored_score']
        assert 'ats_score' in data['tailored_score']
        assert 'quality_score' in data['tailored_score']
