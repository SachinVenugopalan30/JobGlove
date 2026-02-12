import json
from unittest.mock import Mock, patch

import pytest


@pytest.mark.integration
class TestResumeRoutes:
    """Test resume API routes"""

    def test_check_apis_endpoint(self, client):
        """Test /api/check-apis endpoint"""
        with patch('routes.resume.Config') as mock_config:
            mock_config.check_api_availability.return_value = {
                'openai': True,
                'gemini': False,
                'claude': True
            }

            response = client.get('/api/check-apis')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['openai']
            assert not data['gemini']
            assert data['claude']

    def test_score_endpoint_success(self, client, sample_resume_text, sample_job_description):
        """Test /api/score endpoint with valid data"""
        with patch('routes.resume.create_scoring_service') as mock_create:
            mock_service = Mock()
            mock_service.score_resume.return_value = {
                'ats_score': 18.0,
                'content_score': 19.0,
                'style_score': 23.0,
                'match_score': 24.0,
                'readiness_score': 9.0,
                'total_score': 93.0,
                'ats_feedback': 'Good',
                'content_feedback': 'Strong',
                'style_feedback': 'Professional',
                'match_feedback': 'Excellent',
                'readiness_feedback': 'Ready'
            }
            mock_create.return_value = mock_service

            response = client.post('/api/score', json={
                'resume_text': sample_resume_text,
                'job_description': sample_job_description,
                'api': 'openai'
            })

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['total_score'] == 93.0
            assert data['ats_score'] == 18.0

    def test_score_endpoint_missing_fields(self, client):
        """Test /api/score with missing required fields"""
        response = client.post('/api/score', json={
            'resume_text': 'Some text'
            # Missing job_description and api
        })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_review_endpoint_success(self, client, sample_resume_text, sample_job_description):
        """Test /api/review endpoint with valid data"""
        with patch('routes.resume.create_review_service') as mock_create:
            mock_service = Mock()
            mock_service.review_resume.return_value = [
                {
                    'section': 'Experience',
                    'original_text': 'Developed apps',
                    'strengths': 'Good',
                    'refinement_suggestions': 'Add metrics',
                    'relevance_score': 4
                }
            ]
            mock_create.return_value = mock_service

            response = client.post('/api/review', json={
                'resume_text': sample_resume_text,
                'job_description': sample_job_description,
                'api': 'claude'
            })

            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'bullets' in data
            assert len(data['bullets']) == 1

    def test_review_endpoint_missing_fields(self, client):
        """Test /api/review with missing required fields"""
        response = client.post('/api/review', json={
            'resume_text': 'Some text'
        })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_history_endpoint_empty(self, client):
        """Test /api/resumes/history with no resumes"""
        with patch('routes.resume.get_session') as mock_get_session:
            mock_session = Mock()
            mock_session.query.return_value.order_by.return_value.all.return_value = []
            mock_get_session.return_value = mock_session

            response = client.get('/api/resumes/history')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'resumes' in data
            assert len(data['resumes']) == 0

    def test_history_endpoint_with_resumes(self, client):
        """Test /api/resumes/history returns resumes"""
        with patch('routes.resume.get_session') as mock_get_session:
            mock_resume = Mock()
            mock_resume.to_dict.return_value = {
                'id': 1,
                'user_name': 'John Doe',
                'company': 'Tech Corp',
                'job_title': 'Engineer'
            }
            mock_resume.id = 1

            mock_score = Mock()
            mock_score.total_score = 85.0

            mock_version = Mock()
            mock_version.pdf_path = '/path/to/file.pdf'
            mock_version.tex_path = '/path/to/file.tex'

            mock_session = Mock()
            mock_session.query.return_value.order_by.return_value.all.return_value = [mock_resume]
            mock_session.query.return_value.filter_by.return_value.order_by.return_value.first.side_effect = [
                mock_score, mock_version
            ]
            mock_get_session.return_value = mock_session

            response = client.get('/api/resumes/history')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['resumes']) == 1
            assert data['resumes'][0]['user_name'] == 'John Doe'

    def test_search_endpoint_with_query(self, client):
        """Test /api/resumes/search with search query"""
        with patch('routes.resume.get_session') as mock_get_session:
            mock_resume = Mock()
            mock_resume.to_dict.return_value = {
                'id': 1,
                'user_name': 'John Doe',
                'company': 'Tech Corp',
                'job_title': 'Engineer'
            }
            mock_resume.id = 1

            mock_session = Mock()
            mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_resume]
            mock_session.query.return_value.filter_by.return_value.order_by.return_value.first.return_value = None
            mock_get_session.return_value = mock_session

            response = client.get('/api/resumes/search?q=Tech')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'resumes' in data

    def test_search_endpoint_without_query(self, client):
        """Test /api/resumes/search without query returns all"""
        with patch('routes.resume.get_resume_history') as mock_history:
            mock_history.return_value = ({'resumes': []}, 200)

            response = client.get('/api/resumes/search')

            assert response.status_code == 200

    @patch('routes.resume.score_resume_against_job')
    @patch('routes.resume.extract_text')
    @patch('routes.resume.DocumentParser')
    @patch('routes.resume.AIService')
    @patch('routes.resume.LaTeXGenerator')
    @patch('routes.resume.get_session')
    @patch('routes.resume.os.path.exists')
    @patch('routes.resume.os.remove')
    def test_tailor_resume_endpoint_with_new_fields(
        self, mock_remove, mock_exists, mock_get_session,
        mock_latex, mock_ai, mock_parser, mock_extract_text, mock_score, client
    ):
        """Test /api/tailor-resume with user_name, company, job_title"""
        # Setup mocks
        mock_extract_text.return_value = "John Doe | Senior Software Engineer | Experienced developer with 5+ years in Python, React, and AWS. Built scalable applications."
        mock_parser.extract_header.return_value = "John Doe | john@example.com"
        mock_parser.remove_header.return_value = "Resume without header"

        mock_provider = Mock()
        mock_provider.tailor_resume.return_value = "Tailored resume"
        mock_ai.get_provider.return_value = mock_provider

        mock_latex.generate_latex.return_value = ('/path/to/resume.pdf', '/path/to/resume.tex')

        mock_score.return_value = {
            'total_score': 85,
            'keyword_match_score': 80,
            'keyword_match_details': {'matched': [], 'missing': [], 'match_percentage': 80},
            'relevance_score': 90,
            'ats_score': 85,
            'quality_score': 85,
            'recommendations': []
        }

        mock_session = Mock()
        mock_get_session.return_value = mock_session
        mock_exists.return_value = True

        response = client.post('/api/tailor-resume', json={
            'file_path': '/tmp/test.docx',
            'job_description': 'Job description',
            'api': 'openai',
            'user_name': 'John Doe',
            'company': 'Tech Corp',
            'job_title': 'Software Engineer'
        })

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'pdf_file' in data
        assert 'tex_file' in data
        assert 'tailored_score' in data

        # Verify LaTeX generator was called with user info
        mock_latex.generate_latex.assert_called_once()
        call_args = mock_latex.generate_latex.call_args
        # Check that user_name, company, job_title were passed
        assert 'John Doe' in str(call_args) or call_args[1].get('user_name') == 'John Doe'

    @patch('routes.resume.score_resume_against_job')
    @patch('routes.resume.extract_text')
    @patch('routes.resume.DocumentParser')
    @patch('routes.resume.AIService')
    @patch('routes.resume.LaTeXGenerator')
    @patch('routes.resume.get_session')
    def test_tailor_resume_saves_to_database(
        self, mock_get_session, mock_latex, mock_ai, mock_parser, mock_extract_text, mock_score, client
    ):
        """Test that /api/tailor-resume saves data to database"""
        mock_extract_text.return_value = "Test User | Senior Developer | Experienced in software development with proven track record. Proficient in multiple technologies."
        mock_parser.extract_header.return_value = "Header"
        mock_parser.remove_header.return_value = "Body"

        mock_provider = Mock()
        mock_provider.tailor_resume.return_value = "Tailored"
        mock_ai.get_provider.return_value = mock_provider

        mock_latex.generate_latex.return_value = ('/test.pdf', '/test.tex')

        mock_score.return_value = {
            'total_score': 85,
            'keyword_match_score': 80,
            'keyword_match_details': {'matched': [], 'missing': [], 'match_percentage': 80},
            'relevance_score': 90,
            'ats_score': 85,
            'quality_score': 85,
            'recommendations': []
        }

        mock_session = Mock()
        mock_get_session.return_value = mock_session

        with patch('routes.resume.os.path.exists', return_value=True), \
             patch('routes.resume.os.remove'):

            response = client.post('/api/tailor-resume', json={
                'file_path': '/tmp/test.docx',
                'job_description': 'Job desc',
                'api': 'gemini',
                'user_name': 'Test User',
                'company': 'Test Co',
                'job_title': 'Test Role'
            })

            assert response.status_code == 200

            # Verify database operations were called
            assert mock_session.add.called
            assert mock_session.commit.called
