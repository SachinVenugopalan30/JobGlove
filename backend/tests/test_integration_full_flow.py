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


class TestFullTailoringFlow:
    """Integration tests for the complete resume tailoring workflow"""

    @patch('routes.resume.Config')
    def test_check_apis_returns_available_providers(self, mock_config, client):
        mock_config.OPENAI_API_KEY = 'test_openai_key'
        mock_config.GEMINI_API_KEY = None
        mock_config.ANTHROPIC_API_KEY = 'test_claude_key'
        mock_config.check_api_availability.return_value = {
            'openai': True,
            'gemini': False,
            'claude': True
        }

        response = client.get('/api/check-apis')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['openai'] is True
        assert data['gemini'] is False
        assert data['claude'] is True

    @patch('routes.resume.DocumentParser.validate_file')
    @patch('routes.resume.os.path.join')
    def test_upload_resume_success(self, mock_join, mock_validate, client, tmp_path):
        mock_validate.return_value = True
        mock_join.return_value = str(tmp_path / 'test.pdf')

        data = {'file': (open(__file__, 'rb'), 'test.pdf')}
        response = client.post('/api/upload-resume', data=data, content_type='multipart/form-data')

        assert response.status_code == 200
        result = json.loads(response.data)
        assert 'file_path' in result
        assert 'filename' in result

    @patch('routes.resume.DocumentParser.extract_text')
    @patch('routes.resume.DocumentParser.extract_header')
    @patch('routes.resume.DocumentParser.remove_header')
    @patch('routes.resume.AIService.get_provider')
    @patch('routes.resume.LaTeXGenerator.generate_latex')
    @patch('routes.resume.get_session')
    @patch('routes.resume.os.path.exists')
    @patch('routes.resume.os.remove')
    def test_complete_tailoring_flow_openai(
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
        """Test complete flow: upload -> tailor -> download with OpenAI"""
        mock_extract_text.return_value = "John Doe\njohn@email.com\nSoftware Engineer with 5 years experience"
        mock_extract_header.return_value = "[HEADER]\nJohn Doe\njohn@email.com\n"
        mock_remove_header.return_value = "Software Engineer with 5 years experience"

        mock_provider = MagicMock()
        mock_ai_response = {
            'original_score': {
                'total_score': 75,
                'keyword_match_score': 70,
                'relevance_score': 78,
                'ats_score': 80,
                'quality_score': 72,
                'recommendations': ['Add metrics', 'Use action verbs']
            },
            'tailored_resume': '[EXPERIENCE]\nTech Corp | San Francisco\nSenior Developer | 2020-2023\n- Led team of 5 developers',
            'tailored_score': {
                'total_score': 92,
                'keyword_match_score': 95,
                'relevance_score': 91,
                'ats_score': 90,
                'quality_score': 92
            }
        }
        mock_provider.score_and_tailor_resume.return_value = mock_ai_response
        mock_get_provider.return_value = mock_provider

        mock_latex_gen.return_value = ('/outputs/tailored_resume.pdf', '/outputs/tailored_resume.tex')

        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_exists.return_value = True

        request_data = {
            'file_path': 'uploads/original_resume.pdf',
            'job_description': 'We are looking for a Senior Software Engineer with Python experience...',
            'api': 'openai',
            'user_name': 'John Doe',
            'company': 'Tech Corp',
            'job_title': 'Senior Software Engineer',
        }

        response = client.post(
            '/api/tailor-resume',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'original_score' in data
        assert data['original_score']['total_score'] == 75
        assert len(data['original_score']['recommendations']) == 2

        assert 'tailored_score' in data
        assert data['tailored_score']['total_score'] == 92

        assert data['tailored_score']['total_score'] > data['original_score']['total_score']

        assert 'pdf_file' in data
        assert 'tex_file' in data
        assert 'message' in data

        mock_provider.score_and_tailor_resume.assert_called_once()
        mock_latex_gen.assert_called_once()
        mock_remove.assert_called_once()

    @patch('routes.resume.DocumentParser.extract_text')
    @patch('routes.resume.DocumentParser.extract_header')
    @patch('routes.resume.DocumentParser.remove_header')
    @patch('routes.resume.AIService.get_provider')
    @patch('routes.resume.LaTeXGenerator.generate_latex')
    @patch('routes.resume.get_session')
    @patch('routes.resume.os.path.exists')
    @patch('routes.resume.os.remove')
    def test_complete_flow_with_low_original_score(
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
        """Test flow where resume has low initial score but improves significantly"""
        mock_extract_text.return_value = "Basic resume with minimal content"
        mock_extract_header.return_value = "[HEADER]\nJohn Doe\n"
        mock_remove_header.return_value = "Basic resume with minimal content"

        mock_provider = MagicMock()
        mock_ai_response = {
            'original_score': {
                'total_score': 45,
                'keyword_match_score': 40,
                'relevance_score': 42,
                'ats_score': 50,
                'quality_score': 48,
                'recommendations': [
                    'Add quantified achievements',
                    'Include more relevant keywords',
                    'Improve formatting for ATS',
                    'Use stronger action verbs'
                ]
            },
            'tailored_resume': '[EXPERIENCE]\nTech Corp | Location\nSenior Engineer | 2020-2023\n- Increased efficiency by 40%',
            'tailored_score': {
                'total_score': 88,
                'keyword_match_score': 90,
                'relevance_score': 85,
                'ats_score': 90,
                'quality_score': 87
            }
        }
        mock_provider.score_and_tailor_resume.return_value = mock_ai_response
        mock_get_provider.return_value = mock_provider

        mock_latex_gen.return_value = ('/outputs/resume.pdf', '/outputs/resume.tex')
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_exists.return_value = True

        request_data = {
            'file_path': 'uploads/weak_resume.pdf',
            'job_description': 'Looking for experienced engineer...',
            'api': 'claude',
            'user_name': 'Test User',
            'company': 'Company',
            'job_title': 'Engineer',
        }

        response = client.post(
            '/api/tailor-resume',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['original_score']['total_score'] == 45
        assert data['tailored_score']['total_score'] == 88

        improvement = data['tailored_score']['total_score'] - data['original_score']['total_score']
        assert improvement == 43

        assert len(data['original_score']['recommendations']) == 4

    @patch('routes.resume.DocumentParser.extract_text')
    @patch('routes.resume.DocumentParser.extract_header')
    @patch('routes.resume.DocumentParser.remove_header')
    @patch('routes.resume.AIService.get_provider')
    @patch('routes.resume.LaTeXGenerator.generate_latex')
    @patch('routes.resume.get_session')
    @patch('routes.resume.os.path.exists')
    @patch('routes.resume.os.remove')
    def test_all_score_categories_present(
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
        """Verify all score categories are returned"""
        mock_extract_text.return_value = "Resume content"
        mock_extract_header.return_value = "[HEADER]\n"
        mock_remove_header.return_value = "Resume content"

        mock_provider = MagicMock()
        mock_ai_response = {
            'original_score': {
                'total_score': 70,
                'keyword_match_score': 65,
                'relevance_score': 72,
                'ats_score': 75,
                'quality_score': 68,
                'recommendations': ['Test rec']
            },
            'tailored_resume': 'Tailored content',
            'tailored_score': {
                'total_score': 85,
                'keyword_match_score': 88,
                'relevance_score': 84,
                'ats_score': 82,
                'quality_score': 86
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
            'job_description': 'Job description',
            'api': 'gemini',
            'user_name': 'User',
            'company': 'Co',
            'job_title': 'Role',
        }

        response = client.post(
            '/api/tailor-resume',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        data = json.loads(response.data)

        required_fields = ['total_score', 'keyword_match_score', 'relevance_score', 'ats_score', 'quality_score']

        for field in required_fields:
            assert field in data['original_score'], f"Missing {field} in original_score"
            assert field in data['tailored_score'], f"Missing {field} in tailored_score"
            assert isinstance(data['original_score'][field], (int, float))
            assert isinstance(data['tailored_score'][field], (int, float))

    @patch('routes.resume.DocumentParser.extract_text')
    @patch('routes.resume.DocumentParser.extract_header')
    @patch('routes.resume.DocumentParser.remove_header')
    @patch('routes.resume.AIService.get_provider')
    def test_error_handling_in_flow(
        self,
        mock_get_provider,
        mock_remove_header,
        mock_extract_header,
        mock_extract_text,
        client
    ):
        """Test error handling at various points in the flow"""
        mock_extract_text.return_value = "Resume"
        mock_extract_header.return_value = "[HEADER]\n"
        mock_remove_header.return_value = "Resume"

        mock_provider = MagicMock()
        mock_provider.score_and_tailor_resume.side_effect = Exception("OpenAI API rate limit exceeded")
        mock_get_provider.return_value = mock_provider

        request_data = {
            'file_path': 'uploads/resume.pdf',
            'job_description': 'Job description',
            'api': 'openai',
            'user_name': 'User',
            'company': 'Co',
            'job_title': 'Role',
        }

        response = client.post(
            '/api/tailor-resume',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data
        assert 'rate limit' in data['error'].lower() or 'openai' in data['error'].lower()
